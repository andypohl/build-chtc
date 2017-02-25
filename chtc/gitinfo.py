'''A far cry from the API. This provides some minimal interfacing with Git.'''

# Git commands of interest:
#    $ git status -u no -s *.json
#        If this one outputs anything, then a tracked JSON file has
#        been changed.  
#    $ git log -n1 --pretty=format:"Committer: %cn <%ce>%nCommit: %H%nCommitDate: %cd" software.json
#        This gives a succint summary of the last commit on a JSON.

class GitInfo(object):
    '''Process command-line git output and store some info.'''

    def __init__(self):
        '''Not sure how to draw this up yet.'''