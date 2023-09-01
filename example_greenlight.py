"""
Main program file to execute for processing data
"""
import src.electrochem_data as ed
from pathlib import Path

# Read, time-average and plot multiple test data files from Greenlight fuel cell
# test rig measurements
work_dir = Path('TestData/Greenlight')
file_dir = work_dir/'maxcoat-80ti-ast_gts1_ast-mc - 230715 074738 - part_0.csv'
eclab_data = ed.EChemDataFile(file_dir, 'Greenlight')
print(eclab_data.data)
