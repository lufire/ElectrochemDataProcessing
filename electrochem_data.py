"""
Module to process measurement data from a Gamry Instruments potentiostat
"""

# Import required modules
import pandas as pd
import sys
from abc import ABC, abstractmethod, abstractproperty


class DataFile(ABC):
    """
    Base class to process electrochemistry data files
    """
    FILE_TYPES = {'DTA': 'DTAFile',
                  'Info': 'InfoFile'}

    def __new__(cls, path, file_type):
        # file_ext = path.rsplit('.')[1]
        if file_type in cls.FILE_TYPES:
            return super(DataFile, cls)\
                .__new__(eval(cls.FILE_TYPES[file_type]))
        else:
            # return super(DataFile, cls).__new__(cls, path)
            raise NotImplementedError

    def __init__(self, path, file_type):
        """
        Initialize DTAFile object by reading in a the .DTA file and storing
        corresponding members
        """
        self.path = path
        self.header, self.data = self.read(path)

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

    @abstractmethod
    def read(self, path):
        """
        Return values of concrete implementation in subclasses:
        header, data
        """
        pass

    def __getitem__(self, key):
        if isinstance(key, (tuple, list)):
            if all(isinstance(x, int) for x in key):
                return self.data.iloc[key]
            if all(isinstance(x, str) for x in key):
                return self.data[key]
        elif isinstance(key, (int, slice)):
            return self.data.iloc[key]
        elif isinstance(key, str):
            return self.data[key]
        else:
            raise TypeError('Type is not accepted for direct indexing')


class DTAFile(DataFile):
    """
    Subclass of DataFile to process Gamry DTA-files
    """

    FILE_ENDING = 'DTA'
    HEADER_ENDING = 'CURVE'
    NAMES = {'Vf': 'Voltage',
             'Im': 'Current',
             'Pwr': 'Power',
             'Temp': 'Temperature',
             'T': 'Time'}
    DELIMITER = '\t'
    DECIMAL = ','

    def read(self, path):
        """
        Read in DTA-file and return list of lines
        """
        lines = self.read_as_list(path)
        header, header_length = self.read_header(lines)
        data = pd.read_csv(path, header=[header_length, header_length+1],
                           delimiter=self.DELIMITER, decimal=self.DECIMAL)
        data.drop(data.columns[[0, 1]], axis=1, inplace=True)
        data.rename(columns=self.NAMES, inplace=True)
        return header, data

    def read_header(self, lines):
        """
        Extract header as dictionary from total list of lines of data file
        """
        header_list = []
        for line in lines:
            header_list.append(line)
            if self.HEADER_ENDING in line:
                break
        header_dict = {}
        for line in header_list:
            if line.strip() and not line.startswith('#'):
                line_list = line.rstrip().lstrip().split('\t')
                header_dict[line_list[0]] = tuple(line_list[1:])
        return header_dict, len(header_list)


class InfoFile(DataFile):
    """
    Subclass of DataFile to process custom info files
    """

    FILE_ENDING = 'txt'
    HEADER_ENDING = 'CURVE'
    DELIMITER = '\t'
    DECIMAL = '.'

    def read(self, path):
        """
        Read in DTA-file and return list of lines
        """
        lines = self.read_as_list(path)
        header, header_length = self.read_header(lines)
        data = pd.read_csv(path, header=[header_length, header_length+1],
                           delimiter=self.DELIMITER, decimal=self.DECIMAL)
        return header, data

    def read_header(self, lines):
        """
        Extract header as dictionary from total list of lines of data file
        """
        header_list = []
        for line in lines:
            header_list.append(line)
            if self.HEADER_ENDING in line:
                break
        header_dict = {}
        for line in header_list:
            if line.strip() and not line.startswith('#'):
                line_list = line.rstrip().lstrip().split('\t')
                header_dict[line_list[0]] = tuple(line_list[1:])
        return header_dict, len(header_list)



