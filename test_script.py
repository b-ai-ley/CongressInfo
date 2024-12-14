# test script to evaluate filepaths and figure out environment setup

def main(args):
    '''
    why do i need this? do i need it at all?
    
    > apparently it lets me execute the file as a script
    and it doesn't run simply when imported !!!!
    '''
    
    
    return 


if __name__ == '__main__':
    print('a')
    import numpy as np
    import pandas as pd
    import requests
    import os
    import sys
    print('b')
    
    current_fp = os.getcwd()
    current_py_v = sys.version
    
    
    print('current fp is ' + current_fp)
    print('current py version is ' + current_py_v)