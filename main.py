"""
Main program file to execute for processing data
"""

# Import required modules
import input
import electrochem_analysis as echem_ana

curve = echem_ana.Curve(input.work_dir)

#print(curve[2].data.head())

print(curve[2].data.mean())


