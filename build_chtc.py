#!/usr/bin/env python

"""build_chtc.py

Make a self-contained program tarball, particularly for CHTC's HTCondor pool.
This will produce an HTCondor submit file and a corresponding script file.

Usage: build_chtc.py <software> [-s <version_number>] [-i] [--json <file> --json <file>]
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
"""

import os
import json
import chtc

def do_make_build(arguments):
    """The 'real' main(). Option logic here."""
    json_filenames = arguments['--json']
    my_software = chtc.SoftJson(json_filenames)
    if arguments['--list-software']:
        print '--list-software option not implemented yet'
    else:
        prefix = my_software.lookup(arguments['<software>'], arguments['--software-version'])
        my_shell_script = chtc.ShellScript(prefix)
        my_commands = my_software.build_commands(prefix)
        my_shell_script.add_lines(my_commands)
        my_submit_file = chtc.SubmitFile(prefix)
        my_submit_file.interactive = arguments['--interactive']
        my_shell_script.write()
        my_submit_file.write()
    #pprint(arguments)

if __name__ == '__main__':
    ARGS = chtc.docopt(__doc__, version='build_r.py v0.1 -- 2017-02-17 (github.com/andypohl/building-r)')
    do_make_build(ARGS)
