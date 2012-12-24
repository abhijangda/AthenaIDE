#177 Lines
from PyQt4 import QtCore
import re

class IncludeFileThread(QtCore.QThread):

    def __init__(self,includefilenamearray,filetype,parent=None):

        QtCore.QThread.__init__(self,parent)
        self.includefileclassarray = []
        self.includefilefuncarray = []
        self.includefiledatatypearray = []
        self.includefileslist = includefilenamearray
        self.filetype = filetype
        self.datatypearray = ['char','double','float','int','long','void']

    def setfilelist(self,filelist):
        self.includefileslist = filelist
        #print filelist

    def run(self):
        
        self.includefileclassarray = []
        self.includefilefuncarray = []
        self.includefiledatatypearray = []
        if self.filetype == 'C Project' or self.filetype == 'C File':
            
            for filename in self.includefileslist:
                
                f = open(filename,'r')
                text = ''
                for d in f:
                    text += d
                f.close()
                #print text
                for i in self.datatypearray:
                    for search_iter in re.finditer(r'\b%s\b\s*(\w+.+)\s*{'%i,text):
                        d = search_iter.group()                    
                        d = d[d.find(i)+len(i)+1:d.rfind('\n')]                    
                        if "(" in d and ")" in d and "=" not in d:
                                self.includefilefuncarray.append(d)
                                self.includefiledatatypearray.append(i)
                    for search_iter in re.finditer(r'\b%s\b\s*(\w+.+)\;'%i,text):
                        d = search_iter.group()                    
                        d = d[d.find(i)+len(i)+1:d.rfind('\n')]                    
                        if "(" in d and ")" in d and "=" not in d:
                            if d not in self.includefilefuncarray:
                                self.includefilefuncarray.append(d)
                                self.includefiledatatypearray.append(i)
            #print self.includefilefuncarray              
        if self.filetype == 'C++ Project' or self.filetype == 'C++ File':            
            for filename in self.includefileslist:
                print filename
                f = open(filename,'r')
                text = ''
                for d in f:
                    text += d
                f.close()
                #print text
                cpp_reg_array = re.findall(r'\bclass\b\s*(\w+.+?\}\s*\;)',text,re.DOTALL)
                if cpp_reg_array!=[]:
                    for class_definition in cpp_reg_array:
                        self.includefilefuncarray.append([])
                        self.includefiledatatypearray.append([])
                        #print class_definition
                        if re.findall(r'>\s*\bclass\b\s*\w+',class_definition)!=[]:
                            class_definition = class_definition[class_definition.index('>')+1:len(class_definition)]
                            class_definition = class_definition.lstrip()                        
                            class_name = re.findall(r'\bclass\b\s*(\w+)',class_definition)[0]
                            count = len(re.findall(r'\benum\b',class_definition)) + len(re.findall(r'\bclass\b',class_definition)) + len(re.findall(r'\bstruct\b',class_definition))
                            count -= len(re.findall(r'\}\s*;',class_definition))
                            i=0
                            regex_array = re.findall(r'(?<=\}\;)\s*\w+.+?(?=\}\;)',text,re.DOTALL)
                            while(count>0):
                                if i<len(regex_array):
                                    class_definition += regex_array[i]+'};'
                                else:
                                    break
                                count = len(re.findall(r'\benum\b',class_definition)) + len(re.findall(r'\bclass\b',class_definition)) + len(re.findall(r'\bstruct\b',class_definition))
                                count -= len(re.findall(r'\}\s*;',class_definition))                            
                                i+=1
                            class_definition = class_definition[class_definition.index('class')+len('class'):]
                            self.includefileclassarray.append(class_name)                        
                        else:                        
                            count = len(re.findall(r'\benum\b',class_definition)) + len(re.findall(r'\bclass\b',class_definition)) + len(re.findall(r'\bstruct\b',class_definition))
                            count -= len(re.findall(r'\}\s*;',class_definition))
                            i=0
                            regex_array = re.findall(r'(?<=\}\;)\s*\w+.+?(?=\}\;)',text,re.DOTALL)
                            while(count>0):
                                if i< len(regex_array):
                                    class_definition += regex_array[i]+'};'
                                else:
                                    break
                                count = len(re.findall(r'\benum\b',class_definition)) + len(re.findall(r'\bclass\b',class_definition)) + len(re.findall(r'\bstruct\b',class_definition))
                                count -= len(re.findall(r'\}\s*;',class_definition))                            
                                i+=1                       
                            
                            class_name = re.findall(r'\s*(\w+)',class_definition)[0]                        
                            self.includefileclassarray.append(class_name)
                        #print class_definition
                        ###Removing any number of nested classes and enums and structs
                        ##Can also be done using re.sub function
                        ##Try re.sub function to improve performance
                        class_definition = class_definition[class_definition.index('{')+1:]
                        class_definition_new = ""
                        end=0
                        for search_iter in re.finditer(r'\bclass\b\s*(\w+.+?\}\s*\;)',class_definition,re.DOTALL):
                            class_definition_new+=class_definition[end:search_iter.start()]
                            end=search_iter.end()
                        class_definition_new+=class_definition[end:]
                        class_definition = class_definition_new

                        class_definition_new = ""
                        end=0
                        for search_iter in re.finditer(r'\benum\b(.+?\}\s*\;)',class_definition,re.DOTALL):
                            class_definition_new+=class_definition[end:search_iter.start()]
                            end=search_iter.end()
                        class_definition_new+=class_definition[end:]
                        class_definition = class_definition_new                    

                        class_definition_new = ""
                        end=0
                        for search_iter in re.finditer(r'\bstruct\b\s*(\w+.+?\}\s*\;)',class_definition,re.DOTALL):
                            class_definition_new+=class_definition[end:search_iter.start()]
                            end=search_iter.end()
                        class_definition_new+=class_definition[end:]
                        class_definition = class_definition_new

                        ##Code to detect inline functions 
                        ##Here inline functions body will be removed from the class_definition
                        ##Also inline functions will be converted to normal non-inlined functions
                        inline_function=""
                        bracket_array=[('{',i.start()) for i in re.finditer(r'\{',class_definition)]
                        bracket_array+=[('}',j.start()) for j in re.finditer(r'\}',class_definition)]                    
                        #print class_definition
                        for i in range(len(bracket_array)):
                            for k in range(len(bracket_array)-1):
                                if bracket_array[k][1]>bracket_array[k+1][1]:
                                    o=bracket_array[k+1]
                                    bracket_array[k+1]=bracket_array[k]
                                    bracket_array[k]=o                    
                        class_definition_new=""
                        n=0
                        for search_iter in re.finditer(r'\s*(\w+.+)\s*\{',class_definition):
                            inline_function = search_iter.group()
                            class_definition_new += class_definition[n:search_iter.end()-1]+';'
                            if inline_function.find('{')!=-1:
                                inline_function = inline_function[:inline_function.find('{')]
                            count = 0
                            for j,i in enumerate(bracket_array):
                                if i[0]=='{':
                                    count +=1
                                else:
                                    count -=1
                                if count ==0:
                                    break
                            n=bracket_array[j][1]+1
                            bracket_array = bracket_array[j+1:]
                        if bracket_array !=[]:
                            class_definition_new +=class_definition[n:bracket_array[len(bracket_array)-1][1]]
                        else:
                            class_definition_new +=class_definition[n:]
                        class_definition = class_definition_new
                                                  
                        ##Find out the members
                        reg_exp_funcarray = re.findall(r'\s+(.+\w+.+)\s*?\;',class_definition)
                        
                        if reg_exp_funcarray != []:                        
                            
                            for d in reg_exp_funcarray:
                                add = False
                                if "(" in d and ")" in d and "=" not in d:
                                    add = True
                                    index_open_bracket = d.rfind('(')
                                    space_rindex = 0
                                    for search_iter in re.finditer(r'\s*\w+\(',d):
                                        space_rindex = search_iter.start()                                    

                                if "(" not in d and ")" not in d:
                                    if '=' in d:
                                        add = True
                                        equals_index = d.rfind('=')
                                        can_break = False
                                        for space_rindex in range(equals_index,0,-1):
                                            if d[space_rindex].isalnum() or d[space_rindex] == '_':
                                                can_break = True
                                            else:
                                                if d[space_rindex].isspace() and can_break == True:
                                                    break                                    
                                    else:
                                        add = True
                                        space_rindex = d.rfind(' ')                            
                                if add == True:
                                    if '=' in d:
                                        self.includefilefuncarray[len(self.includefilefuncarray)-1].append(d[space_rindex:equals_index-1].lstrip())
                                    else:
                                        self.includefilefuncarray[len(self.includefilefuncarray)-1].append(d[space_rindex:].lstrip())
                                        self.includefiledatatypearray[len(self.includefiledatatypearray)-1].append(d[0:space_rindex].rstrip())
        
##            print self.includefiledatatypearray
##            print self.includefilefuncarray
            print self.includefileclassarray
