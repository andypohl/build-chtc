'''
Functions to do with the silly JSON database.  Loading and all the logic of
overriding entries, inheritence, etc.
'''

import json
import os

def tarball_prefix(entry_or_dep):
    '''Either Software-Version or just Software.  This becomes the tarball prefix.'''
    if 'Version' not in entry_or_dep.keys():
        return entry_or_dep['Software']
    return entry_or_dep['Software'] + '-' + entry_or_dep['Version']

# probably should separate this out into its own module at some point
def load_software_db(file_names):
    '''Load JSON files and return a dict keyed on software-version'''
    if file_names is None or not isinstance(file_names, list) or len(file_names) == 0:
        return None
    my_dict = {}
    defaults = {}
    try:
        for fname in file_names:
            with open(fname) as json_fp:
                json_array = json.load(json_fp)
                # set aside heirs for now
                # overriding. note we also override previous entries in the same file.
                # entries not seen before but are supposed to inherit something are
                # discarded.
                for entry in json_array:
                    key = tarball_prefix(entry)
                    if key in my_dict.keys() and 'Inherits' in entry.keys():
                        for subkey, val in entry.iterkeys():
                            my_dict[key][subkey] = val
                    elif 'Inherits' not in my_dict.keys():
                        my_dict[key] = entry
                    # assign default software to be the bottom-most entry in the JSON file
                    defaults[entry['Software']] = key
    except IOError:
        print "ERROR: Couldn't find one of the files"
        return None
    combined = {"Defaults": defaults, "Entries": my_dict}
    return combined

def find_all_software(soft_dict, tarball_prefix):
    if tarball_prefix not in soft_dict.keys():
        return False
    if 'Dependent_Software' in soft_dict[tarball_prefix].keys():
        for entry in soft_dict[tarball_prefix]['Dependent_Software']:
            return find_all_software(soft_dict, entry)
    return True

def list_software(json_files):
    """Print list of software to screen."""
    json_data = load_software_db(json_files)
    col1_format = '{0:<24}'
    header = ['Software (Version)', 'Depends on']
    print col1_format.format(header[0]) + header[1]
    for entry in json_data:
        if 'Dependent_Software' in entry.keys():
            deps = [s['Software']+' ('+s['Version']+')' for s in entry['Dependent_Software']]
            deps = 'N/A' if len(deps) == 0 else ', '.join(deps)
        else:
            deps = 'N/A'
        print col1_format.format(entry['Software'] + ' (' + entry['Version'] + ')') + deps

def __run_tests():
    files = ["software.json"]
    my_dict = load_software_db(files)
    print my_dict

if __name__ == '__main__':
    __run_tests()
