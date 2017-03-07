# make docopt class available at package level
from chtc.docopt import docopt

# functions dealing with software JSON file
#from chtc.softjson import tarball_prefix, load_software_db, find_all_software, list_software

# class to make the shell script
from chtc.shellscript import ShellScript
from chtc.submitfile import SubmitFile
from chtc.caseinsensitivedict import CaseInsensitiveDict
from chtc.ordereddict import OrderedDict
from chtc.softentry import SoftEntryDecoder
from chtc.softentry import SoftEntry
from chtc.softjson import SoftJson
