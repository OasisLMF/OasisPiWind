#!/usr/bin/env python3

"""
Installs a version of the MDK package from a given branch in the OasisLMF
GitHub repository, and does an end-to-end runtime test of an OasisLMF-managed
model repository on GitHub using a small sample dataset. Runtime options
include 'gul' for ground up loss (GUL) only, "fm" for insured loss, or 'ri' for
reinsurance losses. In practice, the test model repository will generally be
PiWind.
"""

from __future__ import (
    absolute_import,
    division,
    print_function,
)

import argparse
import copy
import io
import json
import os
import shutil
import sys

if sys.version_info[0] < 3:
    import subprocess32 as subprocess
    from subprocess32 import (
        CalledProcessError,
        run,
    )
else:
    import subprocess
    from subprocess import (
        CalledProcessError,
        run,
    )


class MdkModelRunException(Exception):
    pass


def get_default_pip_path():
    default_pip_path = ''

    cmd_str = 'which pip'
    try:
        resp = run(cmd_str.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True).stdout
    except CalledProcessError as e:
        return
    else:
        if not resp:
            raise MdkModelRunException('No default pip path found!')
        default_pip_path = resp.decode('utf-8').strip()

    return default_pip_path


def parse_args():
    desc = (
        'Installs a version of the MDK package from a given branch in the '
        'OasisLMF GitHub repository, and does an end-to-end runtime test '
        'of an OasisLMF-managed model repository on GitHub using a small '
        'sample dataset. Runtime options include "gul" for ground up loss '
        '(GUL) only, "fm" for insured loss, or "ri" for reinsurance '
        'losses.'
    )
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-b', '--mdk-repo-branch', default='develop',
                        help='Target branch in the MDK package GitHub repository to build the package from')

    parser.add_argument('-m', '--model-repo-name', default='OasisPiWind',
                        help='Target model GitHub repository name (must be an OasisLMF managed repository)')

    parser.add_argument('-r', '--model-repo-branch', default='main', help='Target branch in the model GitHub repository to clone')

    parser.add_argument('-t', '--clone-target', default=os.path.abspath('.'),
                        help='Local parent folder in which to clone the model repository - default is script run directory')

    parser.add_argument('-g', '--git-transfer-protocol', default='https', help='Git transfer protocol - https" or "ssh"')

    parser.add_argument('-p', '--pip-path', default=get_default_pip_path(), help='pip path')

    parser.add_argument('-d', '--model-run-mode', default='ri', help='Model run mode - `gul` for GUL only, `fm` for GUL + FM, `ri` for GUL + FM + RI')

    parser.add_argument('-n', '--no-cleanup', action='store_true', default=False,
                        help='Whether to cleanup installed MDK installed package and model repository')

    args = vars(parser.parse_args())

    if not os.path.isabs(args['clone_target']):
        args['clone_target'] = os.path.abspath(args['clone_target'])

    args['model_run_mode'] = args['model_run_mode'].lower()
    if args['model_run_mode'] not in ['gul', 'fm', 'ri']:
        args['model_run_mode'] = 'ri'

    return args


def run_command(cmd_str):
    resp = run(cmd_str.split(), stderr=subprocess.STDOUT)
    print('CMD: {}'.format(cmd_str))
    resp.check_returncode()


def pkg_exists(pkg_name):
    try:
        cmd_str = 'pip show {}'.format(pkg_name)
        resp = run_command(cmd_str)
    except CalledProcessError:
        return False


def pip_uninstall(pkg_name, options_str='-y', pip_path=get_default_pip_path()):
    if pkg_exists(pkg_name):
        cmd_str = 'pip uninstall {} {}'.format(options_str, pkg_name)
        run_command(cmd_str)


def pip_install(pkg_name_or_branch_uri, options_str='', pip_path=get_default_pip_path()):
    pkg_name = pkg_name_or_branch_uri.split('=')[-1]

    if pkg_exists(pkg_name):
        pip_uninstall(pkg_name)

    cmd_str = '{} install {} {}  --break-system-packages'.format(pip_path, options_str, pkg_name_or_branch_uri)
    run_command(cmd_str)


