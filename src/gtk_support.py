import re,threading
from c_cpp_types import *

class Thread(threading.Thread):

    def __init__(self,command,call_back,args=[]):
        
        self._command = command
        self._call_back = call_back
        self.args = args
        super(Thread,self).__init__()
        
    def run(self):
        
        self._command(*self.args)
        self._call_back(*self.args)
        
class gtk_function_type (object):

    def __init__ (self, parent = None):

        super (gtk_function_type, self).__init__ ()

        self.list_funcs = []
        self.name = ""
    
class gtk_functions (object):

    def __init__ (self, parent = None):

        super (gtk_functions, self).__init__ ()

        self.func_str = ""
        self.list_gtk_func_type = []

        self.load_gtk_funcs()
    def callback (self):

        print "loading completed successfully"
        
    def load_gtk_funcs (self):

        self.thread = Thread (self.load_gtk_funcs_thread,self.callback)
        self.thread.start()
        
    def load_gtk_funcs_thread (self):

        f = open ("../gtk_syntax/gtk_functions", "r")
        self.list_gtk_func_type = [gtk_function_type()]
        s = f.readline()
        while s!='':
            func_type_name = s [s.find ('gtk'):s.find ('_',s.find('_')+1)]
            
            if (self.list_gtk_func_type [len(self.list_gtk_func_type)-1].name
                != func_type_name):
                a = gtk_function_type ()
                a.name = func_type_name
                self.list_gtk_func_type.append (a)
                
            func = CFunction()
            func.createFromDeclaration (s)
            self.list_gtk_func_type [len(self.list_gtk_func_type)-1].\
                                    list_funcs.append (func)
            s = f.readline ()

        f.close()
        
    def get_similar_funcs (self, func_str):

        if func_str.count ('_') < 1:
            return []

        func_type_name = func_str [func_str.find ('gtk'):
                                   func_str.find ('_') + 1]
        list_to_return = []
        
        if func_str.count ('_') == 1:            
            for func_type in self.list_gtk_func_type:
                if func_type.name.find (func_str) == 0:
                    list_to_return += [func.getDeclaration () for func in func_type.list_funcs]
        else:
            for func_type in self.list_gtk_func_type:                
                    for func in func_type.list_funcs:
                        if func.name.find (func_str) == 0:
                            list_to_return.append (func.getDeclaration ())
            
        return list_to_return

class gtk_structs (object):

    def __init__ (self, parent = None):

        super (gtk_structs, self).__init__ ()

        self.all_structs_str = ''
        self.load_structs ()
        
    def load_structs (self):

        f = open ('../gtk_syntax/gtk_structs', 'r')
        self.all_structs_str = f.read()
        f.close()

    def is_a_struct (self, struct):

        if re.findall (r'\b%s\b'% (struct), self.all_structs_str) != []:
            return True
        return False

    def get_all_struct_with_str (self, word):
        
        d = re.findall (r'\b%s\w*' % (word), self.all_structs_str)
        print d
        return d

class gtk_defines (object):

    def __init__ (self, parent = None):

        super (gtk_defines, self).__init__ ()

        self.all_defines_str = ''
        self.load_defines ()

    def load_defines (self):

        f = open ('../gtk_syntax/gtk_defines', 'r')
        self.all_defines_str = f.read()
        f.close()

    def is_a_define (self, struct):

        if re.findall (r'\b%s\b'% (struct), self.all_defines_str) != []:
            return True
        return False

    def get_all_define_with_str (self, word):
        
        return re.findall (r'\b%s\w*' % (word), self.all_defines_str)
