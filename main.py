"""
Main program file to execute for processing data
"""

# Import required modules
import input
import electrochem_data as echem_data
import electrochem_analysis as echem_ana


#print(input.file_path[-3:])
#if input.file_path[-3:] == "DTA":
#    gamry_dta = echem_data.DTAFile(input.file_path)
#else:
#    raise NotImplementedError('Type for file ending not yet implemented')

#print(gamry_dta.data.head())

curve = echem_ana.Curve(input.work_dir)

print(curve.mean_values("Vf", 25))


