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

    def get_deps_bfs(self, prefix):
        '''BF-traverse over a definitive list of dependent software and prioritize ones seen'''
        if prefix not in self.software:
            raise LookupError("Couldn't find software %s in the database")
        top_software = self.software[prefix]
        # Working queue (FIFO)
        soft_queue = []
        soft_queue.append(top_software)
        # Final list to construct (LIFO)
        soft_list = []
        while len(soft_queue) > 0:
            # pop the top of the queue
            # python 2.7 dequeue and collections would be more elegant
            popped = soft_queue.pop(0)
            # version-less check to see if software's in the list already or not
            version_less_list = [t['software'] for t in soft_list]
            if popped['software'] in version_less_list:
                # if it is, pull that one off the list so it gets compiled earlier
                removed_ix = version_less_list.index(popped['software'])
                removed = soft_list.pop(removed_ix)
                popped = removed
            soft_list.insert(0, popped)
            if 'dependent_software' in popped:
                for dep in popped['dependent_software']:
                    soft_queue.append(self.software[dep.get_prefix()])
        return soft_list

    def commands_cat(self, prefix):
        '''Inner function which needs reversing in an outer function.'''
        if prefix not in self.software:
            raise LookupError("Couldn't find software %s in the database")
        soft_list = self.get_deps_bfs(prefix)
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

    def subset(self, prefix_list):
        '''Return all or some of the SoftEntrys as a list'''
        return [self.software[prefix] for prefix in prefix_list]
    
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
