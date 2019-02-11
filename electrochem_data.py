"""
Module to process measurement data from a Gamry Instruments potentiostat
"""

# Import required modules
import os
import re
import pandas as pd
import sys
from abc import ABC, abstractmethod
import numpy as np


class DataFile(ABC):
    """
    Base class to process data files
    """
    def __init__(self, path):
        """
        Initialize DataFile object by reading the file and storing
        corresponding members
        """
        self.path = path
        self.file_name = os.path.split(path)[1]
        self.header, self.data, self.units = self.read(path)

    @staticmethod
    def read_as_list(input_file):
        """
        Read in input_file and return list of lines
        """
        if isinstance(input_file, str):
            try:
                with open(input_file, 'r', encoding='latin-1') as f:
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
        header, data, units
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


class EChemDataFile(DataFile, ABC):
    """
    Base class to process electrochemistry data files
    """
    FILE_TYPES = {'DTA': 'DTAFile',
                  'EC-Lab': 'ECLabFile'}

    def __new__(cls, path, file_type):
        if file_type in cls.FILE_TYPES:
            return super(EChemDataFile, cls)\
                .__new__(eval(cls.FILE_TYPES[file_type]))
        else:
            raise NotImplementedError

    def __init__(self, path, file_type):
        """
        Initialize DTAFile object by reading in a the .DTA file and storing
        corresponding members
        """
        self.variable = None
        super().__init__(path)

    @abstractmethod
    def read(self, path):
        """
        Return values of concrete implementation in subclasses:
        header, data, units
        """
        pass

    @abstractmethod
    def calculate_current_density(self, electrode_area):
        """
        Calculate current density based on 'Current' column in data member and
        provided electrode_area (dictionary with keys: name, value, and unit)
        """
        pass


class DTAFile(EChemDataFile):
    """
    Subclass of EChemDataFile to process Gamry DTA-files
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
        columns = []
        for index in data.columns.codes[0]:
            columns.append(data.columns.levels[0][index])
        units = {}
        for index, code in enumerate(data.columns.codes[1]):
            units[columns[index]] = data.columns.levels[1][code]
        data.columns = columns
        return header, data, units

    def read_header(self, lines):
        """
        Extract header as dictionary from total list of lines of data file
        """
        header_list = []
        for line in lines:
            header_list.append(line.strip())
            if self.HEADER_ENDING in line:
                break
        header_dict = {}
        for line in header_list:
            if line and not line.startswith('#'):
                line_list = line.split('\t')
                header_dict[line_list[0]] = tuple(line_list[1:])
        return header_dict, len(header_list)

    def calculate_current_density(self, electrode_area):
        """
        Calculate current density based on 'Current' column in data member and
        provided electrode_area (dictionary with keys: name, value, and unit)
        """
        key = 'Current Density'
        self.units[key] = self.units['Current'] + '/' + electrode_area['unit']
        curr_den = self.data['Current'] / electrode_area['value']
        self.data[key] = curr_den.abs()


class ECLabFile(EChemDataFile):
    """
    Subclass of EChemDataFile to process EC-Lab ASCII txt-files
    """

    FILE_ENDING = 'txt'
    NAMES = {'Ewe': 'Voltage',
             'I': 'Current',
             'P': 'Power',
             'time': 'Time'}
    DELIMITER = '\t'
    DECIMAL = ','

    def read(self, path):
        """
        Read in EC-Lab-file and return list of lines
        """
        lines = self.read_as_list(path)
        header, header_length = self.read_header(lines)
        data = pd.read_csv(path, header=header_length,
                           delimiter=self.DELIMITER, decimal=self.DECIMAL)
        names = []
        units = {}
        for col in data:
            col_list = col.split('/')
            names.append(col_list[0])
            if len(col_list) > 1:
                units[col_list[0]] = col_list[1]
            else:
                units[col_list[0]] = '-'
        data.columns = names
        data.rename(columns=self.NAMES, inplace=True)
        return header, data, units

    @staticmethod
    def read_header(lines):
        """
        Extract header as dictionary from total list of lines of data file
        """
        # Line number of header length variable
        n_header = 2
        header_length = int(lines[n_header-1].split(':')[1].strip()) - 1
        header_list = []
        for i in range(header_length):
            header_list.append(lines[i].strip())
        header_dict = {}
        for line in header_list:
            if line and not line.startswith('#'):
                if ':' in line:
                    line_list = list(map(str.strip, line.split(':', 1)))
                    header_dict[line_list[0]] = line_list[1]
                elif '  ' in line:
                    line_list = list(map(str.strip, line.split('  ', 1)))
                    header_dict[line_list[0]] = line_list[1]
        return header_dict, header_length

    def calculate_current_density(self, electrode_area):
        """
        Calculate current density based on 'Current' column in data member and
        provided electrode_area (dictionary with keys: name, value, and unit)
        """
        key = 'Current Density'
        self.units[key] = self.units['Current'] + '/' + electrode_area['unit']
        curr_den = self.data['Current'] / electrode_area['value']
        self.data[key] = curr_den.abs()


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
        # data = pd.read_csv(path, header=[header_length, header_length+1],
        #                   delimiter=self.DELIMITER, decimal=self.DECIMAL)
        data = None
        units = None
        return header, data, units

    def read_header(self, lines):
        """
        Extract header as dictionary from total list of lines of data file
        """
        header_list = []
        for line in lines:
            header_list.append(line.strip())
            if self.HEADER_ENDING in line:
                break
        header_dict = {}
        for line in header_list:
            if line and not line.startswith('#'):
                line_list = line.split('\t')
                header_dict[line_list[0]] = tuple(line_list[1:])
        return header_dict, len(header_list)

    def set_vars_from_file_names(self, file_names):
        """
        Store variable variation between data file objects associated
        with the provided file names (file_names). file_names strings should
        contain the variable value enclosed by the bounds strings
        """
        var_name = self.header['NAME'][0]
        self.units = {var_name: self.header['UNIT'][0]}
        bounds = self.header['BOUNDS']
        var_values = []
        if isinstance(bounds, (list, tuple)):
            for name in file_names:
                result = re.search(bounds[0] + '(.*)' + bounds[1], name)
                if result:
                    var_values.append(float(result.group(1)))
                else:
                    raise ValueError('Value for variable was not '
                                     'found in file name: ' + name)
        else:
            raise TypeError('bounds must be provided as tuple or list')

        columns = ['File Name', var_name]
        values = [file_names, var_values]
        values = list(map(list, zip(*values)))
        self.data = pd.DataFrame(values, columns=columns)
        self.data.sort_values(var_name, inplace=True)



