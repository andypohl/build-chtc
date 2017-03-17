'''
Class to do with the silly JSON database.  Loading and all the logic of
overriding entries, inheritence, etc.
'''

import json
import os
from softentry import SoftEntryDecoder
from softentry import SoftEntry

class SoftJson(object):
    '''Handles the interplay of multiple JSON files.'''

    def add_json_file(self, json_file, distant=False):
        '''Load JSON file and add contents to current database.'''
        with open(json_file) as fp:
            json_array = json.load(fp, cls=SoftEntryDecoder, distant_url=distant)
            for soft_entry in json_array:
                prefix = soft_entry.get_prefix()
                self.software[prefix] = soft_entry
                self.defaults[soft_entry['software']] = prefix

    def get_deps_recursive(self, prefix):
        '''Recurse over a definitive list of dependent software and skip ones seen'''
        if prefix not in self.software:
            raise LookupError("Couldn't find software %s in the database")
        software = self.software[prefix]
        soft_list = []
        if 'dependent_software' in software:
            for dep in software['dependent_software']:
                dep_soft_list = self.get_deps_recursive(dep.get_prefix())
                # dependencies of dependencies might be asking for a different version
                # so we need to account for that.  Building two different versions of a 
                # software is even worse than building one version twice.
                versionless_list = [d['software'] for d in dep_soft_list]
                for dep_soft in dep_soft_list:
                    vl = dep_soft['software']
                    if vl not in versionless_list:
                        soft_list.append(dep_soft)
        soft_list.append(software)
        return soft_list

    def build_commands_recursive(self, prefix):
        '''Inner recursive function which needs reversing in an outer function.'''
        if prefix not in self.software:
            raise LookupError("Couldn't find software %s in the database")
        soft_list = self.get_deps_recursive(prefix)
        commands_array = []
        for soft in soft_list:
            commands_array.extend(self.software[soft.get_prefix()]['build_commands'])
        return commands_array

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
        if 'substitutions' not in self.software[prefix]:
            return []
        return self.software[prefix]['substitutions']

    def get_comments(self, prefix):
        '''Lookup comments given a prefix'''
        if not self.software.has_key(prefix):
            raise LookupError("Couldn't find software %s in the database")
        return self.software[prefix].get_comments()

    def __init__(self, json_files=None, distant_url=False):
        '''Initialize with or without files.'''
        self.software = {}
        self.defaults = {}
        if json_files is not None:
            if isinstance(json_files, str):
                json_files = [json_files]
            if not isinstance(json_files, list):
                raise TypeError("json_files should be list of strings of filenames or a string of a filename")
            for json_file in json_files:
                self.add_json_file(json_file, distant=distant_url)