def clone_repo(repo_name, target, repo_branch='main', user_or_org_name='OasisLMF', home=os.getcwd(), transfer_protocol='ssh'):
    if not os.path.exists(target):
        os.mkdir(target)

    repo_target = os.path.join(target, repo_name)
    if os.path.exists(repo_target):
        shutil.rmtree(repo_target)

    os.chdir(target)

    if transfer_protocol == 'https':
        repo_url = 'https://github.com/{}/{}'.format(user_or_org_name, repo_name)
    elif transfer_protocol == 'ssh':
        repo_url = 'git+{}://git@github.com/{}/{}'.format(transfer_protocol, user_or_org_name, repo_name)

    run_command('git clone {}'.format(repo_url))
    os.chdir(repo_target)
    if repo_branch[:3] == "PR-" or 'refs/pull' in repo_branch:
        # Fetch Pull Request
        pull_id = int(''.join(d for d in repo_branch if d.isdigit()))
        run_command('git fetch origin pull/{}/head:{}'.format(pull_id, repo_branch))

    # Checkout repo Branch
    run_command('git checkout {}'.format(repo_branch))
    os.chdir(home)


def apply_model_run_mode(model_run_mode, model_mdk_config_fp, as_dict=False):
    with io.open(model_mdk_config_fp, 'r', encoding='utf-8') as f:
        model_mdk_config = json.load(f)

    _model_mdk_config = copy.deepcopy(model_mdk_config)

    if model_run_mode == 'gul':
        for k in model_mdk_config:
            if 'accounts' in k or 'fm' in k or 'ri' in k:
                _model_mdk_config.pop(k)
    elif model_run_mode == 'fm':
        for k in model_mdk_config:
            if 'ri' in k:
                _model_mdk_config.pop(k)

    if as_dict:
        return _model_mdk_config

    # with io.open(model_mdk_config_fp, 'w', encoding='utf-8') as f:
    #    json.dump(_model_mdk_config, f, indent=4, sort_keys=True)


def run_model(model_mdk_config_fp, model_run_dir=os.path.abspath('.')):
    cmd_str = 'oasislmf model run -C {} -r {}'.format(model_mdk_config_fp, model_run_dir)
    run_command(cmd_str)


def print_model_dir_tree(model_run_dir, options_str='-h'):
    cmd_str = 'tree {} {}'.format(options_str, model_run_dir)
    run_command(cmd_str)


