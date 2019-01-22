"""
Main program file to execute for processing data
"""

# Import required modules
import input
import gamry

print(input.file_path[-3:])
if input.file_path[-3:] == "DTA":
    gamry_dta = gamry.DTAFile(input.file_path)
else:
    raise NotImplementedError('Type for file ending not yet implemented')

print(gamry_dta.data.head())
