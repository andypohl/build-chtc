#!/usr/bin/env python

"""build_chtc.py

Make a self-contained program tarball, particularly for CHTC's HTCondor pool.
This will produce an HTCondor submit file and a corresponding script file.

Usage: build_chtc.py <software> [-s <version_number>] [-d <dir>]
       build_chtc.py -h | --help

Options:
   -h, --help                     Show this message.
   -s <version_number>, --software-version <version_number>
                                  Specify a version for the software.
   --request-mem <memory>         [default: 1GB] (for the submit file).  (IN PROGRESS)
   --request-disk <disk>          [default: 3GB] (for the submit file).  (IN PROGRESS)
   -d <dir>, --build-dir <dir>    [default: chtc] The base subdirectory
                                  where the software is installed.
"""

import os
import json
from pprint import pprint
from datetime import datetime
from docopt import docopt

SCRIPT_FILENAME = "build.sh"
SUBMIT_FILENAME = "build.submit"

def load_software_db(db_file='software.json'):
    """Load what is by default software.json and return the dict."""
    with open(db_file) as json_data:
        data = json.load(json_data)
    return data

def generation_info(for_script):
    """Return some information about the script/submit file being made for provenance sake."""
    info = " generated " + datetime.now().strftime("%Y-%d-%m at %H:%M")
    if for_script:
        return SCRIPT_FILENAME + " script" + info
    else:
        return SUBMIT_FILENAME + " submit file" + info

def write_script_beginning(script, software_name, software_version, build_dir):
    """The beginning of the script.  Set up some environment variables and directories, etc."""
    script.write("""\
#!/bin/bash

# %s
# for software = %s, version = %s, build_dir = %s

# Set up environment:
BUILDDIR=$_CONDOR_SCRATCH_DIR/%s
export LD_LIBRARY_PATH=$BUILDDIR/lib
export PATH=$BUILDDIR/bin:$PATH

# Set up main build directory:
mkdir -p $BUILDDIR/src

# cd into this directory to stage installs:
cd $BUILDDIR/src

""" %(generation_info(for_script=True), software_name, software_version, build_dir, build_dir))


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
    script.write("curl -O " + download_url + '\n')
    for command in software_entry['Build_Commands']:
        script.write(command + '\n')
    if 'Comment' in software_entry.keys():
        print software_entry['Comment']

def write_script_middle(script, software_name, software_version):
    """Write the middle part of the script. This is the guts of the script."""
    soft_db = load_software_db()
    write_software_recursive(script, soft_db, software_name, software_version)

def write_script_end(script, build_dir):
    """Write the end part of the script."""
    script.write("""\

# cleanup
cd ../
rm -rf src/

# tar it up
cd ../
tar cfz %s.tar.gz %s
rm -rf %s
""" %(build_dir, build_dir, build_dir))

def write_submit_file(submit_file, build_dir):
    """Make the submit file to accompany the script for HTCondor."""
    submit_file.write("""\
universe = vanilla
executable = %s
log = build.$(Cluster).$(Process).log
output = build.$(Cluster).$(Process).out
error = build.$(Cluster).$(Process).err
transfer_output_files = %s.tar.gz
should_transfer_files = yes
when_to_transfer_output = on_exit
request_memory = 1GB
request_disk = 5GB
queue
""" %(SCRIPT_FILENAME, build_dir))

def make_script_file(software_name, software_version, build_dir):
    """Make the build script.  Beginning and end are more/less hardcoded, while the
    middle comes from the software.json."""
    try:
        # Must deal with situation where version isn't specified:
        if software_version is None:
            software_version = get_default_version(software_name)
        with open(SCRIPT_FILENAME, "w") as script:
            write_script_beginning(script, software_name, software_version, build_dir)
            write_script_middle(script, software_name, software_version)
            write_script_end(script, build_dir)
        os.chmod(SCRIPT_FILENAME, 0755)
        with open(SUBMIT_FILENAME, "w") as submit_file:
            write_submit_file(submit_file, build_dir)
    except LookupError as msg:
        print msg
        script.close()
        submit_file.close()
        os.remove(SCRIPT_FILENAME)
        os.remove(SUBMIT_FILENAME)

def do_make_build(arguments):
    """The 'real' main().  Do the main option logic here, if there is any.
    Make the script, then the submit file.  Returns nothing."""
    software_name = arguments['<software>']
    software_version = arguments['--software-version']
    build_dir = arguments['--build-dir']
    make_script_file(software_name, software_version, build_dir)
    #pprint(arguments)

if __name__ == '__main__':
    ARGS = docopt(__doc__, version='build_r.py v0.1 -- 2017-02-17 (github.com/andypohl/building-r)')
    do_make_build(ARGS)
