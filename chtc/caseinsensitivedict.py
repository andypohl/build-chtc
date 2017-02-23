''' Found on StackOverflow: http://stackoverflow.com/questions/2082152/case-insensitive-dictionary
I'm not sure there's anything better.'''
class CaseInsensitiveDict(dict):
    '''Version of a dictionary where the keys are case-insensitive.'''
    @classmethod
    def _k(cls, key):
        return key.lower() if isinstance(key, basestring) else key
    def __init__(self, *args, **kwargs):
        super(CaseInsensitiveDict, self).__init__(*args, **kwargs)
        self._convert_keys()
    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(self.__class__._k(key))
    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(self.__class__._k(key), value)
    def __delitem__(self, key):
        return super(CaseInsensitiveDict, self).__delitem__(self.__class__._k(key))
    def __contains__(self, key):
        return super(CaseInsensitiveDict, self).__contains__(self.__class__._k(key))
    def has_key(self, key):
        return super(CaseInsensitiveDict, self).has_key(self.__class__._k(key))
    def pop(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).pop(self.__class__._k(key), *args, **kwargs)
    def get(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).get(self.__class__._k(key), *args, **kwargs)
    def setdefault(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).setdefault(self.__class__._k(key), *args, **kwargs)
    def update(self, E={}, **F):
        super(CaseInsensitiveDict, self).update(self.__class__(E))
        super(CaseInsensitiveDict, self).update(self.__class__(**F))
    def _convert_keys(self):
        for k in list(self.keys()):
            v = super(CaseInsensitiveDict, self).pop(k)
            self.__setitem__(k, v)