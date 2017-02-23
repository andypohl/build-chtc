'''
Class to do with the silly JSON database.  Loading and all the logic of
overriding entries, inheritence, etc.
'''

import json
import os
from softentry import SoftEntry

class SoftJson(object):
    '''Handles the interplay of multiple JSON files.'''

    def add_json_file(self, json_file):
        '''Load JSON file and add contents to current database.'''
        with open(json_file) as fp:
            json_array = json.load(fp)
            for entry in json_array:
                soft_entry = SoftEntry(entry, json_file)
                self.software[soft_entry.prefix] = soft_entry
                self.defaults[soft_entry.software] = soft_entry.prefix

    def __init__(self, json_files=None):
        '''Initialize with or without files.'''
        self.software = {}
        self.defaults = {}
        if json_files is not None:
            if isinstance(json_files, str):
                json_files = [json_files]
            if not isinstance(json_files, list):
                raise TypeError("json_files should be list of strings of filenames or a string of a filename")
            for json_file in json_files:
                self.add_json_file(json_file)
