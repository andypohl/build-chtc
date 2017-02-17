#!/usr/bin/env python

"""build_chtc.py

Make a self-contained program tarball, particularly for CHTC's HTCondor pool.
This will produce an HTCondor submit file and a corresponding script file.

Usage: build_chtc.py <software> [-s <version_number>] [-i]
       build_chtc.py -h | --help
       build_chtc.py -l | --list-software

Options:
   -l, --list-software            Show a list of software names and versions input
                                  the default JSON file.
   -h, --help                     Show this message.
   -i, --interactive              Make an interactive submit file.
   -s <version_number>, --software-version <version_number>
                                  Specify a version for the software.
"""

import os
import json
#from pprint import pprint   # don't need this unless playing with docopt
from docopt import docopt

def load_software_db(db_file='software.json'):
    """Load what is by default software.json and return the dict."""
    with open(db_file) as json_data:
        data = json.load(json_data)
    return data

def write_script_beginning(script):
    """The beginning of the script.  Set up some environment variables and directories, etc."""
    script.write("""\
#!/bin/bash

# Set up environment:
BUILDDIR=$_CONDOR_SCRATCH_DIR/chtc
export LD_LIBRARY_PATH=$BUILDDIR/lib
export PATH=$BUILDDIR/bin:$PATH

# Set up main build directory:
mkdir -p $BUILDDIR/src

# cd into this directory to stage installs:
cd $BUILDDIR/src

""")

def find_software(soft_db, software_name, software_version):
    """Not the most efficient thing to loop through the JSON array every time, but it
    makes the software JSON format a little simpler. Otherwise there would need to be a key.abs
    field or something.  Anyway this should be basically instantaneous."""
    for entry in soft_db:
        if (entry['Software'] == software_name) and (entry['Version'] == software_version):
            return entry
    raise LookupError("ERROR: %s version %s not found in database" %(software_name,
                                                                     software_version))

def get_default_version(software_name):
    """Quickly open the database and see if there's a default version we can pick.
    It will be the one where Next_Version=null."""
    soft_db = load_software_db()
    for entry in soft_db:
        if (entry['Software'] == software_name) and (entry['Next_Version'] is None):
            return entry['Version']
    raise LookupError("ERROR: Couldn't find a default version of %s in the database" %(software_name))

def write_software_recursive(script, soft_db, software_name, software_version):
    """Recurses through JSON printing build commands in dependency-first order"""
    software_entry = find_software(soft_db, software_name, software_version)
    if 'Dependent_Software' in software_entry.keys():
        for dep in software_entry['Dependent_Software']:
            write_software_recursive(script, soft_db, dep['Software'], dep['Version'])
    # mention the section this is
    script.write('\n# build %s %s\n' %(software_name, software_version))
    # Download locally if possible
    download_url = software_entry['URL']
    if 'URL_local' in software_entry.keys():
        download_url = software_entry['URL_local']
    # sometimes there is no download e.g. Rlibs
    if download_url is not None:
        script.write("curl -O " + download_url + '\n')
    if 'Build_Commands' in software_entry.keys():
        for command in software_entry['Build_Commands']:
            script.write(command + '\n')
    if 'Comment' in software_entry.keys():
        print software_entry['Comment']

def write_script_middle(script, software_name, software_version):
    """Write the middle part of the script. This is the guts of the script."""
    soft_db = load_software_db()
    write_software_recursive(script, soft_db, software_name, software_version)

def write_script_end(script, tarball_prefix):
    """Write the end part of the script."""
    script.write("""\

# cleanup
cd ../
rm -rf src/

# tar it up
cd ../
tar cfz %s.tar.gz chtc
rm -rf chtc/
""" %(tarball_prefix))

def write_submit_file(submit_file, software_name, software_version, is_interactive):
    """Make the submit file to accompany the script for HTCondor."""
    tarball_prefix = software_name + "-" + software_version
    script_filename = tarball_prefix + ".sh"
    if is_interactive:
        variable_lines = "transfer_input_files = %s\n+IsBuildJob = true\nrequirements = (OpSysAndVer =?= \"SL6\") && (IsBuildSlot == true)" %(script_filename)
    else:
        variable_lines = "executable = " + script_filename
    submit_file.write("""\
universe = vanilla
%s
log = build.$(Cluster).$(Process).log
output = build.$(Cluster).$(Process).out
error = build.$(Cluster).$(Process).err
transfer_output_files = %s.tar.gz
should_transfer_files = yes
when_to_transfer_output = on_exit
request_memory = 1GB
request_disk = 5GB
queue
""" %(variable_lines, tarball_prefix))

def make_both_files(software_name, software_version, is_interactive):
    """Make the build script.  Beginning and end are more/less hardcoded, while the
    middle comes from the software.json."""
    try:
        # Must deal with situation where version isn't specified:
        if software_version is None:
            software_version = get_default_version(software_name)
        tarball_prefix = software_name + "-" + software_version
        script_filename = tarball_prefix + ".sh"
        submit_filename = tarball_prefix + ".submit"
        with open(script_filename, "w") as script:
            write_script_beginning(script)
            write_script_middle(script, software_name, software_version)
            write_script_end(script, tarball_prefix)
        os.chmod(script_filename, 0755)
        with open(submit_filename, "w") as submit_file:
            write_submit_file(submit_file, software_name, software_version, is_interactive)
    except LookupError as msg:
        print msg
        try:
            script.close()
            submit_file.close()
        except UnboundLocalError:
            # arises when those files weren't able to be closed because they weren't used
            pass
        os.remove(script_filename)
        os.remove(submit_filename)

def list_software():
    """Print list of software to screen."""
    json_data = load_software_db()
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

def do_make_build(arguments):
    """The 'real' main(). Option logic here."""
    software_name = arguments['<software>']
    software_version = arguments['--software-version']
    is_interactive = arguments['--interactive']
    if arguments['--list-software']:
        list_software()
    else:
        make_both_files(software_name, software_version, is_interactive)
    #pprint(arguments)

if __name__ == '__main__':
    ARGS = docopt(__doc__, version='build_r.py v0.1 -- 2017-02-17 (github.com/andypohl/building-r)')
    do_make_build(ARGS)
