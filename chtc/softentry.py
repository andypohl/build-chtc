'''Class dealing with a Software JSON file entry (one of the entries in the array)'''

from urlparse import urlparse
from caseinsensitivedict import CaseInsensitiveDict
from datetime import datetime
import re

class SoftEntry(object):
    '''A single software entry.'''

    # checking one of the fields
    def _check_required_field(self, json_cid, field_name):
        '''Throw a KeyError if required field not found.'''
        msg = "ERROR: JSON entry %s in file %s with required field %s not found." %(("encountered" if self.prefix is None else self.prefix), self.json_filename, field_name)
        if not json_cid.has_key(field_name):
            raise KeyError(msg)

    def _check_fields_at_least_one(self, json_cid, fields):
        '''Throws KeyError if one of the fields in list not in JSON entry.'''
        fields_list = ','.join(["\"%s\"" %(x) for x in fields])
        if len(set(fields) & set(json_cid.keys())) == 0:
            raise KeyError("ERROR: At least one of the following fields: %s required in JSON entry %s in %s" %(fields_list, self.prefix, self.json_filename))

    def _get_string_field(self, json_cid, field_name, required=True):
        '''Throws KeyError or TypeError.  Returns value.'''
        if required:
            self._check_required_field(json_cid, field_name)
        elif not json_cid.has_key(field_name):
            return None
        string = json_cid[field_name]
        if string is None:
            return None
        msg = "ERROR: %s field in JSON entry %s in file %s should be a string but is not." %(field_name, ("encountered" if self.prefix is None else self.prefix), self.json_filename)
        if not isinstance(string, unicode):
            raise TypeError(msg)
        return string

    def _check_and_get_url_type(self, json_cid):
        '''Gets the url type and checks for missing fields.'''
        self._check_fields_at_least_one(json_cid, ["url_extends", "url_local", "url"])
        url_type = "standard"
        if json_cid.has_key('url_extends'):
            url_type = "extends"
        elif json_cid.has_key('url_local'):
            url_type = "local"
        return url_type

    # It's often easy to forget the https:// or ftp:// etc.
    def _check_and_set_url(self, json_cid):
        '''Check to see if it's a valid URL.  If not, throw ValueError'''
        self._check_fields_at_least_one(json_cid, ["url_extends", "url_local", "url"])
        self.extending = False
        field_name = 'url'
        url = self._get_string_field(json_cid, 'url', False)
        if json_cid.has_key('url_extends'):
            self.extending = True
            field_name = 'url_extends'
            url = self._get_string_field(json_cid, 'url_extends', False)
        elif json_cid.has_key('url_local'):
            field_name = 'url_local'
            url = self._get_string_field(json_cid, 'url_local', False)
        self.url_type = self._check_and_get_url_type(json_cid)
        u = urlparse(url)
        if u.scheme == '' or u.netloc == '':
            raise ValueError("ERROR: Field %s in entry %s in file %s doesn't seem to be a URL" %(field_name, self.prefix, self.json_filename))
        if not u.path.endswith('.tar.gz') and not u.path.endswith('.tgz'):
            raise ValueError("ERROR: Field %s in entry %s in file %s doesn't seem to be a .tar.gz or .tgz file" %(field_name, self.prefix, self.json_filename))
        self.url = url

    # We do build stuff in the $BUILDDIR/src dir.  If we're extending another tarball, we need to
    # download that, unpack it, and recursively copy ("cp -R") into the directory above us, then
    # remove the unpacked dir.
    def _extending_build_commands(self):
        '''Appends download/unpacking/copying commands to beginning of self.build_commands'''
        path = urlparse(self.url).path
        path = re.sub(r'.*\/', '', path)
        return [u'tar xfz ' + path, u'cp -R software/* ../', u'rm -rf software/ ' + path]

    # Get a list of strings on cid_key.  e.g. "Build_Commands" or "Substitutions"
    def _get_string_list(self, json_cid, cid_key):
        '''Throws TypeErrors'''
        if not json_cid.has_key(cid_key):
            return []
        array = json_cid[cid_key]
        if not isinstance(array, list):
            raise TypeError("ERROR: Field \"%s\" for entry %s in file %s must be a list" %(cid_key, self.prefix, self.json_filename))
        for item in array:
            if not isinstance(item, unicode) and not isinstance(item, str):
                raise TypeError("ERROR: Field \"%s\" for entry %s in file %s must be a list of strings." %(cid_key, self.prefix, self.json_filename))
        return array

    # Build commands should be an array of strings.  Can't check much beyond that.
    def _get_build_commands(self, json_cid):
        '''Throws TypeErrors and returns nothing.'''
        array = self._get_string_list(json_cid, 'Build_Commands')
        # add some lines to top
        top_commands = [u'# %s' %(self.prefix), u'wget %s' %(self.url)]
        if self.extending:
            top_commands.extend(self._extending_build_commands())
        array[:0] = top_commands
        # add a blank command
        array.append(u'')
        return array

    # More checking.
    def _check_deps(self, json_cid):
        '''Check the array of dictionaries that they are nothing but "Software"/"Version" tuples.
        Throws KeyError, TypeError.  Returns an array of CaseInsensitiveDicts'''
        if not json_cid.has_key('dependent_software'):
            return []
        array = json_cid['dependent_software']
        if not isinstance(array, list):
            raise TypeError("ERROR: Software dependencies for entry %s in file %s must be a list" %(self.prefix, self.json_filename))
        # Could be empty
        cid_array = []
        for item in array:
            cid = CaseInsensitiveDict(item)
            if sorted(cid.keys()) != ['software', 'version']:
                raise KeyError('ERROR: Required fields in software dependencies must be \"Software\" and \"Version\"  from entry %s in file %s' %(self.prefix, self.json_filename))
            cid_array.append(cid)
        return cid_array

    def _check_release_date(self, json_cid):
        '''Throws TypeError if release_date isn't a string. Returns a datetime.date object'''
        if not json_cid.has_key('release_date'):
            return None
        release_date = json_cid['release_date']
        if not isinstance(release_date, unicode):
            raise TypeError("ERROR: Release_Date for entry %s in file %s must be a string" %(self.prefix, self.json_filename))
        dt = datetime.strptime(str(release_date), "%Y-%m-%d" ).date()
        return dt

    def _generate_example_commands(self):
        '''Just return a simple array of commands to git something and copy files'''
        repo_base_dir = self.example_dir.split('/')[0]
        return ["git clone " + self.example_repo,
                "cp -r %s/* $EXAMPLEDIR/" %(self.example_dir),
                "rm -rf " + repo_base_dir]

    # Kind of a long initialization function but it is mostly error-checking
    def __init__(self, json_dict, json_filename):
        '''Initialize with a dictionary from a JSON.  Can throw exceptions.'''
        if json_dict is None or json_dict == {}:
            raise ValueError("ERROR: Found empty software entry in %s." %(json_filename))
        json_cid = CaseInsensitiveDict(json_dict)
        self.prefix = None
        self.json_filename = json_filename
        # REQUIRED fields: 'Software', 'Version', 'URL_extends'/'URL'/'URL_local'
        self.software = self._get_string_field(json_cid, 'software', True)
        self.version = self._get_string_field(json_cid, 'version', True)
        self.prefix = self.software + '-' + self.version
        self._check_and_set_url(json_cid)
        # OPTIONAL fields: 'Build_Commands', 'Release_Date', 'Previous_Version', 'Next_Version', 'Dependent_Software' 
        self.build_commands = self._get_build_commands(json_cid)
        self.example_repo = self._get_string_field(json_cid, 'Example_Repository', required=False)
        self.example_dir = self._get_string_field(json_cid, 'Example_Directory', required=False)
        self.example_commands = self._get_string_list(json_cid, 'Example_Commands')
        if not self.example_commands:       
            if bool(self.example_repo) & bool(self.example_dir):
                self.example_commands = self._generate_example_commands()
        elif bool(self.example_repo) | bool(self.example_dir):
            raise NameError("ERROR: Need to have either Example_Repository/Example_Directory or Example_Commands specfied. Not a combination.")     
        self.required_substitutions = self._get_string_list(json_cid, 'Substitutions')
        self.release_date = self._check_release_date(json_cid)
        self.previous_version = self._get_string_field(json_cid, 'previous_version', False)
        self.next_version = self._get_string_field(json_cid, 'next_version', False)
        self.deps = self._check_deps(json_cid)

##### Command-line testing (not in test suite)
def __run_tests():
    import json
    filename = "../software.json"
    with open(filename) as json_fd:
        array = json.load(json_fd)
        for entry in array:
            x = SoftEntry(entry, filename)
            print x.prefix + ': ' + x.url

if __name__ == '__main__':
    __run_tests()
