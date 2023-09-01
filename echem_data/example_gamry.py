"""
Main program file to execute for processing data
"""
import echem_data.src.electrochem_analysis as ea
from pathlib import Path

# Read, time-average and plot multiple test data files from Gamry measurements
work_dir = Path('../TestData/Gamry')
curve = ea.Curve(work_dir/'0k8V_zn8_paa1_20181112', 'DTA')
curve.plot_means('Pump Speed', 'Current', points=50, save_file=True)
curve.plot_series('Current')
curve.plot_means('Pump Speed', 'Current Density', points=50, save_file=True)
multi_curve = ea.MultiCurve(work_dir, 'DTA')
multi_curve.plot_means('Pump Speed', 'Current Density',
                       points=50, save_file=True)
