#1222 lines


from PyQt4 import QtGui
from PyQt4.Qt import QTextCursor
from PyQt4 import QtGui,QtCore 
import re
global indentct,indentTF
indentct = 0

class txtInputclass(QtGui.QTextEdit):
       
    def __init__(self,filetype,parent=None):
        
        QtGui.QTextEdit.__init__(self,parent)
        self.openbrackets = 0
        self.closebrackets = 0
        self.openbigbrackets = 0
        self.closebigbrackets = 0
        self.removeselectedtext = True
        self.bracketspaired=0
        self.bigbracketspaired=0
        self.encoding = ''
        self.datatypearray = ['char','double','float','int','long','void']
        self.includefilefuncarray = []
        includefilefuncposarray=[]
        self.includefiledatatypearray = []
        self.includefileclassarray = []
        self.object_classarray = []
        self.object_namearray = []
        self.funcmatchlist = QtGui.QListWidget(self)
        self.connect(self.funcmatchlist,QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem*)'),self.funcmatchlistdoubleclicked)
        self.funcmatchlist.setVisible(False)
        self.prev_pos = 0
        self.remove_prev_highlight = False
        self.indentwidth = ''
        self.indentTF = ''
        self.inc_indent_syms = ''
        self.dec_indent_syms = ''
        self.parent = parent
        self.filetype = filetype
        self.prev_line = -1
        self.linestrackarray = [-1,-1,-1,-1,-1]
        self.boollinetrack = True
        self.showtooltip = False
        self.contains_class_definitions = False
        self.connect(self,QtCore.SIGNAL('cursorPositionChanged()'),self.cursor_position_changed)
        
        try:            
            settings = ''
            settingsfile = open('./settings.ini','r')
            for line in settingsfile:
                settings = settings + line
            
            settingsfile.close()
            
            for i in range(settings.index('<indentwidth>')+len('<indentwidth>'),settings.index('</indentwidth>')):
                self.indentwidth = self.indentwidth + settings[i]
                
            for i in range(settings.index('<incindentsymbols>')+len('<incindentsymbols>'),settings.index('</incindentsymbols>')):
                self.inc_indent_syms = self.inc_indent_syms + settings[i]
                
            for i in range(settings.index('<decindentsymbols>')+len('<decindentsymbols>'),settings.index('</decindentsymbols>')):
                self.dec_indent_syms = self.dec_indent_syms + settings[i]

            for i in range(settings.index('<indentation>')+len('<indentation>'),settings.index('</indentation>')):
                self.indentTF= self.indentTF + settings[i]                
        except:
            pass
    
    def document_contents_change(self,position,charsRemoved,charsAdded):
        
        ### Here the positions of detected functions and classes will be updated
        ### Whenever the text of the document is changed
        ### And also whenever some text is removed then whether that function exists
        ### or not
        cc = self.textCursor()
        
        if self.filetype == 'C Project' or self.filetype == 'C File':
            if len(self.parent.combo_funcposarray)>0 and self.parent.combo_funcposarray[0] > cc.position()-1:
                start_index = 0
            else:
                start_index = self.parent.combo_func.currentIndex()+1
            
            if charsRemoved == 0:
                for i in range(start_index,self.parent.combo_func.count()):
                    self.parent.combo_funcposarray[i] += charsAdded                    
            else:
                if charsAdded == 0:
                    if start_index !=0:                        
                        #func = str(self.includefilefuncarray[start_index-1])
                        func = ''
                        for d in str(self.includefilefuncarray[start_index-1]):
                            if d == '*' or d == '(' or d==')'or d=='[' or d==']':
                                func += '\\'+d
                            else:
                                func += d
                        data_type = self.includefiledatatypearray[start_index-1]                        
                        s=str(self.toPlainText())                        
                        if re.findall(r'\b%s\s*%s'%(data_type,func),s)==[]:
                            del self.includefilefuncarray[start_index-1]
                            del self.includefiledatatypearray[start_index-1]
                            del self.parent.combo_funcposarray[start_index-1]
                            self.parent.combo_func.removeItem(start_index-1)
                        
                    for i in range(start_index,self.parent.combo_func.count()):
                        self.parent.combo_funcposarray[i] -= charsRemoved
        else:
            if self.filetype == 'C++ Project' or self.filetype == 'C++ File':
                if self.parent.combo_class.count() == 0:
                    if len(self.parent.combo_funcposarray)>0 and self.parent.combo_funcposarray[0] > cc.position():
                        start_index = 0
                    else:
                        start_index = self.parent.combo_func.currentIndex()+1
                    
                    if charsRemoved == 0:
                        for i in range(start_index,self.parent.combo_func.count()):
                            self.parent.combo_funcposarray[i] += charsAdded                    
                    else:
                        if charsAdded == 0:
                            if start_index !=0:                                                                
                                s=str(self.toPlainText())
                                func = ''
                                for d in str(self.parent.combo_func.itemText(start_index-1)):
                                    if d == '*' or d == '(' or d==')'or d=='[' or d==']':
                                        func += '\\'+d
                                    else:
                                        func += d
                                
                                data_type = func.split(' ')[0]
                                func = func[func.find(' ')+1:]                              
                                
                                if re.findall(r'\b%s\s*%s'%(data_type,func),s)==[]:                                    
                                    del self.parent.combo_funcposarray[start_index-1]
                                    self.parent.combo_func.removeItem(start_index-1)
                            for i in range(start_index,self.parent.combo_func.count()):
                                self.parent.combo_funcposarray[i] -= charsRemoved
                else:
                    if charsAdded == 0:
                        s=str(self.toPlainText())
                        try:
                            if self.contains_class_definitions == False:                                
                                func = ''
                                start_index = self.parent.combo_func.currentIndex()
                                for d in str(self.parent.combo_func.itemText(start_index)):
                                    if d == '*' or d == '(' or d==')'or d=='[' or d==']':
                                        func += '\\'+d
                                    else:
                                        func += d                        
                                class_index = self.includefileclassarray.index(str(self.parent.combo_class.itemText(self.parent.combo_class.currentIndex())))
                                data_type = self.includefiledatatypearray[class_index][start_index]
                                data_type = data_type[data_type.find(' ')+1:]
                                class_name = self.parent.combo_class.itemText(self.parent.combo_class.currentIndex())                        
                                if re.findall(r'\b%s\s*%s::%s'%(data_type,class_name,func),s)==[]:  
                                    del self.parent.combo_funcposarray[self.parent.combo_class.currentIndex()][start_index]
                                    del self.parent.func_array[self.parent.combo_class.currentIndex()][start_index]
                                    self.parent.combo_func.removeItem(start_index)
                        except:
                            pass
                        if self.filetype == 'C++ Project' and self.contains_class_definitions == True:                            
                                func = ''
                                start_index = self.parent.combo_func.currentIndex()
                                for d in str(self.parent.combo_func.itemText(start_index)):
                                    if d == '*' or d == '(' or d==')'or d=='[' or d==']':
                                        func += '\\'+d
                                    else:
                                        func += d
                                try:
                                    class_index = self.includefileclassarray.index(str(self.parent.combo_class.itemText(self.parent.combo_class.currentIndex())))
                                except IndexError:
                                    class_index = self.includefileclassarray.index(str(self.parent.combo_class.itemText(self.parent.combo_class.currentIndex()+1)))
                                    
                                data_type = self.includefiledatatypearray[class_index][start_index]                                
                                class_name = self.parent.combo_class.itemText(self.parent.combo_class.currentIndex())                                
                                if re.findall(r'\b%s'%(func),s)==[]:                                    
                                    del self.parent.combo_funcposarray[class_index][start_index]                                    
                                    self.parent.combo_func.removeItem(start_index)
                         
                    for current_class_index in range(self.parent.combo_class.currentIndex(),self.parent.combo_class.count()):
                        if len(self.parent.combo_funcposarray)>0 and self.parent.combo_funcposarray[current_class_index][0] > cc.position():
                            start_index = 0
                        else:
                            start_index = self.parent.combo_func.currentIndex()+1
                        
                        if charsRemoved == 0:
                            for i in range(start_index,len(self.parent.combo_funcposarray[current_class_index])):
                                self.parent.combo_funcposarray[current_class_index][i] += charsAdded
                        else:
                            if charsAdded == 0:                                
                                for i in range(start_index,len(self.parent.combo_funcposarray[current_class_index])):
                                    
                                    self.parent.combo_funcposarray[current_class_index][i] -= charsRemoved
                                    

    def cursor_position_changed(self):
        
        cc = self.textCursor()
        self.line = cc.blockNumber()
        self.funcmatchlist.setVisible(False)
        
        if self.prev_line != self.line:
            QtGui.QToolTip.hideText()
            self.showtooltip = False
            if self.boollinetrack == True:                
                i=0
                while(i<5 and self.linestrackarray[i]!=-1):
                    i+=1
                index = i
                if i<5:
                    if self.linestrackarray[i-1]!=cc.blockNumber()+1 and i!=0:
                        self.linestrackarray[i] = cc.blockNumber()+1
                    else:
                        if i==0:
                            self.linestrackarray[i] = cc.blockNumber()+1
                j=0
                if i==5:
                    i=0
                    while i<5 and self.linestrackarray[i] !=cc.blockNumber()+1:
                        i+=1
                    if i==5:
                        for j in range(0,4):
                            self.linestrackarray[j] = self.linestrackarray[j+1]
                        self.linestrackarray[4] = cc.blockNumber()+1
                    
                    if i<4:
                        for j in range(i,4):
                            self.linestrackarray[j] = self.linestrackarray[j+1]
                        self.linestrackarray[4] = cc.blockNumber()+1            
                
            if self.filetype == 'C Project' or self.filetype == 'C File':
                for i in range(len(self.parent.combo_funcposarray)-1,-1,-1):
                    if self.parent.combo_funcposarray[i] < cc.position():
                        self.parent.combo_func.setCurrentIndex(i)
                        break                
            else:
                if self.filetype == 'C++ Project':
                    try:                        
                        if self.parent.combo_class.count() == 0:
                            for i in range(len(self.parent.combo_funcposarray)-1,-1,-1):
                                if self.parent.combo_funcposarray[i] < cc.position():
                                    self.parent.combo_func.setCurrentIndex(i)
                                    break
                        else:
                            for i in range(len(self.parent.combo_funcposarray)-1,-1,-1):
                                can_break = False
                                for j in range(len(self.parent.combo_funcposarray[i])-1,-1,-1):
                                    if self.parent.combo_funcposarray[i][j] < cc.position():
                                        if self.parent.combo_class.currentIndex() != i:
                                            self.parent.combo_class_item_activated(i)
                                            self.parent.combo_class.setCurrentIndex(i)
                                        self.parent.combo_func.setCurrentIndex(j)
                                        can_break = True
                                        break
                                if can_break == True:
                                    break                                
                    except:
                        pass
                else:
                    if self.filetype == 'C++ File':
                        try:
                            if self.parent.combo_class.count() != 0:
                                for i in range(len(self.parent.combo_funcposarray)):
                                    can_break = False
                                    for j in range(len(self.parent.combo_funcposarray[i])-1,-1,-1):
                                        if self.parent.combo_funcposarray[i][j] < cc.position():
                                            if self.parent.combo_class.currentIndex() != i:
                                                self.parent.combo_class_item_activated(i)
                                                self.parent.combo_class.setCurrentIndex(i)
                                            self.parent.combo_func.setCurrentIndex(j)
                                            can_break = True
                                            break
                                    if can_break == True:
                                        break
                        except:
                            pass
        
        self.prev_line = self.line
        
    def fill_c_code_completion(self):

        self.document().contentsChange.connect(self.document_contents_change)
        text = str(self.toPlainText())
        self.includefilefuncarray = []
        self.includefiledatatypearray = []
        self.parent.combo_funcposarray=[]
        self.parent.combo_func.clear()
        if self.filetype == 'C Project' or self.filetype == 'C File':                
            for i in self.datatypearray:
                for search_iter in re.finditer(r'\b%s\b\s*(\w+.+)\s*{'%i,text):
                    d = search_iter.group()                    
                    d = d[d.find(i)+len(i)+1:d.rfind('\n')]                    
                    if "(" in d and ")" in d and "=" not in d:
                            self.includefilefuncarray.append(d)
                            self.includefiledatatypearray.append(i)
                            self.parent.combo_funcposarray.append(search_iter.start())
                            self.parent.combo_func.addItem(i+" "+d)        

    def fill_cpp_code_completion(self):

        text = str(self.toPlainText())
        
        ##There can be three cases, either there can be global functions in the file
        ## or there can be function definitions of classes
        ## or classes will be defined
        ## But these three cases are valid for projects only
        ## In a C++ File, there may be any combination of these three cases
        ## So for file let us first take the find the class definition and then
        ## find its functions definitions. Declaration of functions inside the
        ## class declaration will be ignored.
        ## Function definitions of classes outside the class declarations is extracted
        
        if self.filetype == 'C++ File':            
            self.parent.func_array = []            
            self.parent.combo_funcposarray=[]
            self.parent.combo_class.clear()
            #print re.findall(r'\bclass\b\s*(\w+.+?\}\s*\;)',text,re.DOTALL)
            for class_search_iter in re.finditer(r'\bclass\b\s*(\w+.+?\}\s*\;)',text,re.DOTALL):
                class_definition = class_search_iter.group()
                class_name = ''
                
                if 'class' in class_definition:
                    if '>' in class_definition:
                        class_definition = class_definition[class_definition.index('<')+1:]
                    class_definition = class_definition[class_definition.index('class')+len('class'):]
                    spaces = 0
                    for d in class_definition:
                        if d == ' ':
                            spaces +=1
                        else:
                            break
                    class_definition = class_definition[spaces:len(class_definition)]
                    class_name = ''
                    for j in class_definition:
                        if j == '\n' or j== '{' or j == ':' or j==' ':
                            break
                        else:
                            class_name = class_name + j
                    #print class_name
                else:                    
                    for j in class_definition:
                        if j == '\n' or j== '{' or j == ':' or j==' ':
                            break
                        else:
                            class_name = class_name + j
                    
                count = 0
                
                self.parent.combo_class.addItem(class_name)
                self.parent.combo_funcposarray.append([])
                self.parent.func_array.append([])
                for search_iter in re.finditer(r'\b%s\s*::\s*(\w+.+)\s*{'%class_name,text):
                             
                    d = search_iter.group()
                    if d.find('\n') != -1:
                        if d.find('{') > d.find('\n'):
                            d = d[d.find('::')+2:d.find('\n')]
                        if d.find('{') < d.find('\n'):
                            d = d[d.find('::')+2:d.find('{')]
                    else:
                        d = d[d.find('::')+2:d.find('{')]
                        
                    if "(" in d and ")" in d and "=" not in d:
                        self.parent.func_array[len(self.parent.func_array)-1].append(d)
                        self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1].append(search_iter.start())
                    count +=1
                    contains_class_functions = True          

        ####For files in C++ Project
        if self.filetype == 'C++ Project':
            self.parent.func_array = []
            self.parent.combo_funcposarray=[]
            self.parent.combo_class.clear()
            contains_class_functions = False
            for i in range(len(self.includefileclassarray)):
                count = 0                    
                for search_iter in re.finditer(r'\b%s::\s*(\w+.+)\s*{'%self.includefileclassarray[i],text):
                    if count == 0:
                        self.parent.combo_class.addItem(self.includefileclassarray[i])
                        self.parent.combo_funcposarray.append([])
                        self.parent.func_array.append([])
                    d = search_iter.group()
                    if d.find('\n') != -1:
                        if d.find('{') > d.find('\n'):
                            d = d[d.find('::')+2:d.find('\n')]
                        if d.find('{') < d.find('\n'):
                            d = d[d.find('::')+2:d.find('{')]
                    else:
                        d = d[d.find('::')+2:d.find('{')]
                        
                    if "(" in d and ")" in d and "=" not in d:
                        self.parent.func_array[len(self.parent.func_array)-1].append(d)
                        self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1].append(search_iter.start())
                    count +=1
                    contains_class_functions = True
            #print self.parent.combo_funcposarray
            #print self.parent.func_array
            ##########################################
            count = 0
            ####For file containing class definition
            if contains_class_functions==False:
                self.contains_class_definitions = False
                for class_search_iter in re.finditer(r'\bclass\b\s*(\w+.+?\}\s*\;)',text,re.DOTALL):
                    self.contains_class_definitions = True
                    class_definition = class_search_iter.group()
                    self.parent.func_array.append([])
                    self.parent.combo_funcposarray.append([])
                    #print class_definition
                    #self.includefiledatatypearray.append([])                    
                    if 'class' in class_definition:                        
                        class_definition = class_definition[class_definition.index('class')+len('class'):]
                        spaces = 0
                        for d in class_definition:
                            if d == ' ':
                                spaces +=1
                            else:
                                break
                        class_definition = class_definition[spaces:len(class_definition)]
                        angle_bracket_index = class_definition.find('>')
                        if angle_bracket_index !=-1:
                            starting_brace = class_definition.find('{')
                            if starting_brace !=-1:
                                if starting_brace > angle_bracket_index:
                                    new_line_index = class_definition.find('\n',angle_bracket_index,starting_brace)
                                    if new_line_index !=-1:
                                        class_definition = class_definition[new_line_index+1:]
                                    else:
                                        class_definition = class_definition[angle_bracket_index+1:]
                        if 'class ' in class_definition:                        
                            class_definition = class_definition[class_definition.index('class ')+len('class '):]                        
                        class_name = ''
                        for j in class_definition:
                            if j == '\n' or j== '{' or j == ':' or j==' ':
                                break
                            else:
                                class_name = class_name + j
                        class_name = class_name.rstrip()
                    else:
                        class_name = ''
                        for j in class_definition:
                            if j == '\n' or j== '{' or j == ':' or j==' ':
                                break
                            else:
                                class_name = class_name + j
                    self.parent.combo_class.addItem(class_name)
                    #for j in self.datatypearray:
                        #reg_exp_funcarray = re.findall(r'\b%s\b\s*(\w+.+)'%j,class_definition)
                    for search_iter in re.finditer(r'\s+(.+\w+.+)?\;',class_definition):
                        d = search_iter.group()                            
                        add = False
                        if "(" in d and ")" in d and "=" not in d:
                            add = True
                            index_open_bracket = d.rfind('(')
                            space_rindex = 0
                            if ' ' in d:                                        
                                can_break = False
                                for space_rindex in range(index_open_bracket+1,0,-1):
                                    if d[space_rindex].isalnum() or d[space_rindex] == '_':
                                        can_break = True
                                    else:
                                        if d[space_rindex].isspace() and can_break == True:
                                            break                                
                            
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
                            count =1
                            if '=' in d:
                                self.parent.func_array[len(self.parent.func_array)-1].append(d[0:space_rindex].rstrip() + ' ' +d[space_rindex:equals_index-1].lstrip())
                            else:
                                self.parent.func_array[len(self.parent.func_array)-1].append((d.rstrip()).lstrip())
                            self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1].append(search_iter.end()+class_search_iter.start()-len(class_name))
                            
            ##For file containing only global functions
            if contains_class_functions == False and count ==0:
                for i in self.datatypearray:                    
                    for search_iter in re.finditer(r'\b%s\b\s*(\w+.+)\s*{'%i,text):
                        if count == 0:
                            self.parent.hbox_combo.removeWidget(self.parent.combo_class)
                        d = search_iter.group()    
                        d = d[d.find(i)+len(i)+1:d.rfind('\n')]            
                        if "(" in d and ")" in d and "=" not in d:                                
                                self.parent.combo_funcposarray.append(search_iter.start())
                                self.parent.combo_func.addItem(i+" "+d)
                        count = 1
            ############################################            
        self.document().contentsChange.connect(self.document_contents_change)
        
    def funcmatchlistdoubleclicked(self,item):
        
        cc = self.textCursor()
        cc.select(QTextCursor.WordUnderCursor)
        cc.removeSelectedText()
        text = str(item.text())
        if "(" in text and ")" in text and "=" not in text:
            add = True
            index_open_bracket = text.rfind('(')
            space_rindex = 0
            if ' ' in text:                                        
                can_break = False
                for space_rindex in range(index_open_bracket+1,0,-1):
                    if text[space_rindex].isalnum() or text[space_rindex] == '_':
                        can_break = True
                    else:
                        if text[space_rindex].isspace() and can_break == True:
                            break          
            text = text[:text.find('(')]            
        if "(" not in text and ")" not in text:
            if '=' in text:
                equals_index = text.rfind('=')
                can_break = False
                for space_rindex in range(equals_index,0,-1):
                    if text[space_rindex].isalnum() or text[space_rindex] == '_':
                        can_break = True
                    else:
                        if text[space_rindex].isspace() and can_break == True:
                            break                                    
            else:
                add = True
                space_rindex = text.rfind(' ')
        self.insertPlainText(text[space_rindex:].lstrip())
        self.funcmatchlist.setVisible(False)        

    def highlightcurrentline(self):

        cc = self.textCursor()
        self.prev_pos = cc.position()
        cc.setPosition(cc.position()+1,cc.MoveAnchor)
        cc.select(cc.LineUnderCursor)
        self.setTextCursor(cc)
        self.setTextBackgroundColor(QtGui.QColor(242,242,242,255))
        cc.setPosition(self.prev_pos,cc.MoveAnchor)
        self.setTextCursor(cc)
        self.remove_prev_highlight = True
          
    def keyPressEvent(self,event):

        global indentct
        if self.removeselectedtext == False:
            cc = self.textCursor()
            cc.setPosition(cc.position(),QTextCursor.MoveAnchor)
            self.setTextCursor(cc)
            self.removeselectedtext = True
        line =''
        k=0        

        if event.key() == 16777234 or event.key() == 16777219: #16777234 represents Left Key 16777219 for Backspace Key

            cc = self.textCursor()
            currentposition = cc.position()
            cc.select(QTextCursor.LineUnderCursor)
            line = cc.selectedText()
            spaces = 0
            for d in line:
                if d == ' ':
                    spaces+=1
                else:
                    break
            cc.movePosition(QTextCursor.StartOfLine,QTextCursor.MoveAnchor)
            lineposition = cc.position()
            maxleftposition = cc.position()+spaces
             
            if event.key() == 16777219:
                if currentposition <= maxleftposition and currentposition != lineposition:
                    if (currentposition-lineposition)%len(self.indentwidth)==0:
                        cc.setPosition(currentposition,QTextCursor.MoveAnchor)
                        cc.setPosition(currentposition-len(self.indentwidth)+1,QTextCursor.KeepAnchor)
                        cc.removeSelectedText()
                    else:
                        cc.setPosition(currentposition,QTextCursor.MoveAnchor)
                        cc.setPosition(lineposition+int(float(currentposition-lineposition)/float(len(self.indentwidth)))*len(self.indentwidth)+1,QTextCursor.KeepAnchor)
                        cc.removeSelectedText()
                    self.setTextCursor(cc)
            else:
                
                if currentposition <= maxleftposition and currentposition != lineposition:
                    if (currentposition-lineposition)%len(self.indentwidth)==0:
                        cc.setPosition(currentposition-len(self.indentwidth)+1,QTextCursor.MoveAnchor)
                    else:
                        cc.setPosition(lineposition+int(float(currentposition-lineposition)/float(len(self.indentwidth)))*len(self.indentwidth)+1,QTextCursor.MoveAnchor)
                    self.setTextCursor(cc)
                                          
        if self.indentTF == 'True':
            if event.key() == 16777220 and indentct>=0:
                cc = self.textCursor()
                #cc.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
                cc.movePosition(QTextCursor.StartOfLine,QTextCursor.KeepAnchor)
                line = str(cc.selectedText())                
                try:                    
                    if self.filetype == 'C Project' or self.filetype == 'C File':
                        ##To add functions when enter key is pressed to func array
                        line = line + ' '
                        for i in self.datatypearray:
                            for search_iter in re.finditer(r'\b%s\b\s*(\w+.+)'%i,line):
                                d = search_iter.group()
                                d = d[d.find(i)+len(i)+1:d.rfind('\n')]                            
                                if "(" in d and ")" in d:
                                    if "=" not in d and ";" not in d:
                                        if d not in self.includefilefuncarray:                                       
                                            self.includefilefuncarray.insert(self.parent.combo_func.currentIndex()+1,d)
                                            self.includefiledatatypearray.insert(self.parent.combo_func.currentIndex()+1,i)
                                            self.parent.combo_funcposarray.insert(self.parent.combo_func.currentIndex()+1,cc.position())
                                            self.parent.combo_func.insertItem(self.parent.combo_func.currentIndex()+1,i+" "+d)
                        line = line[:len(line)-1]
                    else:
                        #####Code to add functions and classes, when they are added
                        scope_resolution_operator_found = False
                        if self.parent.combo_class.count() == 0:
                            line = line + ' '
                            for i in self.datatypearray:
                                for search_iter in re.finditer(r'\b%s\b\s*(\w+.+)'%i,line):                                
                                    d = search_iter.group()
                                    d = d[d.find(i)+len(i)+1:d.rfind('\n')]                                
                                    if "(" in d and ")" in d:
                                        if "=" not in d and ";" not in d:
                                            if d not in self.includefilefuncarray:
                                                self.includefilefuncarray.insert(self.parent.combo_func.currentIndex()+1,d)
                                                self.includefiledatatypearray.insert(self.parent.combo_func.currentIndex()+1,i)
                                                self.parent.combo_funcposarray.insert(self.parent.combo_func.currentIndex()+1,cc.position())
                                                self.parent.combo_func.insertItem(self.parent.combo_func.currentIndex()+1,i+" "+d)
                            line = line[:len(line)-1]
                        else:
                            combo_class_current_index = self.parent.combo_class.currentIndex()
                            combo_class_current_text = str(self.parent.combo_class.itemText(combo_class_current_index))                        
                            for search_iter in re.finditer(r'\b%s::\s*(\w+.+)\s*'%str(self.parent.combo_class.itemText(combo_class_current_index)),line):
                                d = search_iter.group()
                                if "(" in d and ")" in d and "=" not in d and ";" not in d:
                                        scope_resolution_operator_found = True
                                        func = d[d.find(combo_class_current_text)+len(combo_class_current_text)+len('::'):]
                                        for i in range(self.parent.combo_func.count()):
                                            if d == self.parent.combo_func.itemText(i):
                                                break
                                        if i != self.parent.combo_func.count():                                        
                                            self.parent.combo_funcposarray[combo_class_current_index].insert(self.parent.combo_func.currentIndex()+1,cc.position())                                    
                                            self.parent.combo_func.insertItem(self.parent.combo_func.currentIndex()+1,func)
                            ######If file contains class definition#####
                            if self.filetype == 'C++ Project':                            
                                for search_iter in re.finditer(r'\s+(.+\w+.+)?\;',line):
                                    d = search_iter.group()                            
                                    add = False
                                    if "(" in d and ")" in d and "=" not in d:
                                        add = True
                                        index_open_bracket = d.rfind('(')
                                        space_rindex = 0
                                        if ' ' in d:                                        
                                            can_break = False
                                            for space_rindex in range(index_open_bracket+1,0,-1):
                                                if d[space_rindex].isalnum() or d[space_rindex] == '_':
                                                    can_break = True
                                                else:
                                                    if d[space_rindex].isspace() and can_break == True:
                                                        break                                
                                        
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
                                        count =1
                                        if '=' in d:
                                            self.parent.func_array[combo_class_current_index].insert(self.parent.combo_func.currentIndex()+1,d[0:space_rindex].rstrip() + ' ' +d[space_rindex:equals_index-1].lstrip())
                                            self.parent.combo_func.insertItem(self.parent.combo_func.currentIndex()+1,d[0:space_rindex].rstrip() + ' ' +d[space_rindex:equals_index-1].lstrip())
                                        else:
                                            self.parent.func_array[combo_class_current_index].insert(self.parent.combo_func.currentIndex()+1,(d.rstrip()).lstrip())
                                            self.parent.combo_func.insertItem(self.parent.combo_func.currentIndex()+1,(d.rstrip()).lstrip())
                                        self.parent.combo_funcposarray[combo_class_current_index].insert(self.parent.combo_func.currentIndex()+1,cc.position())                                
                                ##########################################################################
                    
                        if scope_resolution_operator_found == False:                            
                            ##Match classnames and add object names                        
                            for i in self.includefileclassarray:
                                if i in line:
                                    try:
                                        p = re.findall(r'\b%s\b\s*(\w+.?\;)'%i,line,re.DOTALL)[0] ##reg exp for finding only one object name, if there are more than one then except block will be called
                                        if ';' in p:
                                           object_array = [p[0:len(p)-1]]
                                        else:
                                           object_array = p.split(',')
                                    except IndexError :
                                        object_array = re.findall(r'\b%s\b\s*(\w+.+)?\;'%i,line,re.DOTALL)[0].split(',') #reg exp for finding more than one object name
                                               
                                    for j in object_array:
                                        try:
                                            index = self.object_namearray.index(j)
                                            #print index
                                            if i != self.object_classarray[index]:
                                                self.object_classarray[index] = i
                                        except:
                                            self.object_namearray.append(j)
                                            self.object_classarray.append(i)                        
                            #print self.object_namearray
                            #print self.object_classarray
                            ##################################################
                except:
                    pass
                if line == '':
                    cc.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
                    cc.movePosition(QTextCursor.StartOfLine,QTextCursor.KeepAnchor)
                    line = str(cc.selectedText())
                
                linesplit = line.split(self.indentwidth)
                indentct = 0
                if line != '':
                    for i in range(0,len(linesplit)-1):
                        d = linesplit[i]
                        if d == '':
                            indentct +=1
                        if d != '':
                            break
                    
                    cc.clearSelection()
                    cc.movePosition(QTextCursor.EndOfLine,QTextCursor.MoveAnchor)
                    inc_count=0
                    dec_count=0
                    for d in self.inc_indent_syms:
                        if d!=' ' and d!='\t':
                            inc_count += line.count(d)
                    for d in self.dec_indent_syms:
                        if d!=' ' and d!='\t':
                            dec_count += line.count(d)
                    if inc_count>dec_count:
                        k = 1                                                                        
                        indentct +=1
                        if indentct == 0:
                            QtGui.QTextEdit.keyPressEvent(self,event)
                            cc.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
                            cc.insertText(self.indentwidth)
                        QtGui.QTextEdit.keyPressEvent(self,event)
                        cc.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
                        for i in range(0,indentct):
                            cc.insertText(self.indentwidth)
                    break_index = line.find('break;')
                    continue_index = line.find('continue;')
                    index1 = -1
                    if break_index != -1 and line[break_index-1] == ' ':
                        index1 = break_index
                    if continue_index != -1 and line[continue_index-1] == ' ':
                        index1 = continue_index
                    if inc_count<dec_count or index1 !=-1:
                        k=1
                        
                        indentct -= 1
                        if indentct == 0:
                            QtGui.QTextEdit.keyPressEvent(self,event)
                        else:
                            QtGui.QTextEdit.keyPressEvent(self,event)
                            cc.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
                            for i in range(0,indentct):
                                cc.insertText(self.indentwidth)
                        
                    
                    if inc_count==dec_count and k !=1:
                        k=0
                                               
                        QtGui.QTextEdit.keyPressEvent(self,event)
                        cc.movePosition(QtGui.QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
                        for i in range(0,indentct):
                            cc.insertText(self.indentwidth)
                                                  
                        #if prevchar == '':
                           # QtGui.QTextEdit.keyPressEvent(self,event)
                else:
                    QtGui.QTextEdit.keyPressEvent(self,event)

            else:   
                QtGui.QTextEdit.keyPressEvent(self,event)
                if indentct < 0:
                    indentct = 0
        else:
            QtGui.QTextEdit.keyPressEvent(self,event)

        if event.key() == 16777232: #Home key has 16777232
            cc = self.textCursor()
            cc.select(QTextCursor.LineUnderCursor)
            line = cc.selectedText()
            spaces = 0
            for d in line:
                if d == ' ':
                    spaces+=1
                else:
                    break
            prev_pos = cc.position()            
            cc.movePosition(QTextCursor.StartOfLine,QTextCursor.MoveAnchor)
            maxleftposition = cc.position()+spaces
            
            if event.modifiers() == QtCore.Qt.ShiftModifier:
                cc.setPosition(prev_pos,cc.MoveAnchor)
                cc.setPosition(maxleftposition,QTextCursor.KeepAnchor)
            else:
                cc.setPosition(maxleftposition,QTextCursor.MoveAnchor)
            self.setTextCursor(cc)
            
        if self.showtooltip == True:
            
            if self.tooltip_func_index !=-1 and self.tooltip_class_index == -1:
                
                x1,y1,x2,y2 = self.cursorRect().getCoords()
                self.tooltip_x = self.mapToGlobal(QtCore.QPoint(x2,y2)).x()
                self.tooltip_y = self.mapToGlobal(QtCore.QPoint(x2,y2)).y()
                QtGui.QToolTip.showText(QtCore.QPoint(self.tooltip_x,self.tooltip_y),self.includefilefuncarray[self.tooltip_func_index],self)

            if self.tooltip_func_index !=-1 and self.tooltip_class_index != -1:

                x1,y1,x2,y2 = self.cursorRect().getCoords()
                self.tooltip_x = self.mapToGlobal(QtCore.QPoint(x2,y2)).x()
                self.tooltip_y = self.mapToGlobal(QtCore.QPoint(x2,y2)).y()
                QtGui.QToolTip.showText(QtCore.QPoint(self.tooltip_x,self.tooltip_y),self.includefilefuncarray[self.tooltip_class_index][self.tooltip_func_index],self)
            
        if event.key() == 40: #40 is for (
            cc = self.textCursor()
            cc.movePosition(cc.PreviousWord,cc.KeepAnchor,2)
            selected_text = str(cc.selectedText())
            
            if self.filetype == 'C Project' or self.filetype == 'C File':
                
                for i in range(len(self.includefilefuncarray)+1):
                    try:
                        if selected_text == self.includefilefuncarray[i][0:len(selected_text)]:
                            break
                    except:
                        pass
                if i!= len(self.includefilefuncarray):
                    self.tooltip_func_index = i
                    self.tooltip_class_index = -1
                    self.showtooltip = True
            else:
                if self.filetype == 'C++ Project' or self.filetype == 'C++ File':
                    
                    cc.movePosition(cc.PreviousWord,cc.KeepAnchor,2)
                    selected_text = unicode(cc.selectedText(),'utf-8')
                    dot_index = selected_text.find('.')                    
                    if dot_index !=-1:
                        object_name = selected_text[:dot_index]
                        func_name = selected_text[dot_index+1:]
                        index_object = self.object_namearray.index(object_name)            
                        matched_class = self.object_classarray[index_object]
                        index_class = self.includefileclassarray.index(matched_class)
                        for i in range(len(self.includefilefuncarray[index_class])+1):
                            try:
                                if self.includefilefuncarray[index_class][i].find(func_name)!=-1:
                                    break
                            except:
                                pass
                        if i!= len(self.includefilefuncarray[index_class]):
                            self.tooltip_func_index = i
                            self.tooltip_class_index = index_class
                            self.showtooltip = True
                    else:
                        scope_resolution_index = selected_text.find('::')
                        if scope_resolution_index != -1:
                            class_name = selected_text[:scope_resolution_index]
                            func_name = selected_text[scope_resolution_index+2:]                                                    
                            index_class = self.includefileclassarray.index(class_name)
                            
                            for i in range(len(self.includefilefuncarray[index_class])+1):
                                try:
                                    if self.includefilefuncarray[index_class][i].find(func_name)!=-1:
                                        break
                                except:
                                    pass
                            if i!= len(self.includefilefuncarray[index_class]):
                                self.tooltip_func_index = i
                                self.tooltip_class_index = index_class
                                self.showtooltip = True
         
        if event.key() == 41: ##41 is for )
            cc = self.textCursor()
            self.closebrackets +=1
            pos = cc.columnNumber()
            cc.select(QTextCursor.LineUnderCursor)
            line = str(cc.selectedText())
            self.indexopenbracketarray = []
            self.indexclosebracketarray = []
            index = 0
            indexopenbracket = -1
            for i in range(line.count("(")):
                index = line.find("(",index)
                self.indexopenbracketarray.append(index)
                index +=1
            index = 0
            
            if len(self.indexopenbracketarray) >0:
                for i in range(line.count(")")):
                    index = line.find(")",index)
                    self.indexclosebracketarray.append(index)
                    index +=1
                
                for i in range(line.count(")")):
                    s = line[self.indexopenbracketarray[len(self.indexopenbracketarray)-1-i]:self.indexclosebracketarray[len(self.indexclosebracketarray)-1]+1]                    
                    s1=""
                    if s.count(")") == s.count("("):
                        if pos == self.indexclosebracketarray[len(self.indexclosebracketarray)-1]+1:
                            indexopenbracket = self.indexopenbracketarray[len(self.indexopenbracketarray)-1-i]
                        else:
                            for j in range(line.count(")")):
                                if self.indexopenbracketarray[len(self.indexopenbracketarray)-1-j] <= pos:
                                    s1 = line[self.indexopenbracketarray[len(self.indexopenbracketarray)-1-j]:pos]
                                    if s1.count(")") == s1.count("("):
                                        indexopenbracket = line.index(s1)
                                        break
                        break
                if indexopenbracket != -1:                   
                    cc.movePosition(QTextCursor.StartOfLine,QTextCursor.MoveAnchor)
                    cc.movePosition(QTextCursor.NextCharacter,QTextCursor.MoveAnchor,indexopenbracket)
                    cc.movePosition(cc.PreviousWord,cc.KeepAnchor)
                    selected_text = cc.selectedText()
                    
                    if str(QtGui.QToolTip.text()).find(selected_text+'(') == 0:
                        QtGui.QToolTip.hideText()
                        self.showtooltip = False
                    cc.movePosition(QTextCursor.StartOfLine,QTextCursor.MoveAnchor)
                    cc.movePosition(QTextCursor.NextCharacter,QTextCursor.MoveAnchor,indexopenbracket)
                    cc.movePosition(QTextCursor.NextCharacter,QTextCursor.KeepAnchor,pos-indexopenbracket)
                    self.setTextCursor(cc)
                    self.removeselectedtext = False

        if event.key() == 93: ##93 is for ]            
            cc = self.textCursor()
            self.closebigbrackets +=1
            pos = cc.columnNumber()
            cc.select(QTextCursor.LineUnderCursor)
            line = str(cc.selectedText())
            self.indexopenbigbracketarray = []
            self.indexclosebigbracketarray = []
            index = 0
            indexopenbigbracket = -1
            for i in range(line.count("[")):
                index = line.find("[",index)
                self.indexopenbigbracketarray.append(index)
                index +=1
            index = 0
            if len(self.indexopenbigbracketarray) >0:
                for i in range(line.count("]")):
                    index = line.find("]",index)
                    self.indexclosebigbracketarray.append(index)
                    index +=1
                
                for i in range(line.count("]")):
                    s = line[self.indexopenbigbracketarray[len(self.indexopenbigbracketarray)-1-i]:self.indexclosebigbracketarray[len(self.indexclosebigbracketarray)-1]+1]
                    s1=""
                    if s.count("]") == s.count("["):
                        if pos == self.indexclosebigbracketarray[len(self.indexclosebigbracketarray)-1]+1:
                            indexopenbigbracket = self.indexopenbigbracketarray[len(self.indexopenbigbracketarray)-1-i]
                        else:
                            for j in range(line.count("]")):
                                if self.indexopenbigbracketarray[len(self.indexopenbigbracketarray)-1-j] <= pos:
                                    s1 = line[self.indexopenbigbracketarray[len(self.indexopenbigbracketarray)-1-j]:pos]
                                    if s1.count("]") == s1.count("["):
                                        indexopenbigbracket = line.index(s1)
                                        break
                        break
                    
                if indexopenbigbracket != -1:                   
                    cc.movePosition(QTextCursor.StartOfLine,QTextCursor.MoveAnchor)
                    cc.movePosition(QTextCursor.NextCharacter,QTextCursor.MoveAnchor,indexopenbigbracket)
                    cc.movePosition(QTextCursor.NextCharacter,QTextCursor.KeepAnchor,pos-indexopenbigbracket)
                    self.setTextCursor(cc)
                    self.removeselectedtext = False
                    
        if len(self.includefilefuncarray)!=0:            
            if event.key() == 32 or event.key() == 16777217 or event.key() == 16777220: #for Tab,space and enter key
                self.funcmatchlist.setVisible(False)
            else:            
                cc = self.textCursor()
                cc.select(QTextCursor.WordUnderCursor)
                word = str(cc.selectedText())
                self.funcmatchlist.setVisible(False)
                self.funcmatchlist.clear()
                
                if len(word)>=3:
                    if self.includefileclassarray == []:                            
                        for i in range(len(self.includefilefuncarray)):
                            if word == self.includefilefuncarray[i][0:len(word)]:
                                x1,y1,x2,y2 = self.cursorRect().getCoords()
                                self.funcmatchlist.setGeometry(x2,y2,181,151)
                                self.funcmatchlist.addItem(self.includefiledatatypearray[i] + " "+ self.includefilefuncarray[i])
                                self.funcmatchlist.setVisible(True)                       

                cc.clearSelection()
                
        #If dot . is pressed then check whether there's an object and whether it is available
        if event.key() == 46 and self.object_namearray !=[]:            
            cc = self.textCursor()
            cc.movePosition(cc.WordLeft,cc.MoveAnchor,2)
            cc.select(QTextCursor.WordUnderCursor)
            word = cc.selectedText()
            try:
                index_object = self.object_namearray.index(word)            
                matched_class = self.object_classarray[index_object]
                index_class = self.includefileclassarray.index(matched_class)
                x1,y1,x2,y2 = self.cursorRect().getCoords()
                self.funcmatchlist.setGeometry(x2,y2,181,151)
                self.funcmatchlist.clear()
                self.funcmatchlist.setVisible(True)                       
                for i in range(len(self.includefilefuncarray[index_class])):
                    self.funcmatchlist.addItem(self.includefiledatatypearray[index_class][i] + " "+ self.includefilefuncarray[index_class][i])
            except:
                pass
            
        #if scope resolution operator :: is inserted
        print self.includefileclassarray
        if event.key() == 58 and self.includefileclassarray !=[]:            

            cc = self.textCursor()
            cc.movePosition(cc.WordLeft,cc.KeepAnchor,1)
            cc.select(QTextCursor.WordUnderCursor)
            if str(cc.selectedText()) == '::':
                cc.select(QTextCursor.LineUnderCursor)
                line = cc.selectedText()
                for j in range(len(self.includefileclassarray)):
                    if self.includefileclassarray[j] in line:
                        index_class = j
                        x1,y1,x2,y2 = self.cursorRect().getCoords()
                        self.funcmatchlist.setGeometry(x2,y2,181,151)
                        self.funcmatchlist.clear()
                        self.funcmatchlist.setVisible(True)                       
                        for i in range(len(self.includefilefuncarray[index_class])):
                            self.funcmatchlist.addItem(self.includefiledatatypearray[index_class][i] + " "+ self.includefilefuncarray[index_class][i])

class codewidget(QtGui.QWidget):

    class NumberBar(QtGui.QWidget):
 
        def __init__(self, *args):
            
            QtGui.QWidget.__init__(self, *args)
            self.edit = None            
            self.highest_line = 0
 
        def setTextEdit(self, edit):
            
            self.edit = edit
 
        def update(self, *args):
            
            width = self.fontMetrics().width(str(self.highest_line)) + 4
            if self.width() != width:
                self.setFixedWidth(width)
            QtGui.QWidget.update(self, *args)
 
        def paintEvent(self, event):
            
            contents_y = self.edit.verticalScrollBar().value()
            page_bottom = contents_y + self.edit.viewport().height()
            font_metrics = self.fontMetrics()
            current_block = self.edit.document().findBlock(self.edit.textCursor().position())
            block_count = self.edit.document().blockCount()            
            painter = QtGui.QPainter(self)
            
            block =current_block
            line_count_next = block.blockNumber()
            
            while block.isValid():
                line_count_next += 1                
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()
                if position.y() >= contents_y and position.y() <=page_bottom:
                    bold = False
                    if block == current_block:
                        bold = True
                        font = painter.font()
                        font.setBold(True)
                        painter.setFont(font)
                    
                    painter.drawText(self.width() - font_metrics.width(str(line_count_next)) - 3, round(position.y()) - contents_y + font_metrics.ascent(), str(line_count_next))
                    
                    if bold:
                        font = painter.font()
                        font.setBold(False)
                        painter.setFont(font)       
            
                if position.y() > page_bottom:
                    break                
                block = block.next()
            block = current_block
            line_count_prev = block.blockNumber()+1
            
                
            while block.isValid():               
                
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()                
                if position.y() >contents_y  and position.y() <=page_bottom:
                    bold = False
                    if block == current_block:
                        bold = True
                        font = painter.font()
                        font.setBold(True)
                        painter.setFont(font)
                    
                    painter.drawText(self.width() - font_metrics.width(str(line_count_prev)) - 3, round(position.y()) - contents_y + font_metrics.ascent(), str(line_count_prev))
                    
                    if bold:
                        font = painter.font()
                        font.setBold(False)
                        painter.setFont(font)       
            
                if position.y() < contents_y:
                    break                
                block = block.previous()
                line_count_prev -= 1                    
                    
            self.highest_line = line_count_next
            painter.end()
            QtGui.QWidget.paintEvent(self, event)
            
    def __init__(self,projtype,parent=None):

        QtGui.QWidget.__init__(self,parent)
        
        self.vbox = QtGui.QVBoxLayout(self)
        self.txtInput = txtInputclass(projtype,self)        

        self.number_bar = self.NumberBar()
        self.number_bar.setTextEdit(self.txtInput)
        self.hbox_textedit = QtGui.QHBoxLayout(self)
        self.hbox_textedit.setSpacing(0)
        self.hbox_textedit.setMargin(0)
        self.hbox_textedit.addWidget(self.number_bar)
        self.hbox_textedit.addWidget(self.txtInput)
        self.widget_textedit = QtGui.QWidget(self)
        self.widget_textedit.setLayout(self.hbox_textedit)
        
        #self.vbox.addLayout(self.hbox_combo)
        self.vbox.addWidget(self.widget_textedit)
        self.vbox.setContentsMargins(0,0,0,0)
        self.vbox.setSpacing(0)        
        self.setLayout(self.vbox)
        self.txtInput.installEventFilter(self)
        self.txtInput.viewport().installEventFilter(self)
        self.parent = parent
        self.combo_funcposarray = []
        self.func_array=[]
        self.class_pos_array = []
        self.combo_class = QtGui.QComboBox(self)
        self.combo_class.hide()
        #self.show_combo_boxes(projtype)
        
    def eventFilter(self, object, event):
                
        if object in (self.txtInput, self.txtInput.viewport()):
            self.number_bar.update()
            return False
        return QtGui.QWidget.eventFilter(object, event)
 
    def getTextEdit(self):
        return self.txtInput
    
    def show_combo_boxes(self,projtype):

        if projtype != '':
            
            try:
                self.combo_widget.hide()
                del self.combo_func                
            except:
                pass
            self.hbox_combo = QtGui.QHBoxLayout(self)
            if projtype == 'C++ Project' or projtype=='C++ File':
                self.combo_class = QtGui.QComboBox(self)
                self.hbox_combo.addWidget(self.combo_class,0,QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
                self.combo_class.activated.connect(self.combo_class_item_activated)
            self.combo_func = QtGui.QComboBox(self)            
            self.combo_func.activated.connect(self.combo_func_item_activated)
            self.hbox_combo.addWidget(self.combo_func,1,QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
                
            self.combo_widget = QtGui.QWidget(self)            
            self.hbox_combo.setSpacing(5)
            self.hbox_combo.setContentsMargins(0,0,0,5)            
            self.combo_widget.setLayout(self.hbox_combo)            
            self.vbox.removeWidget(self.widget_textedit)
            self.vbox.addWidget(self.combo_widget)
            self.vbox.addWidget(self.widget_textedit)
            self.txtInput.filetype=projtype
            self.vbox.setContentsMargins(0,0,0,0)
            self.vbox.setSpacing(0)
            self.setLayout(self.vbox)
            
    def combo_class_item_activated(self,i):
        
        ####Go to class definition if available
        self.combo_func.hide()        
        self.hbox_combo.removeWidget(self.combo_func)        
        del self.combo_func
        self.combo_func = QtGui.QComboBox(self)
        self.combo_func.activated.connect(self.combo_func_item_activated)
        self.hbox_combo.addWidget(self.combo_func,1,QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        
        for j in self.func_array[i]:
            self.combo_func.addItem(j)
            
    def combo_func_item_activated(self,i):
        
        ######Go to position of function in txtinput
        cc = self.txtInput.textCursor()
        if self.combo_class.count() == 0:
            cc.setPosition(self.combo_funcposarray[i]+1,cc.MoveAnchor)            
        else:
            cc.setPosition(self.combo_funcposarray[self.combo_class.currentIndex()][i]+1,cc.MoveAnchor)
        self.txtInput.setTextCursor(cc)
        self.txtInput.highlightcurrentline()
