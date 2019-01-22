"""
Input data file
"""

# Import required modules
import os

# Working directory containing set of files to process
work_dir \
    = r"W:\Projekte\IGF_UZB_61602\04 Bearbeitung\Batteriemessung_112018\MK1"
file_name = r"PWRGALVANOSTATIC-ps0-zn-paa1-20181108-1715.DTA"

file_path = os.path.join(work_dir, file_name)
