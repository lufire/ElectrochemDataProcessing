"""
Main program file to execute for processing data
"""
import echem_data.src.electrochem_data as ed
from pathlib import Path
import os

# Read, time-average and plot multiple test data files from Greenlight fuel cell
# test rig measurements
file_dir = Path(__file__).parent.absolute()
file_path = file_dir.joinpath(r'..\TestData\Greenlight\test_data.csv')
eclab_data = ed.EChemDataFile(file_path, 'Greenlight')
print(eclab_data.data)
