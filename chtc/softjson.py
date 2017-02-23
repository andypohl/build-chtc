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

    def _build_commands_reversed(self, prefix):
        '''Inner recursive function which needs reversing in an outer function.'''
        if not self.software.has_key(prefix):
            raise LookupError("Couldn't find software %s in the database")
        software = self.software[prefix]
        commands_array = []
        for dep in software.deps:
            dep_prefix = dep['software'] + '-' + dep['version']
            dep_commands_array = self._build_commands_reversed(dep_prefix)
            commands_array.extend(dep_commands_array)
        commands_array.extend(software.build_commands)
        return commands_array
    
    def build_commands(self, prefix):
        '''Build up the list of commands, recursively'''
        commands = self._build_commands_reversed(prefix)
        commands.reverse()
        return commands

    def lookup(self, software_name, software_version):
        '''Raise a LookupError if not found. Otherwise return prefix.'''
        if software_version is not None:
            prefix = software_name + '-' + software_version
            if not self.software.has_key(prefix):
                raise LookupError("Couldn't find %s version %s in database" %(software_name, software_version))
        else:
            try:
                prefix = self.defaults[software_name]
            except KeyError:
                raise LookupError("Couldn't find %s in software database" %(software_name))
        return prefix
    
    def required_substitutions(self, prefix):
        '''Lookup a substitution list given a prefix'''
        if not self.software.has_key(prefix):
            raise LookupError("Couldn't find software %s in the database")
        return self.software[prefix].required_substitutions

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
