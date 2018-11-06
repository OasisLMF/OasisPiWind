<img src="https://oasislmf.org/packages/oasis_theme_package/themes/oasis_theme/assets/src/oasis-lmf-colour.png" alt="Oasis LMF logo" width="250"/>

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/OasisLMF/OasisPiWind/master) [![Build](http://ci.oasislmfdev.org/buildStatus/icon?job=oasis_PiWind)](http://ci.oasislmfdev.org/blue/organizations/jenkins/oasis_PiWind)

# Oasis PiWind
Toy UK windstorm model that provides an example Oasis implementation, providing a concrete implementation of an Oasis model respository built using the <a href="https://github.com/OasisLMF/cookiecutter-OasisModel">Oasis cookiecutter</a> utility.

## Cloning the repository

You can clone this repository from <a href="https://github.com/OasisLMF/OasisPiWind" target="_blank">GitHub</a>. Before doing this you must generate an SSH key pair on your local machine and add the public key of that pair to your GitHub account (use the GitHub guide at <a href="https://help.github.com/articles/connecting-to-github-with-ssh/" target="_blank">https://help.github.com/articles/connecting-to-github-with-ssh/</a>).

    git clone git+{https,ssh}://git@github.com/OasisLMF/OasisPiWind

## Building and running the keys server

Please ensure that you have Docker installed on your system and that Docker has the proper access privileges.

The PiWind lookup is a built-in lookup provided by the <a href="https://pypi.org/project/oasislmf/" target="_blank">`oasislmf`</a> Python package, and the PiWind keys server is based on a Flask application for built-in lookups and which is part of the `oasis_keys_server` submodule. The Flask source code is built in to a base image named `coreoasis/builtin_keys_server`, which is available from <a href="https://hub.docker.com/r/coreoasis/builtin_keys_server/" target="_blank">Docker Hub</a>. Please ensure you've been given read access to this repository so that the base image can be sourced during the build.

You can build the PiWind keys server (from the base of your PiWind repository) by running

    docker build -f docker/Dockerfile.oasislmf_piwind_keys_server -t <image name/tag> .

Run `docker images` to list all images and check the one you've built exists. To run the image in a container you can use the command

    docker run -dp 5000:80 --name=<container name/tag> <image name/tag>

This will run the container on the local host on port 5000.

To check the container is running use the command `docker ps`. If you want to run the healthcheck on the keys server then use the command

    curl http://localhost:5000/OasisLMF/PiWind/0.0.0.1/healthcheck

You should get a response of `OK` if the keys server has initialised and is running normally, otherwise you should get the HTML error response from Apache. To enter the running container you can use the command

    docker exec -it <container name> bash

The log files to check are `/var/log/apache/error.log` (Apache error log), `/var/log/apache/access.log` (Apache request log), and `/var/log/oasis/keys_server.log` (the keys server Python log). In case of request timeout issues you can edit the `Timeout` option value (in seconds) in the file `/etc/apache2/sites-available/oasis.conf` and restart Apache (`service apache2 restart`).

## Testing the keys server

You can test a running keys server by making a manual keys request (using `curl` or `wget`) - you need to pass in a UTF-8 encoded model locatons/exposures CSV file in the request.

    curl -v http://localhost:5000/OasisLMF/PiWind/0.0.0.1/get_keys --data-binary @</path/to/model/exposure/file> -H 'Content-type:text/csv; charset=utf-8' --compressed

## Running via the Oasis MDK

The <a href="https://pypi.org/project/oasislmf/" target="_blank">Oasis model development kit (MDK)</a> is a Python package which provides a command line interface (CLI) for developing and running models using the Oasis framework. It can be installed via the Python package installer `pip` (or `pip3` for Python 3). The PiWind repository contains a <a href="https://github.com/OasisLMF/OasisPiWind/blob/develop/keys_data/PiWind/lookup.json" target="_blank">JSON configuration file</a> that allows the PiWind model to be run via the MDK.

    {
        "source_exposures_file_path": "tests/data/SourceLocPiWind10.csv",
        "source_exposures_validation_file_path": "flamingo/PiWind/Files/ValidationFiles/Generic_Windstorm_SourceLoc.xsd",
        "source_to_canonical_exposures_transformation_file_path": "flamingo/PiWind/Files/TransformationFiles/MappingMapToGeneric_Windstorm_CanLoc_A.xslt",
        "canonical_exposures_profile_json_path": "canonical-loc-profile.json",
        "canonical_exposures_validation_file_path": "flamingo/PiWind/Files/ValidationFiles/Generic_Windstorm_CanLoc_B.xsd",
        "canonical_to_model_exposures_transformation_file_path": "flamingo/PiWind/Files/TransformationFiles/MappingMapTopiwind_modelloc.xslt",
        "source_accounts_file_path": "tests/data/SourceAccPiWind.csv",
        "canonical_accounts_profile_json_path": "canonical-acc-profile.json",
        "source_accounts_validation_file_path": "flamingo/PiWind/Files/ValidationFiles/Generic_CanAcc_A.xsd",
        "source_to_canonical_accounts_transformation_file_path": "flamingo/PiWind/Files/TransformationFiles/MappingMapToGeneric_CanAcc_A.xslt",
        "model_data_path": "model_data/PiWind",
        "analysis_settings_json_file_path": "analysis_settings.json",
        "lookup_config_file_path": "keys_data/PiWind/lookup.json",
        "fm_agg_profile_path": "fm-agg-profile.json"
    }


**NOTE**: All paths in this JSON file should be given relative to the location of the file.

Using the configuration file an end-to-end analysis can be executed using the command:

	oasislmf model run -C /path/to/oasislmf.json [-r OUTPUT_DIRECTORY] [--fm]

If you specified an output directory the package will generate all the files there. Otherwise the files will be generated in a UTC timestamped folder named `ProgOasis-<UTC timestamp`> in your working directory.

This can also be done by providing all the arguments via the command line - use the `oasislmf model run --help` command to view the required argument flags. Particular steps in the analysis can be also be executed independently using either command line arguments or a JSON configuration file (via the `-C` flag):

    oasislmf model generate-peril-areas-rtree-file-index  # Generate an Rtree spatial file index from a source peril areas CSV file

    oasislmf model transform-source-to-canonical          # Generate a canonical exposures/accounts file from a source exposures/accounts file

    oasislmf model transform-canonical-to-model           # Generate a model exposures file from a canonical exposures file

    oasislmf model generate-keys                          # Generate Oasis keys and keys error files

    oasislmf model generate-oasis-files                   # Generate Oasis files (GUL only by defaut; for FM add the `--fm` flag)

    oasislmf model generate-losses                        # Generate losses from an existing set of Oasis files and analysis settings JSON

Use the `--help` flag to show the command line flags and JSON key names for the arguments.
