#!/usr/bin/env python

"""build_chtc.py

Make a self-contained program tarball, particularly for CHTC's HTCondor pool.
This will produce an HTCondor submit file and a corresponding script file.

Usage: build_chtc.py <software> [-s <version_number>] [-i] [--json <file> --json <file>] [-r <VAR=value> -r <VAR=value> -x <VAR=value>]
       build_chtc.py -h | --help
       build_chtc.py -l | --list-software

Options:
   -l, --list-software            Show a list of software names and versions input
                                  the default JSON file.
   -h, --help                     Show this message.
   -i, --interactive              Make an interactive submit file.
   --json <file>                  [default: software.json] Specify JSON files to use as software
                                  database.  If using this option to add a second JSON file to
                                  override entries in in the first, then order this option in the
                                  command like "--json first.json --json second.json".
   -s <version_number>, --software-version <version_number>
                                  Specify a version for the software.
   -r <VAR=value>, --substitute <VAR=value>
                                  Replace {{VAR}} in the generated script with the value you want.
                                  This is a required option if the particular JSON entry has 
                                  substitutions at all.  If there are multiple substitutions required,
                                  use the option multiple times e.g. "-r VAR1=val1 -r VAR2=val2".
    -x <VAR=value>, --other <VAR=value>
                                  Other options not mentioned in this help.
                                  
"""

import os
import json
#from pprint import pprint
import chtc

def get_substitutions(subst_list, required_subs):
    '''Process -r/--substitution list'''
    tuples = []
    for subst in subst_list:
        tup = tuple(subst.split('='))
        if len(tup) != 2:
            raise ValueError("Malformed --substition %s" %(subst))
        tuples.append(tup)
    # Check that all required ones are accounted for:
    req_set = set(required_subs)
    my_set = set([tuples[i][0] for i in range(len(tuples))])
    if len(req_set - my_set) > 0:
        raise NameError("Missing required substitutions for the software specified.")
    return tuples

def list_to_dict(other_list):
    '''If there are other options, make a dict'''
    if other_list is None:
        return {}
    other_dict = {}
    if isinstance(other_list, str) or isinstance(other_list, unicode):
        other_list = [other_list]
    for kv in other_list:
        tup = tuple(kv.split('='))
        if len(tup) != 2:
            raise ValueError("Malformed --other %s option" %(kv))
        other_dict[tup[0]] = tup[1]
    return other_dict

def do_make_build(arguments):
    """The 'real' main(). Option logic here."""
#    pprint(arguments)
    json_filenames = arguments['--json']
    my_software = chtc.SoftJson(json_filenames)
    if arguments['--list-software']:
        print '--list-software option not implemented yet'
    else:
        prefix = my_software.lookup(arguments['<software>'], arguments['--software-version'])
        required_subs = my_software.required_substitutions(prefix)
        substitutions = get_substitutions(arguments['--substitute'], required_subs)
        other_options = list_to_dict(arguments['--other'])
        my_shell_script = chtc.ShellScript(prefix, substitutions)
        my_commands = my_software.build_commands_recursive(prefix)
        my_shell_script.add_lines(my_commands)
        if 'bosco' in other_options:
            # Overrides --interactive
            my_submit_file = chtc.BoscoSubmitFile(prefix, other_options['bosco'])
        elif arguments['--interactive']:
            my_submit_file = chtc.InteractiveSubmitFile(prefix)
        else:
            my_submit_file = chtc.SubmitFile(prefix)
        my_shell_script.write()
        my_submit_file.write()
        comments = my_software.get_comments(prefix)
        if comments:
            print comments

if __name__ == '__main__':
    ARGS = chtc.docopt(__doc__, version='build_r.py v0.1 -- 2017-02-17 (github.com/andypohl/building-r)')
    do_make_build(ARGS)
