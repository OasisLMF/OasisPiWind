#!/usr/bin/env python3
"""
benchmark_commits.py - Benchmark oasislmf execution time across multiple git commits/branches.

For each commit, builds a PiWind worker Docker image with that oasislmf version installed
and runs the integration tests, measuring total execution time.

Usage:
    # Test specific commits or branches
    python benchmark_commits.py abc1234 def5678 main develop

    # Read commits from a file (one per line, # for comments)
    python benchmark_commits.py --file commits.txt

    # Use the v2 platform compose file and run only a subset of tests
    python benchmark_commits.py abc1234 --compose docker/plat2-v2.docker-compose.yml \\
        --api-version v2 --pytest-args "-k case_0"

    # Keep docker images after run (for debugging), verbose output
    python benchmark_commits.py abc1234 --cleanup --verbose
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).parent.resolve()
DOCKERFILE_WORKER = REPO_ROOT / "docker" / "Dockerfile.piwind_worker"
DEFAULT_COMPOSE = str(REPO_ROOT / "docker-compose.yml")
DEFAULT_WORKER_IMG = "coreoasis/model_worker"
DEFAULT_WORKER_TAG = "latest"
DEFAULT_SERVER_IMG = "coreoasis/api_server"
DEFAULT_SERVER_TAG = "latest"


@dataclass
class CommitResult:
    commit: str
    tag: str
    worker_img: str = ""   # actual image name used when running tests
    worker_tag: str = ""   # actual image tag used when running tests
    built: bool = False    # True only if we built the image ourselves (controls cleanup)
    build_duration: float = 0.0
    test_duration: float = 0.0
    total_duration: float = 0.0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    status: str = "pending"  # pending | build_failed | test_failed | passed
    pytest_durations: dict = field(default_factory=dict)
    error_message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ---------------------------------------------------------------------------
# Shell helpers
# ---------------------------------------------------------------------------

def run_command(
    cmd: list[str],
    env: Optional[dict] = None,
    cwd: Optional[Path] = None,
    timeout: Optional[int] = None,
) -> tuple[int, str, str, float]:
    """Run a command, capturing stdout/stderr. Returns (rc, stdout, stderr, duration)."""
    start = time.monotonic()
    merged_env = {**os.environ, **(env or {})}
    result = subprocess.run(
        cmd,
        env=merged_env,
        cwd=str(cwd or REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr, time.monotonic() - start


def stream_command(
    cmd: list[str],
    env: Optional[dict] = None,
    cwd: Optional[Path] = None,
    prefix: str = "",
    timeout: Optional[int] = None,
) -> tuple[int, str, float]:
    """Run a command, streaming output to stdout. Returns (rc, combined_output, duration)."""
    start = time.monotonic()
    merged_env = {**os.environ, **(env or {})}
    lines: list[str] = []

    process = subprocess.Popen(
        cmd,
        env=merged_env,
        cwd=str(cwd or REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    assert process.stdout is not None
    for line in process.stdout:
        line = line.rstrip("\n")
        lines.append(line)
        print(f"{prefix}{line}" if prefix else line, flush=True)

    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    return process.returncode, "\n".join(lines), time.monotonic() - start


# ---------------------------------------------------------------------------
# Docker helpers
# ---------------------------------------------------------------------------

def make_image_tag(commit: str) -> str:
    """Create a docker-safe image tag from a commit hash or branch name."""
    tag = re.sub(r"[^a-zA-Z0-9._-]", "-", commit)
    return f"bench-{tag[:50]}"


def build_worker_image(
    commit: str,
    bench_img: str,
    image_tag: str,
    base_worker_img: str,
    base_worker_tag: str,
    no_cache: bool = False,
    verbose: bool = False,
) -> tuple[bool, float, str]:
    """
    Build the PiWind worker image with the specified oasislmf commit/branch installed.

    Rewrites the FROM line to use the specified base worker image, then passes
    `oasislmf_branch` as a build-arg (matching the pattern used in CI).

    Returns (success, duration_seconds, error_output_tail)
    """
    original = DOCKERFILE_WORKER.read_text()
    # Replace the FROM line so we can target a specific base worker image/tag
    modified = re.sub(
        r"^FROM\s+\S+",
        f"FROM {base_worker_img}:{base_worker_tag}",
        original,
        count=1,
        flags=re.MULTILINE,
    )

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".Dockerfile",
        dir=REPO_ROOT,
        delete=False,
        prefix="_bench_",
    ) as tf:
        tf.write(modified)
        tmp_dockerfile = tf.name

    try:
        cmd = [
            "docker", "build",
            "-f", tmp_dockerfile,
            "--build-arg", f"oasislmf_branch={commit}",
            "-t", f"{bench_img}:{image_tag}",
        ]
        if no_cache:
            cmd.append("--no-cache")
        cmd.append(".")

        if verbose:
            rc, output, duration = stream_command(cmd, prefix="  [build] ")
        else:
            rc, stdout, stderr, duration = run_command(cmd)
            output = stdout + stderr

        if rc != 0:
            return False, duration, output
        return True, duration, ""

    finally:
        os.unlink(tmp_dockerfile)


def image_exists(image_name: str, image_tag: str) -> bool:
    """Return True if the Docker image is present in the local image store."""
    rc, _, _, _ = run_command(
        ["docker", "image", "inspect", f"{image_name}:{image_tag}"]
    )
    return rc == 0


def is_semver(ref: str) -> bool:
    """Return True if ref looks like a semver tag (e.g. 2.5.0 or v2.5.0)."""
    return bool(re.match(r"^v?\d+\.\d+\.\d+", ref))


def dockerhub_tag_exists(image: str, tag: str) -> bool:
    """
    Return True if image:tag exists as a public image on Docker Hub,
    without pulling it. Uses `docker manifest inspect` which queries the
    registry API directly.

    DOCKER_CLI_EXPERIMENTAL is set for compatibility with Docker < 20.10.
    """
    rc, _, _, _ = run_command(
        ["docker", "manifest", "inspect", f"{image}:{tag}"],
        env={"DOCKER_CLI_EXPERIMENTAL": "enabled"},
    )
    return rc == 0


def cleanup_images(results: list[CommitResult], bench_img: str) -> None:
    """Remove Docker images that were built during this benchmark run."""
    for r in results:
        if not r.built:
            continue
        full_tag = f"{r.worker_img}:{r.worker_tag}"
        subprocess.run(
            ["docker", "rmi", full_tag, "--force"],
            capture_output=True,
        )
        print(f"  Removed: {full_tag}")


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_tests(
    bench_img: str,
    image_tag: str,
    compose_file: str,
    api_version: str,
    server_img: str,
    server_tag: str,
    extra_pytest_args: list[str],
    verbose: bool = False,
    test_timeout: Optional[int] = None,
) -> tuple[bool, float, int, int, int, int, dict, str]:
    """
    Run the integration test suite against the specified worker image.

    Returns:
        (success, duration, passed, failed, errors, skipped, per_test_durations, raw_output)
    """
    env = {
        "WORKER_IMG": bench_img,
        "WORKER_TAG": image_tag,
        "SERVER_IMG": server_img,
        "SERVER_TAG": server_tag,
        "WORKER_API_VER": api_version,
    }

    cmd = [
        "pytest",
        f"--docker-compose={compose_file}",
        "--docker-compose-remove-volumes",
        "--durations=0",  # show all test durations
        "-v",
        "tests/test_piwind_integration.py",
        *extra_pytest_args,
    ]

    if verbose:
        rc, output, duration = stream_command(cmd, env=env, prefix="  [pytest] ", timeout=test_timeout)
    else:
        rc, stdout, stderr, duration = run_command(cmd, env=env, timeout=test_timeout)
        output = stdout + stderr

    passed, failed, errors_, skipped, durations = _parse_pytest_output(output)
    return rc == 0, duration, passed, failed, errors_, skipped, durations, output


def _parse_pytest_output(output: str) -> tuple[int, int, int, int, dict]:
    """
    Parse pytest stdout/stderr to extract counts and per-test timings.

    Returns (passed, failed, errors, skipped, durations_dict)
    where durations_dict maps "test_id[phase]" -> seconds.
    """
    passed = failed = errors = skipped = 0

    # Final summary line: "5 passed, 2 failed in 42.3s"
    summary = re.search(r"=+\s*([\w ,]+)\s+in\s+[\d.]+s\s*=+\s*$", output, re.MULTILINE)
    if summary:
        text = summary.group(1)
        for pattern, key in [
            (r"(\d+) passed", "passed"),
            (r"(\d+) failed", "failed"),
            (r"(\d+) error", "errors"),
            (r"(\d+) skipped", "skipped"),
        ]:
            m = re.search(pattern, text)
            if m:
                val = int(m.group(1))
                if key == "passed":
                    passed = val
                elif key == "failed":
                    failed = val
                elif key == "errors":
                    errors = val
                elif key == "skipped":
                    skipped = val

    # Duration lines from --durations=0:
    # "  0.12s call     tests/test_piwind_integration.py::case_0::test_output_file[...]"
    # "  1.23s setup    tests/..."
    durations: dict[str, float] = {}
    for m in re.finditer(r"^\s*([\d.]+)s\s+(\w+)\s+(tests/\S+)", output, re.MULTILINE):
        secs = float(m.group(1))
        phase = m.group(2)
        test_id = m.group(3)
        durations[f"{test_id}[{phase}]"] = secs

    return passed, failed, errors, skipped, durations


# ---------------------------------------------------------------------------
# Output / reporting
# ---------------------------------------------------------------------------

def _sep(char: str = "─", width: int = 80) -> None:
    print(char * width)


def print_results_table(results: list[CommitResult]) -> None:
    """Print a formatted summary table to stdout."""
    if not results:
        return

    commit_w = max(20, max(len(r.commit) for r in results) + 2)

    print("\n")
    _sep("═")
    print("  BENCHMARK RESULTS SUMMARY")
    _sep("═")

    header = (
        f"{'Commit':<{commit_w}}"
        f"{'Status':<14}"
        f"{'Build(s)':>10}"
        f"{'Test(s)':>10}"
        f"{'Total(s)':>10}"
        f"{'Passed':>8}"
        f"{'Failed':>8}"
    )
    print(header)
    _sep()

    status_label = {
        "passed": "PASS",
        "test_failed": "FAIL",
        "build_failed": "BUILD ERR",
        "pending": "PENDING",
    }

    for r in results:
        label = status_label.get(r.status, r.status.upper())
        print(
            f"{r.commit:<{commit_w}}"
            f"{label:<14}"
            f"{r.build_duration:>10.1f}"
            f"{r.test_duration:>10.1f}"
            f"{r.total_duration:>10.1f}"
            f"{r.passed:>8}"
            f"{r.failed:>8}"
        )

    _sep("═")

    completed = [r for r in results if r.status in ("passed", "test_failed")]
    if len(completed) > 1:
        fastest = min(completed, key=lambda r: r.test_duration)
        slowest = max(completed, key=lambda r: r.test_duration)
        delta = slowest.test_duration - fastest.test_duration
        pct = (delta / fastest.test_duration * 100) if fastest.test_duration > 0 else 0.0
        print(f"\n  Fastest: {fastest.commit} ({fastest.test_duration:.1f}s)")
        print(f"  Slowest: {slowest.commit} ({slowest.test_duration:.1f}s)")
        print(f"  Delta:   +{delta:.1f}s  ({pct:.1f}% slower)")

    # Per-test timing breakdown (slowest setups, i.e. generate+analyze phases)
    all_durations: dict[str, list[tuple[str, float]]] = {}
    for r in completed:
        for key, secs in r.pytest_durations.items():
            # Strip the commit-specific prefix and group by test id
            all_durations.setdefault(key, []).append((r.commit, secs))

    setup_entries = [
        (k, v) for k, v in all_durations.items() if "[setup]" in k
    ]
    if setup_entries and len(completed) > 1:
        print("\n  Per-test setup times (generate + analyze, seconds):")
        _sep("-", 60)
        # Find the widest test name
        name_w = max(len(k) for k, _ in setup_entries)
        name_w = min(name_w, 60)
        commit_header = "  ".join(f"{r.commit[:12]:>13}" for r in completed)
        print(f"  {'Test':<{name_w}}  {commit_header}")
        _sep("-", 60)
        for test_key, timings_list in sorted(setup_entries):
            timing_by_commit = dict(timings_list)
            values = "  ".join(
                f"{timing_by_commit.get(r.commit, 0.0):>13.1f}"
                for r in completed
            )
            short_name = test_key[:name_w]
            print(f"  {short_name:<{name_w}}  {values}")


def save_results(results: list[CommitResult], output_path: Path) -> None:
    """Save benchmark results as a JSON file."""
    data = {
        "benchmark_run": datetime.utcnow().isoformat() + "Z",
        "results": [asdict(r) for r in results],
    }
    output_path.write_text(json.dumps(data, indent=2))
    print(f"\n  Results saved to: {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark oasislmf execution time across git commits/branches",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # --- Commits input ---
    parser.add_argument(
        "commits",
        nargs="*",
        metavar="COMMIT",
        help="oasislmf git commit hashes, branches, or tags to benchmark",
    )
    parser.add_argument(
        "--file", "-f",
        type=Path,
        metavar="FILE",
        help="File with one commit/branch per line (lines starting with # are ignored)",
    )

    # --- Docker / image options ---
    parser.add_argument(
        "--worker-img",
        default=DEFAULT_WORKER_IMG,
        metavar="IMAGE",
        help=f"Base worker image (default: {DEFAULT_WORKER_IMG})",
    )
    parser.add_argument(
        "--worker-tag",
        default=DEFAULT_WORKER_TAG,
        metavar="TAG",
        help=f"Base worker tag (default: {DEFAULT_WORKER_TAG})",
    )
    parser.add_argument(
        "--server-img",
        default=DEFAULT_SERVER_IMG,
        metavar="IMAGE",
        help=f"API server image (default: {DEFAULT_SERVER_IMG})",
    )
    parser.add_argument(
        "--server-tag",
        default=DEFAULT_SERVER_TAG,
        metavar="TAG",
        help=f"API server tag (default: {DEFAULT_SERVER_TAG})",
    )
    parser.add_argument(
        "--bench-img",
        default="piwind-bench",
        metavar="NAME",
        help="Docker image name for built benchmark images (default: piwind-bench)",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable Docker layer cache when building worker images",
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Always rebuild Docker images even if a matching tag already exists locally",
    )

    # --- Test / compose options ---
    parser.add_argument(
        "--compose",
        default=DEFAULT_COMPOSE,
        metavar="FILE",
        help=f"Docker Compose file to use (default: {DEFAULT_COMPOSE})",
    )
    parser.add_argument(
        "--api-version",
        default="v2",
        choices=["v1", "v2"],
        help="WORKER_API_VER for the compose stack (default: v2)",
    )
    parser.add_argument(
        "--pytest-args",
        default="",
        metavar="ARGS",
        help='Extra pytest arguments, e.g. \'--pytest-args "-k case_0 case_1"\'',
    )
    parser.add_argument(
        "--test-timeout",
        type=int,
        default=None,
        metavar="SECONDS",
        help="Timeout in seconds for each test run (default: no limit)",
    )

    # --- Output options ---
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("benchmark_results.json"),
        metavar="FILE",
        help="Path for the JSON results file (default: benchmark_results.json)",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Keep built Docker images after the run (useful for debugging)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Stream all Docker/pytest output to stdout in real time",
    )

    args = parser.parse_args()

    # --- Collect commits ---
    commits: list[str] = list(args.commits)
    if args.file:
        if not args.file.exists():
            print(f"Error: --file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        for line in args.file.read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                commits.append(line)

    if not commits:
        parser.error("Provide at least one commit as a positional argument or via --file")

    # Deduplicate, preserving order
    seen: set[str] = set()
    commits = [c for c in commits if not (c in seen or seen.add(c))]  # type: ignore[func-returns-value]

    extra_pytest_args = args.pytest_args.split() if args.pytest_args else []

    # --- Header ---
    _sep("═")
    print(f"  PiWind oasislmf Benchmark")
    print(f"  Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Commits : {', '.join(commits)}")
    print(f"  Compose : {args.compose}")
    print(f"  API ver : {args.api_version}")
    print(f"  Base img: {args.worker_img}:{args.worker_tag}")
    _sep("═")

    results: list[CommitResult] = []

    for idx, commit in enumerate(commits, 1):
        print(f"\n[{idx}/{len(commits)}] {commit}")
        _sep("-", 60)

        tag = make_image_tag(commit)
        result = CommitResult(commit=commit, tag=tag)
        t_start = time.monotonic()

        # --- Resolve which image to use ---
        # If the ref looks like a semver (e.g. 2.5.0) check whether the
        # official coreoasis/model_worker image for that version exists on
        # Docker Hub. If it does, use it directly and skip the build entirely.
        use_img = args.bench_img
        use_tag = tag
        built = False

        if not args.force_rebuild and is_semver(commit):
            semver_tag = commit.lstrip("v")
            official_img = DEFAULT_WORKER_IMG
            print(f"  Semver detected — checking {official_img}:{semver_tag} on Docker Hub ...")
            if dockerhub_tag_exists(official_img, semver_tag):
                print(f"  Found official image, skipping build")
                use_img = official_img
                use_tag = semver_tag

        # --- Docker build (only when not using an official image) ---
        if use_img == args.bench_img:
            already_exists = image_exists(args.bench_img, tag)
            if already_exists and not args.force_rebuild:
                print(f"  Build: SKIPPED (image {args.bench_img}:{tag} already exists, use --force-rebuild to rebuild)")
            else:
                if already_exists:
                    print(f"  Building {args.bench_img}:{tag} (--force-rebuild) ...")
                else:
                    print(f"  Building {args.bench_img}:{tag} ...")
                ok, build_dur, err = build_worker_image(
                    commit=commit,
                    bench_img=args.bench_img,
                    image_tag=tag,
                    base_worker_img=args.worker_img,
                    base_worker_tag=args.worker_tag,
                    no_cache=args.no_cache,
                    verbose=args.verbose,
                )
                result.build_duration = build_dur
                print(f"  Build {'OK' if ok else 'FAILED'} ({build_dur:.1f}s)")

                if not ok:
                    result.status = "build_failed"
                    result.error_message = err
                    result.total_duration = time.monotonic() - t_start
                    results.append(result)
                    if err and not args.verbose:
                        print(f"  Last build output:\n{err}")
                    continue

                built = True

        result.worker_img = use_img
        result.worker_tag = use_tag
        result.built = built

        # --- Run tests ---
        print(f"  Running tests ...")
        (
            test_ok,
            test_dur,
            passed,
            failed,
            errors_,
            skipped,
            durations,
            test_output,
        ) = run_tests(
            bench_img=use_img,
            image_tag=use_tag,
            compose_file=args.compose,
            api_version=args.api_version,
            server_img=args.server_img,
            server_tag=args.server_tag,
            extra_pytest_args=extra_pytest_args,
            verbose=args.verbose,
            test_timeout=args.test_timeout,
        )

        result.test_duration = test_dur
        result.total_duration = time.monotonic() - t_start
        result.passed = passed
        result.failed = failed
        result.errors = errors_
        result.skipped = skipped
        result.pytest_durations = durations
        result.status = "passed" if test_ok else "test_failed"

        print(
            f"  Tests {'PASSED' if test_ok else 'FAILED'} ({test_dur:.1f}s)"
            f"  [passed={passed} failed={failed} errors={errors_} skipped={skipped}]"
        )

        if not test_ok and not args.verbose:
            # Show tail of output when tests fail and we weren't streaming
            tail_lines = test_output.splitlines()[-40:]
            print(f"\n  Last pytest output:")
            _sep("-", 60)
            for line in tail_lines:
                print(f"  {line}")
            _sep("-", 60)

        results.append(result)

    # --- Summary table ---
    print_results_table(results)

    # --- Persist results ---
    save_results(results, args.output)

    # --- Cleanup ---
    if args.cleanup:
        built_count = sum(1 for r in results if r.built)
        if built_count:
            print(f"\n  Cleaning up {built_count} built Docker image(s) ...")
            cleanup_images(results, args.bench_img)
        else:
            print("\n  Cleanup: nothing to remove (no images were built)")

    any_non_passing = any(r.status != "passed" for r in results)
    sys.exit(1 if any_non_passing else 0)


if __name__ == "__main__":
    main()
