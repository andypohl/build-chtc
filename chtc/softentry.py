'''Class dealing with a Software JSON file entry (one of the entries in the array)'''

from urlparse import urlparse
from caseinsensitivedict import CaseInsensitiveDict
from datetime import datetime
import re
import json
from json import JSONDecoder
from json import JSONEncoder

class SoftEntryDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        JSONDecoder.__init__(self, object_hook=self.softentry_parse, *args, **kwargs)

    def softentry_parse(self, d):
        return SoftEntry.factory(d)

class SoftEntry(CaseInsensitiveDict):

    @staticmethod
    def url_filename(url_string):
        ''''''
        u = urlparse(url_string)
        if u.scheme == '' or u.netloc == '':
            raise ValueError("Bad URL encountered")
        if not u.path.endswith('.tar.gz') and not u.path.endswith('.tgz'):
            raise ValueError("URL not a .tar.gz or .tgz")
        return re.sub(r'.*\/', '', u.path)

    @classmethod
    def factory(cls, json_dict):
        '''Factory method to determine which subclass to return'''
        # this seems like it could be inefficient
        cid = CaseInsensitiveDict(json_dict)
        if 'url_extends' in cid:
            return SoftEntryExtending(cid)
        return SoftEntry(cid)
    
    # Initializer
    def __init__(self, cid):
        super(SoftEntry, self).__init__(cid)
        self.prefix = self['software'] + '-' + self['version']
        if 'url_local' in self:
            self['url'] = self['url_local']
        if 'release_date' in self:
            # replace string version of date with a datetime date
            date_string = self.pop('release_date')
            self.release_date = datetime.strptime(date_string, "%Y-%m-%d" ).date()
        if self['url']:
            self.tarball_name = url_filename(self['url'])
        self.pre_commands = [u'# ' + self.prefix, u'wget ' + self['url']]
    # Subclasses hopefully use this too
    def __str__(self):
        return '\n'.join(self.pre_commands + [''] + self['build_commands'])

    # Ordered by release date by default
    def __lt__(self, other):
        if self.release_date and other.release_date:
            return self.release_date - other.release_date

class SoftEntryExtending(SoftEntry):

    # Subclass in the situation we're making a tarball from another tarball
    def __init__(self, cid):
        super(SoftEntryExtending, self).__init__(cid)
        self.pre_commands = self.pre_commands + [u'tar xfz ' + self.tarball_filename, u'cp -R software/* $BUILDDIR/software/']
        self['url'] = self['url_extending']

def __run_tests():
    x = '{"Software": "R", "Release_Date": "2016-10-21", "Dependent_Software": {"Software": "libjpeg", "Version": "1.0"}}'
    y = json.loads(x, cls=SoftEntryDecoder)
    print type(y)

if __name__ == '__main__':
    __run_tests()
