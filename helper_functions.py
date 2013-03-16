def str_to_bool(string):

    if string.lower()=='true':
        return True
    return False
        
def getRegExpString(string):

    s = string.replace("(",'\(')
    s = s.replace("*",'\*')
    return s
