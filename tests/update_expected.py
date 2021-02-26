#!/usr/bin/env python3

from oasislmf.manager import OasisManager
import configparser
import os
import shutil
import json

"""
quick and dirty script to read the CI test config.ini and run default test cases using the MDK 

needs cleanup 
"""

config_file = 'test-config.ini'
config_dir = ''
config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(config_dir, config_file)))


expected_dir = 'ci/expected/'
expected_update = True   #toggle to auto copy new resuslts to expected 

test_model = config.get('default','test_model').lower()
test_list = config.get(test_model,'run_test_cases').split()
test_options = {
    'loc_file': "oed_location_csv", 
    'acc_file': "oed_accounts_csv", 
    'inf_file': "oed_info_csv", 
    'scp_file': "oed_scope_csv", 
    'settings_run': "analysis_settings_json"}


# read this from `oasislmf.json`
default_kwargs = {
    "lookup_config_json": os.path.abspath("../keys_data/PiWind/lookup.json"),
    "lookup_data_dir": os.path.abspath("../keys_data/PiWind"),
    "model_data_dir": os.path.abspath("../model_data/PiWind"),                                                                                    
}

for case in test_list:
    kwargs = default_kwargs.copy()
    kwargs['model_run_dir'] = os.path.join('runs', case)

    for param in test_options:
        val = config.get(f'{test_model}.{case}', param, fallback=None)
        if val:
            kwargs[test_options[param]] = os.path.abspath(os.path.join(config_dir, val))
    print(f" === {case} ==============")
    print(json.dumps(kwargs, indent=4))
    OasisManager().run_model(**kwargs)

    if expected_update: 
        # Copy input files 
        shutil.copytree(
            os.path.join(kwargs['model_run_dir'], 'input'),
            os.path.join(expected_dir, case, 'input'),
            dirs_exist_ok=True
        )

        # copy output files  
        shutil.copytree(
            os.path.join(kwargs['model_run_dir'], 'output'),
            os.path.join(expected_dir, case, 'output'),
            dirs_exist_ok=True
        )
