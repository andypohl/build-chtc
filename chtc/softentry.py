'''Class dealing with a Software JSON file entry (one of the entries in the array)'''

from urlparse import urlparse
from caseinsensitivedict import CaseInsensitiveDict
from datetime import datetime
import re
import json
from json import JSONDecoder
from json import JSONEncoder

class SoftEntryDecoder(json.JSONDecoder):

    def __init__(self, **kwargs):
        self.distant_url = False
        if kwargs and 'distant_url' in kwargs:
            self.distant_url = kwargs['distant_url']
        JSONDecoder.__init__(self, object_hook=self.softentry_parse)

    def softentry_parse(self, d, **kwargs):
        return SoftEntry(d, distant_url=self.distant_url)

class SoftEntry(CaseInsensitiveDict):

    @staticmethod
    def url_filename(url_string):
        '''Check a URL, essentially'''
        u = urlparse(url_string)
        if u.scheme == '' or u.netloc == '':
            raise ValueError("Bad URL encountered")
        if not u.path.endswith('.tar.gz') and not u.path.endswith('.tgz'):
            raise ValueError("URL not a .tar.gz or .tgz")
        return re.sub(r'.*\/', '', u.path)
    
    # Initializer
    def __init__(self, cid, distant_url=False):
        super(SoftEntry, self).__init__(cid)
        self.prefix = self['software'] + '-' + self['version']
        if not distant_url and 'url_local' in self:
            self['url'] = self['url_local']
        if 'release_date' in self:
            # replace string version of date with a datetime date
            date_string = self.pop('release_date')
            self.release_date = datetime.strptime(date_string, "%Y-%m-%d" ).date()
        else:
            self.release_date = None
        self.pre_commands = [u'# ' + self.prefix]
        if 'url' in self:
            self.pre_commands = self.pre_commands +  [u'wget ' + self['url']]
        if 'build_commands' in self:
            self['build_commands'] = self.pre_commands + self['build_commands']

    # Subclasses hopefully use this too
    def __str__(self):
        if 'build_commands' not in self:
            return ''
        return '\n'.join(self['build_commands'])

    # Ordered by release date by default
    def __lt__(self, other):
        if self.release_date and other.release_date:
            return self.release_date - other.release_date

    # access methods... I don't remember the rationale for these but 
    # they seem like a good practice 
    def get_prefix(self):
        '''Return the prefix string i.e. "<software>-<version>"'''
        return self.prefix

    def get_release_date(self):
        '''Return release date as datetime.date'''
        return self.release_date

    def get_comments(self):
        if 'comments' in self:
            return self['comments']
        return None