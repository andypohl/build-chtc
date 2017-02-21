# make docopt class available at package level
from chtc.docopt import docopt

# functions dealing with software JSON file
from chtc.softjson import tarball_prefix, load_software_db, find_all_software, list_software

# class to make the shell script
from chtc.shellscript import ShellScript
