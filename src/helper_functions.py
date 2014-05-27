import os

def str_to_bool(string):

    if string.lower()=='true':
        return True
    return False
        
def getRegExpString(string):

    s = string.replace("(",'\(')
    s = s.replace("*",'\*')
    return s

def getRootDir():
    cur_dir = os.getcwd ()
    if cur_dir [len (cur_dir) - 1] == os.sep:
        cur_dir = cur_dir [:len (cur_dir) - 1]
    
    src_index = cur_dir.rfind ('/src') +1
        
    return cur_dir [:src_index]