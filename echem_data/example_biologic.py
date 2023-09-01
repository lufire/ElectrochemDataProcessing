"""
Main program file to execute for processing data
"""
import echem_data.src.electrochem_data as ed
from pathlib import Path

# Read Biologic potentiostat data
work_dir = Path('../TestData/Biologic')
file_dir = work_dir/'1.4571_plasma.txt'
eclab_data = ed.EChemDataFile(file_dir, 'EC-Lab')
print(eclab_data.data)