def model_run_ok(model_run_dir, model_run_mode):

    def _is_non_empty_file(fp, substr_match=False, is_dir=False):
        print(fp)
        if not substr_match:
            print((os.path.isfile(fp) if not is_dir else os.path.isdir(fp)) and os.path.getsize(fp) > 0)
            return (os.path.isfile(fp) if not is_dir else os.path.isdir(fp)) and os.path.getsize(fp) > 0
        else:
            substr, dir_name, dir_contents = os.path.basename(fp), os.path.dirname(fp), os.listdir(os.path.dirname(fp))
            try:
                fn = [fn for fn in dir_contents if substr in fn][0]
            except (AttributeError, IndexError):
                print('False')
                return False
            _fp = os.path.join(dir_name, fn)
            print(os.path.getsize(_fp) > 0)
            return os.path.getsize(_fp) > 0

    ri = model_run_mode == 'ri'
    output_files = [
        'S1_ept.csv',
        'S1_melt.csv',
        'S1_mplt.csv',
        'S1_palt.csv',
        'S1_psept.csv',
        'S1_qelt.csv',
        'S1_qplt.csv',
        'S1_selt.csv',
        'S1_splt.csv',
        'S1_summary-info.csv',
    ]

    assert (_is_non_empty_file(model_run_dir, is_dir=True))
    assert (_is_non_empty_file(os.path.join(model_run_dir, 'input', 'analysis_settings.json'))) # user settings
    assert (_is_non_empty_file(os.path.join(model_run_dir, 'output', 'analysis_settings.json'))) # Merged settings
    assert (_is_non_empty_file(os.path.join(model_run_dir, 'input'), is_dir=True))
    assert (_is_non_empty_file(os.path.join(model_run_dir, 'output'), is_dir=True))
    assert (_is_non_empty_file(os.path.join(model_run_dir, 'static'), is_dir=True))
    assert (_is_non_empty_file(os.path.join(model_run_dir, 'run_kernel.sh')))

    direct_csv_inputs_fp = os.path.join(model_run_dir, 'input', 'csv') if not ri else os.path.join(model_run_dir, 'input')

    assert (_is_non_empty_file(os.path.join(direct_csv_inputs_fp, 'location'), substr_match=True))
    assert (_is_non_empty_file(os.path.join(direct_csv_inputs_fp, 'keys'), substr_match=True))
    assert (_is_non_empty_file(os.path.join(direct_csv_inputs_fp, 'keys-errors'), substr_match=True))

    assert (_is_non_empty_file(os.path.join(direct_csv_inputs_fp, 'items.csv')))
    assert (_is_non_empty_file(os.path.join(direct_csv_inputs_fp, 'coverages.csv')))
    assert (_is_non_empty_file(os.path.join(direct_csv_inputs_fp, 'gulsummaryxref.csv')))
    assert (_is_non_empty_file(os.path.join(direct_csv_inputs_fp, 'gul_summary_map.csv')))

    bin_inputs_fp = os.path.join(model_run_dir, 'input')
    assert (_is_non_empty_file(os.path.join(bin_inputs_fp, 'occurrence.bin')))
    assert (_is_non_empty_file(os.path.join(bin_inputs_fp, 'events.bin')))
    assert (_is_non_empty_file(os.path.join(bin_inputs_fp, 'items.bin')))
    assert (_is_non_empty_file(os.path.join(bin_inputs_fp, 'coverages.bin')))
    assert (_is_non_empty_file(os.path.join(bin_inputs_fp, 'gulsummaryxref.bin')))

    outputs_fp = os.path.join(model_run_dir, 'output')
    assert (_is_non_empty_file(os.path.join(outputs_fp, 'analysis_settings.json')))
    for ord_file in output_files:
        assert (_is_non_empty_file(os.path.join(outputs_fp, f"gul_{ord_file}")))

    if model_run_mode in ['fm', 'ri']:
        assert (_is_non_empty_file(os.path.join(direct_csv_inputs_fp, 'account'), substr_match=True))
        assert (_is_non_empty_file(os.path.join(direct_csv_inputs_fp, 'fm_programme.csv')))
        assert (_is_non_empty_file(os.path.join(direct_csv_inputs_fp, 'fm_profile.csv')))
        assert (_is_non_empty_file(os.path.join(direct_csv_inputs_fp, 'fm_policytc.csv')))
        assert (_is_non_empty_file(os.path.join(direct_csv_inputs_fp, 'fm_xref.csv')))
        assert (_is_non_empty_file(os.path.join(direct_csv_inputs_fp, 'fmsummaryxref.csv')))
        assert (_is_non_empty_file(os.path.join(direct_csv_inputs_fp, 'fm_summary_map.csv')))

        assert (_is_non_empty_file(os.path.join(bin_inputs_fp, 'fm_programme.bin')))
        assert (_is_non_empty_file(os.path.join(bin_inputs_fp, 'fm_profile.bin')))
        assert (_is_non_empty_file(os.path.join(bin_inputs_fp, 'fm_policytc.bin')))
        assert (_is_non_empty_file(os.path.join(bin_inputs_fp, 'fm_xref.bin')))
        assert (_is_non_empty_file(os.path.join(bin_inputs_fp, 'fmsummaryxref.bin')))

        for ord_file in output_files:
            assert (_is_non_empty_file(os.path.join(outputs_fp, f"il_{ord_file}")))

        if model_run_mode == 'ri':
            assert (_is_non_empty_file(os.path.join(bin_inputs_fp, 'ri_layers'), substr_match=True))
            assert (_is_non_empty_file(os.path.join(bin_inputs_fp, 'RI'), substr_match=True))
            for ord_file in output_files:
                assert (_is_non_empty_file(os.path.join(outputs_fp, f"ri_{ord_file}")))

    return True


