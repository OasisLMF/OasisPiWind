#!/usr/bin/env python

#import argparser
import unittest
import os
import filecmp
from parameterized import parameterized
#import pandas as pd
#from pandas.util.testing import assert_frame_equal

dir_output        = os.environ["MODEL_OUTPUT_FOUND"]
dir_expected      = os.environ["MODEL_OUTPUT_EXPECTED"]
filelist_expected = [f for f in os.listdir(os.path.abspath(dir_expected))]
filelist_output   = [f for f in os.listdir(os.path.abspath(dir_output))]

class CheckModelOutput(unittest.TestCase):
    def test_dirs_exisit(self):
        self.assertTrue(os.path.exists(dir_output))
        self.assertTrue(os.path.exists(dir_expected))

    def test_filenames_match(self):
        self.assertTrue(filelist_expected)
        self.assertTrue(filelist_output)
        self.assertEqual(filelist_expected, filelist_output)

    @parameterized.expand(filelist_output)
    def test_values_match(self, file_name):
        '''
        Test if dataframes match to 1 sig figure 'check_less_precise=1'

        check_less_precise : bool or int, default False
        Specify comparison precision. Only used when check_exact is False. 
        5 digits (False) 
        3 digits (True)
        If int, then specify the digits to compare
        '''
        self.assertTrue(filecmp.cmp(
            os.path.join(dir_expected, file_name),
            os.path.join(dir_output, file_name)
        ))

        #assert_frame_equal(
        #    pd.read_csv(os.path.join(dir_expected, file_name)), 
        #    pd.read_csv(os.path.join(dir_output, file_name)), 
        #    #check_exact=False,
        #    #check_less_precise=1,
        #)

if __name__ == "__main__":
    #https://stackoverflow.com/questions/11380413/python-unittest-passing-arguments
    unittest.main()
