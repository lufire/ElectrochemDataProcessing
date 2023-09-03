"""
Main program file to execute for processing data
"""
import pandas as pd
from pathlib import Path

# Read and plot ZBT test rig data
file_dir = Path(__file__).parent.absolute()
work_dir = file_dir.joinpath(r'..\TestData\ZBT-LabView')
file_path = work_dir.joinpath(r'08_01_2019_Danfoss_Duese_0.2_Wasser')
dataframe = pd.read_csv(file_path, delimiter='\t', decimal=',')
dataframe1 = dataframe[dataframe['p1 (aicv6)'] > 0.1]
ax = dataframe1.plot('Unnamed: 1', 'p1 (aicv6)')
fig = ax.get_figure()
fig.savefig(str(work_dir/'plot.png'), bbox_inches='tight')