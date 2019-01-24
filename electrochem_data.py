"""
Module to process measurement data from a Gamry Instruments potentiostat
"""

# Import required modules
import re
import pandas as pd
import sys

class DataFile:
    """
    Abstract base class to process electrochemistry data files
    """
    FILE_TYPES = {'DTA': 'DTAFile'}

    def __new__(cls, path):
        file_ext = path.rsplit('.')[1]
        if file_ext in cls.FILE_TYPES:
            return super(DataFile, cls)\
                .__new__(eval(cls.FILE_TYPES[file_ext]))
        else:
            return super(DataFile, cls).__new__(cls, path)

class DTAFile(DataFile):
    """
    Subclass of DataFile to process Gamry DTA-files
    """

    FILE_ENDING = 'DTA'
    HEADER_ENDING = 'CURVE'
    NAMES = {'Voltage': 'Vf',
             'Current': 'Im',
             'Power': 'Pwr',
             'Temperature': 'Temp',
             'Time': 'T'}
    DELIMITER = '\t'
    DECIMAL = ','

    def __init__(self, path):
        """
        Initialize DTAFile object by reading in a the .DTA file and storing
        corresponding members
        """
        self.header, self.data = self.read(path)

    def read(self, path):
        """
        Read in DTA-file and return list of lines
        """
        lines = self.read_as_list(path)
        header = self.read_header(lines)
        header_length = len(header)
        print(header_length)

        data = pd.read_csv(path, header=[header_length, header_length+1],
                           delimiter=self.DELIMITER, decimal=self.DECIMAL)
        data.drop(data.columns[[0, 1]], axis=1, inplace=True)
        return header, data

    @staticmethod
    def read_as_list(input_file):
        """
        Read in input_file and return list of lines
        """
        if isinstance(input_file, str):
            try:
                with open(input_file, 'r') as f:
                    input_list = f.readlines()
            except FileNotFoundError:
                print("File was not found: \n", input_file)
                sys.exit()
        elif isinstance(input_file, (list, tuple)):
            input_list = input_file
        else:
            raise TypeError('Provide the input file either as path pointing '
                            'to file or as tuple or list of content')
        return input_list

    def read_header(self, lines):
        """
        Extract header as dictionary from total list of lines of Gamry DTA-file
        """
        header_list = []
        for line in lines:
            header_list.append(line)
            if self.HEADER_ENDING in line:
                break
        header_dict = {}
        for line in header_list:
            line_list = line.rstrip().split('\t')
            header_dict[line_list[0]] = tuple(line_list[1:])
        return header_dict

    def __getitem__(self, key):
        if isinstance(key, (tuple, list)):
            if all(isinstance(x, int) for x in key):
                return self.data.iloc[key]
            if all(isinstance(x, str) for x in key):
                return self.data[key]
        elif isinstance(key, (int, slice)):
            return self.data.iloc[key]
        elif isinstance(key, str):
            if key in self.NAMES:
                name = self.NAMES[key]
                return self.data[name]
            return self.data[key]
        else:
            raise TypeError('Provided type is accepted for direct indexing')

