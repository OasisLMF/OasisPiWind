.. image:: https://oasislmf.org/packages/oasis_theme_package/themes/oasis_theme/assets/src/oasis-lmf-colour.png
    :title: Oasis LMF logo
    :width: 250

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/OasisLMF/OasisPiWind/master)

# Oasis PiWind
Toy UK windstorm model that provides an example Oasis implementation, providing a concrete implementation of an Oasis model respository built using the <a href="https://github.com/OasisLMF/cookiecutter-OasisModel">Oasis cookiecutter</a> utility.

## Cloning the repository

You can clone this repository from <a href="https://github.com/OasisLMF/OasisPiWind" target="_blank">GitHub</a> using HTTPS or SSH. Before doing this you must generate an SSH key pair on your local machine and add the public key of that pair to your GitHub account (use the GitHub guide at <a href="https://help.github.com/articles/connecting-to-github-with-ssh/" target="_blank">https://help.github.com/articles/connecting-to-github-with-ssh/</a>). To clone over SSH use

    git clone --recursive git+ssh://git@github.com/OasisLMF/OasisPiWind

To clone over HTTPS use

    git clone --recursive https://<GitHub user name:GitHub password>@github.com/OasisLMF/OasisPiWind

## Managing the submodules

There is only submodule - `src/oasis_keys_server` which contains the Flask app that handles the keys requests dispatched to the model lookup services.

Run the command

    git submodule

to list the submodules (latest commit IDs, paths and branches). If any are missing then you can add them using

	git submodule add <submodule GitHub repo URL> <local path/destination>

If you've already cloned the repository and wish to update the submodules (all at once) in your working directory from their GitHub repositories then run

    git submodule foreach 'git pull origin'

You can also update the submodules individually by navigating to their location and pulling from the corresponding remote repository on GitHub.

You should not make any local changes to these submodules because you have read-only access to their GitHub repositories. So submodule changes can only propagate from GitHub to your local repository. To detect these changes you can run `git status -uno` and to commit them you can add the paths and commit them in the normal way.

## Building and running the keys server

First, ensure that you have Docker installed on your system and that your Unix user has been added to the `docker` user group (run `sudo usermod -a -G docker $USER`).

To build the keys server run the command

    sudo docker build -f <docker file name> -t <image name/tag> .

Run `docker images` to list all images and check the one you've built exists. To run the image in a container you can use the command

    docker run -dp 5000:80 --name=<container name/tag> <image name/tag>

To check the container is running use the command `docker ps`. If you want to run the healthcheck on the keys server then use the command

    curl -s http://<server or localhost>:5000/OasisPiWind/<model identifier>/<model version>/healthcheck

You should get a response of `OK` if the keys server has initialised and is running normally, otherwise you should get the HTML error response from Apache. To enter the running container you can use the command

    docker exec -it <container name> bash

The log files to check are `/var/log/apache/error.log` (Apache error log), `/var/log/apache/access.log` (Apache request log), and `/var/log/oasis/keys_server.log` (the keys server Python log). In case of request timeout issues you can edit the `Timeout` option value (in seconds) in the file `/etc/apache2/sites-available/oasis.conf` and restart Apache (`service apache2 restart`).

## Testing the keys server

The `./src/oasis_keys_server` submodule contains a set of Python test cases which you can run against a locally running keys server for a defined model. The tests require configuration information which can be found in an INI file `KeysServerTests.ini` located in `./tests/keys_server_tests/data/<model ID>`. If this subfolder and file does not exist then you will have to create it. The file should define some files and keys server properties needed to run the tests.

    [Default]
    MODEL_VERSION_FILE_PATH=/path/to/your/OasisPiWind/tests/keys_server_tests/data/<model ID>/ModelVersion.csv
    SAMPLE_CSV_MODEL_EXPOSURES_FILE_PATH=/path/to/your/OasisPiWind/tests/keys_server_tests/data/<model ID>/<model loc. test CSV file>
    SAMPLE_JSON_MODEL_EXPOSURES_FILE_PATH=/path/to/your/OasisPiWind/tests/keys_server_tests/data/<model ID>/<model loc. test JSON file>
    KEYS_SERVER_HOSTNAME_OR_IP=localhost
    KEYS_SERVER_PORT=5000

Make sure the paths exist and the server hostname/IP and port are correct. Then copy the INI file (`./tests/keys_server_tests/data/PiWind/KeysServerTests.ini`) to `./src/oasis_keys_server/tests` and then run

    python -m unittest -v KeysServerTests

You should see the tests passing

    test_healthcheck (KeysServerTests.KeysServerTests) ... ok
    test_keys_request_csv (KeysServerTests.KeysServerTests) ... ok
    test_keys_request_csv__invalid_content_type (KeysServerTests.KeysServerTests) ... ok
    test_keys_request_json (KeysServerTests.KeysServerTests) ... ok
    test_keys_request_json__invalid_content_type (KeysServerTests.KeysServerTests) ... ok

    ----------------------------------------------------------------------
    Ran 5 tests in 0.250s

    OK

To run individual test cases you can use

    python -m unittest -v KeysServerTests.KeysServerTests.<test case name>

## Running a test analysis using the Oasis MDK

The Oasis MDK provides utilities for developing models. This is accessed by installing the <a href=https://github.com/OasisLMF/OasisLMF"">oasislmf package</a>. The repository contains a <a href="https://github.com/OasisLMF/OasisPiWind/blob/master/mdk-oasislmf-piwind.json" target="_blank">JSON configuration file</a> for the model which can be used to run the model.

    {
        "keys_data_path": "keys_data/PiWind",
        "model_version_file_path": "keys_data/PiWind/ModelVersion.csv", 
        "lookup_package_path": "src/keys_server",
        "canonical_exposures_profile_json_path": "oasislmf-piwind-canonical-profile.json",
        "source_exposures_file_path": "tests/data/SourceLocPiWind.csv",
        "source_exposures_validation_file_path": "flamingo/PiWind/Files/ValidationFiles/Generic_Windstorm_SourceLoc.xsd",
        "source_to_canonical_exposures_transformation_file_path": "flamingo/PiWind/Files/TransformationFiles/MappingMapToGeneric_Windstorm_CanLoc_A.xslt",
        "canonical_exposures_validation_file_path": "flamingo/PiWind/Files/ValidationFiles/Generic_Windstorm_CanLoc_B.xsd",
        "canonical_to_model_exposures_transformation_file_path": "flamingo/PiWind/Files/TransformationFiles/MappingMapTopiwind_modelloc.xslt",
        "analysis_settings_json_file_path": "analysis_settings.json",
        "model_data_path": "model_data/PiWind"
    }

**NOTE**: All the paths are given relative to the location of the PiWind repository.

An analysis can be executed using the command is:

	oasislmf model run -C mdk-oasislmf-piwind.json -r [OUTPUT_DIRECTORY]
