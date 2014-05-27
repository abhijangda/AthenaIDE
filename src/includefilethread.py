#177 Lines
from PyQt4 import QtCore
import re,os
from c_cpp_types import *
from helper_functions import *

class IncludeFileThread(QtCore.QThread):

    def __init__(self,includefilenamearray,filetype,parent=None):

        QtCore.QThread.__init__(self,parent)
        self.includefileclassarray = []
        self.includefilefuncarray = []
        self.includefiledatatypearray = []
        self.includefileslist = includefilenamearray
        self.filetype = filetype
        self.list_typedef = []
        
    def setfilelist(self,filelist):
        self.includefileslist = filelist
        #print filelist

    def run(self):

        self.includefileclassarray = []
        self.includefilefuncarray = []
        self.includefiledatatypearray = []
        if self.filetype == 'C Project' or self.filetype == 'C File':
            
            for filename in self.includefileslist:
                if os.path.exists(filename)==False:
                    continue
                f = open(filename,'r')
                text = ''
                for d in f:
                    text += d
                f.close()
                #print text

                cpp_reg_array = re.findall(r'\bstruct\b\s*\w+.+?\}\s*\;',text,re.DOTALL)
                
                if cpp_reg_array!=[]:
                    for class_definition in cpp_reg_array:
                        
                        if class_definition.count('{')>class_definition.count('}'):
                            regex_array = re.findall(r'(?<=\}\;)\s*\w+.+?(?=\}\;)',text,re.DOTALL)
                            count = class_definition.count('{')-class_definition.count('}')
                            i=0
                            while count>0 and i<len(regex_array):
                               class_definition += regex_array[i] + '};'
                               count = class_definition.count('{')-class_definition.count('}')

                        class_definition = class_definition[class_definition.find('struct'):]

                        text = text.replace(class_definition,'')

                        c_struct = CStruct()
                        c_struct.createFromDeclaration(class_definition)
                        self.includefileclassarray.append(c_struct)

                    for struct in self.includefileclassarray:

                        d = re.findall(r'\btypedef\s+%s\s+.+;'%struct.getDeclaration(),text)
                        
                        for s in d:
                            s = s.replace(';','')
                            typedef = CTypedef()
                            typedef.createFromDeclaration(s)
                            typedef.typedef_with = struct
                            struct.list_typedef.append(typedef)
                            self.list_typedef.append(typedef)
                    
                for search_iter in re.finditer(r'\w+[\s*\*]*\s+[\s*\*]*\w+\s*\(.*\s*.*\)\s*?;',text):
                    #print d,filename
                    d = search_iter.group()                    
                    if d.rfind ('\n') > d.rfind (')'):
                        d = d[:d.rfind('\n')]

                    d = d.replace ('\n', ' ')
                    if isThisAFunction(d)==False:
                        continue
                    func = CFunction()
                    func.createFromDeclaration(d)
                    self.includefilefuncarray.append(func)                    
                    #self.includefiledatatypearray.append(i)
                
                for search_iter in re.finditer(r'\w+[\s*\*]*\s+[\s*\*]*\w+\s*\(.*\s*.*\)\s*?{',text):
                    d = search_iter.group()
                    if d.rfind ('\n') > d.rfind (')'):
                        d = d[:d.rfind('\n')]

                    d = d.replace ('\n', ' ')
                    
                    func = CFunction()
                    func.createFromDeclaration(d)
                    #print func.name
                    if isThisAFunction(d)==False:
                        continue
                    
                    should_continue = False
                    for _func in self.includefilefuncarray:
                        if _func.isEqualTo(func)==True:
                            should_continue = True
                            break
                    if should_continue==True:
                        continue
                    
                    self.includefilefuncarray.append(func)              
                        
        elif self.filetype == 'C++ Project' or self.filetype == 'C++ File':            
            for filename in self.includefileslist:
                if os.path.exists(filename)==False:
                    continue
                f = open(filename,'r')
                text = ''
                for d in f:
                    text += d
                f.close()
                #print text
                cpp_reg_array = re.findall(r'[\btemplate\s*<class\s+\w+\s*>]*\bclass\b\s*\w+.+?\}\s*\;',text,re.DOTALL)
                
                if cpp_reg_array!=[]:
                    for class_definition in cpp_reg_array:
                        
                        if class_definition.count('{')>class_definition.count('}'):
                            regex_array = re.findall(r'(?<=\}\;)\s*\w+.+?(?=\}\;)',text,re.DOTALL)
                            count = class_definition.count('{')-class_definition.count('}')
                            i=0
                            while count>0 and i<len(regex_array):
                               class_definition += regex_array[i] + '};'
                               count = class_definition.count('{')-class_definition.count('}')

                        if 'template' in class_definition:
                            class_definition = class_definition[class_definition.find('template'):]
                        else:
                            class_definition = class_definition[class_definition.find('class'):]

                        text = text.replace(class_definition,'')

                        cpp_class = CPPClass()
                        #print class_definition
                        cpp_class.createFromDeclaration(class_definition)
                        self.includefileclassarray.append(cpp_class)
                        
##            for _class in self.includefileclassarray:
##                print _class.name,"class name"
##                print 'public'
##                for _var in _class.list_public_members:
##                    print _var.type + _var.return_type + _var.name
##
##                print 'private'
##                for _var in _class.list_private_members:
##                    print _var.type + _var.return_type + _var.name
##
##                print 'protected'
##                for _var in _class.list_protected_members:
##                    print _var.type + _var.return_type + _var.name
##
##                print 'nested'
##                for __class in _class.list_nested_class_structs:
##                    print __class.name,"         class name"
##                    print '         public'
##                    for _var in __class.list_public_members:
##                        print _var.type + _var.return_type + _var.name
##
##                    print '      private'
##                    for _var in __class.list_private_members:
##                        print _var.type + _var.return_type + _var.name
##
##                    print '     protected'
##                    for _var in __class.list_protected_members:
##                        print _var.type + _var.return_type + _var.name