def cleanup(pip_path=get_default_pip_path(), mdk_pkg_name='oasislmf', model_run_dir=None):
    pip_uninstall(mdk_pkg_name, options_str='-v -y', pip_path=pip_path)
    if model_run_dir:
        shutil.rmtree(model_run_dir)


if __name__ == "__main__":

    args = parse_args()

    print('\nProcessing script arguments: {}'.format(json.dumps(args, indent=4, sort_keys=True)))

    if not args['pip_path']:
        raise MdkModelRunException('pip path could not be determined and/or no pip path provided when calling the script')

    if args['git_transfer_protocol'] not in ['https', 'ssh']:
        args['git_transfer_protocol'] = 'ssh'

    pkg_uri = 'oasislmf[extra]@git+{}://git@github.com/OasisLMF/OasisLMF.git@{}'.format(args['git_transfer_protocol'], args['mdk_repo_branch'])

    print('\nInstalling MDK package {}'.format(pkg_uri))

    try:
        pip_install(pkg_uri, pip_path=args['pip_path'])
    except CalledProcessError as e:
        raise MdkModelRunException('\nError trying to pip install package: {}'.format(e))

    print('\nMDK package successfully installed from branch {}'.format(args['mdk_repo_branch']))

    print('\nCloning model repository {} (branch {}) in {}\n'.format(args['model_repo_name'], args['model_repo_branch'], args['clone_target']))

    try:
        clone_repo(args['model_repo_name'], args['clone_target'], repo_branch=args['model_repo_branch'],
                   transfer_protocol=args['git_transfer_protocol'])
    except CalledProcessError as e:
        raise MdkModelRunException('\nError while trying to clone {} repository: {}\n'.format(args['model_repo_name'], e))

    print('\n{} successfully cloned in {}'.format(args['model_repo_name'], args['clone_target']))

    local_model_repo_fp = os.path.join(args['clone_target'], args['model_repo_name'])
    model_mdk_config_fp = os.path.join(local_model_repo_fp, 'oasislmf.json')

    print('\nAdjusting {} MDK config. file to suit model run mode "{}"'.format(args['model_repo_name'], args['model_run_mode'].upper()))
    apply_model_run_mode(args['model_run_mode'], model_mdk_config_fp)

    model_run_dir = os.path.join(local_model_repo_fp, 'test-run')
    print(
        '\nRunning {} end-to-end via MDK using config. file {} - model run dir. is {}\n'.format(args['model_repo_name'], model_mdk_config_fp, model_run_dir))

    try:
        run_model(model_mdk_config_fp, model_run_dir=model_run_dir)
    except CalledProcessError as e:
        raise MdkModelRunException('\nError while trying to run {} via MDK: {}'.format(args['model_repo_name'], e))

    print('\nModel run OK')

    print('\nModel run directory has the following structure\n')
    try:
        print_model_dir_tree(model_run_dir)
    except CalledProcessError as e:
        print('\nError getting or printing model run directory tree - skipping step')

    print('\nChecking correctess of model run directory')
    try:
        model_run_ok(model_run_dir, args['model_run_mode'])
    except AssertionError:
        print('\nModel run error - missing, incorrect or incomplete files in model run dir. {}'.format(model_run_dir))
        sys.exit(1)

    print('\nModel run directory has the expected structure')

    print('\nModel run completed successfully')

    if not args['no_cleanup']:
        print('\nCleaning up - removing MDK package install and test model repository {}'.format(args['model_repo_name']))
        try:
            cleanup(pip_path=args['pip_path'], model_run_dir=local_model_repo_fp)
        except CalledProcessError as e:
            print('\nError cleaning up: {}'.format(e))

    sys.exit(0)
