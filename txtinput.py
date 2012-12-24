#1849 lines
## Everything which is left to do is written in get_include_file_classes_and_members function
## Correct the regular expression for regex_arrW in fill_cpp_code_completion function
## So that gtk_container in gtk_vbox.cpp of gtk_creator project cannot be detected

from PyQt4 import QtGui
from PyQt4.Qt import QTextCursor
from PyQt4 import QtGui,QtCore 
import re
global indentct,indentTF
indentct = 0
import time,random
import includefilethread

class HiddenText(object):

    def __init__(self,text,start_pos,end_pos,new_length):

        self.text= text
        self.start_pos = start_pos
        self.length = end_pos - start_pos
        self.new_length = new_length #The length between { \n...\n }
        self.number_of_lines = text.count('\n')-2
        super(HiddenText,self).__init__()

    def set_start_pos(self,start_pos):

        self.start_pos = start_pos

    def change_start_pos(self, factor):

        self.start_pos += factor

    def get_number_of_lines(self):

        return self.number_of_lines

class TextCursor(QtGui.QTextCursor):

    def __init__(self,textCursor,parent=None):

        QtGui.QTextCursor.__init__(self,textCursor)

        self.parent = parent

    def positionWithHiddenText(self):

        return QtGui.QTextCursor.position(self)

    def blockNumberWithHiddenText(self):

        return QtGui.QTextCursor.blockNumber(self)
    
    def position(self):

        pos = self.positionWithHiddenText()
        for i,x in enumerate(self.parent.hidden_text_array):
            if x.start_pos<pos:
                pos += x.length-len('\n...\n')
                
        return pos

    def blockNumber(self):

        blockNumber = self.blockNumberWithHiddenText()
        pos = self.positionWithHiddenText()
        for i,x in enumerate(self.parent.hidden_text_array):
            if x.start_pos<pos:
                blockNumber += x.get_number_of_lines()

        return blockNumber

    def setPositionWithHiddenText(self,pos,anchor):

        QtGui.QTextCursor.setPosition(self,pos,anchor)

    def setPosition(self,pos,anchor):

        for i,x in enumerate(self.parent.hidden_text_array):
            if x.start_pos<pos:
                pos += x.length-len('\n...\n')

        self.setPositionWithHiddenText(pos,anchor)

    def setLine(self,line):

        self.setPositionWithHiddenText(0,self.MoveAnchor)
        self.movePosition(self.Down,self.MoveAnchor,line)
        pos = self.positionWithHiddenText()
        for i,x in enumerate(self.parent.hidden_text_array):
            if x.start_pos<pos:
                line -= x.get_number_of_lines()
        
        self.setPositionWithHiddenText(0,self.MoveAnchor)
        self.movePosition(self.Down,self.MoveAnchor,line-1)
        
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
        self.includefilenamearray=[]
        
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
        self.includefilethread = includefilethread.IncludeFileThread([''],self.filetype,self)
        self.connect(self.includefilethread,QtCore.SIGNAL('finished()'),self.thread_finished)
        #self.includefilethread.start()
        self.xcfr=0
        self.hidden_text_array=[]
        self.runToPlainText=0
        
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

        self.isDirty=True        

    def textCursorWithHiddenText(self):

        return QtGui.QTextEdit.textCursor(self)
    
    def textCursor(self):

        cc = QtGui.QTextEdit.textCursor(self)
        new_cc = TextCursor(cc,self)
        return new_cc
    
    def showAllText(self): ##This function will show all the hidden text

        if self.hidden_text_array==[]:
            return
        
        for i in range(len(self.hidden_text_array)-1,-1,-1):            
            start_pos = self.hidden_text_array[i].start_pos
            
            cc = self.textCursor()
            cc.setPositionWithHiddenText(start_pos,cc.MoveAnchor)
            cc.setPositionWithHiddenText(start_pos+len('\n...\n')+1,cc.KeepAnchor)
            #print unicode(cc.selectedText(),'utf-8')
            cc.removeSelectedText()
            
            cc.setPositionWithHiddenText(start_pos,cc.MoveAnchor)            
            cc.insertText(self.hidden_text_array[i].text)#.rstrip())
            
        self.hidden_text_array = []
        
    def toPlainText(self):
        
        self.showAllText()
        return super(txtInputclass,self).toPlainText()       
        
    def toPlainTextWithHidden(self):

        return super(txtInputclass,self).toPlainText()
    
    def getisDirty(self):

        return self.isDirty

    def setisDirty(self,isdirty):

        self.isDirty = isdirty
    
    def thread_finished(self):

        self.includefileclassarray += self.includefilethread.includefileclassarray
        self.includefilefuncarray += self.includefilethread.includefilefuncarray
        self.includefiledatatypearray += self.includefilethread.includefiledatatypearray
##        print self.includefilethread.includefiledatatypearray
##        print self.includefilethread.includefilefuncarray
##        print self.includefilethread.includefileclassarray
         
    def document_contents_change(self,position,charsRemoved,charsAdded):
        
        ### Here the positions of detected functions and classes will be updated
        ### Whenever the text of the document is changed
        ### And also whenever some text is removed then whether that function exists
        ### or not
        ### You can improve this algorithm by changing the positions only when cursor
        ### is moved to next line, not when every character is added or removed
        
        cc = self.textCursor()
        self.isDirty=True
        
        if charsRemoved == charsAdded:           
            return
        
        ##Position of hidden text is updated 
        for i,x in enumerate(self.hidden_text_array):
            if x.start_pos>position:
                if charsRemoved==0:
                    x.change_start_pos(charsAdded)
                else:
                    if charsAdded==0:
                        x.change_start_pos((-1)*charsRemoved)
        ##################################
                        
        s=str(self.toPlainTextWithHidden())
        
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
                                #print "%s %s::%s"%(data_type,class_name,func)
                                #if re.findall(r'\b%s\s*%s::%s'%(data_type,class_name,func),s)==[]:
                                if re.findall(r'%s::%s'%(class_name,func),s)==[]:  
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
#                        print self.parent.combo_funcposarray
#                        print current_class_index
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
        #print "cursor position changed"
        
        for i,x in enumerate(self.hidden_text_array):
            if cc.positionWithHiddenText() > x.start_pos and cc.positionWithHiddenText() < x.start_pos + x.new_length:
                cc.setPosition(x.start_pos-2,cc.MoveAnchor)
                self.setTextCursor(cc)
                break

        if self.prev_line != self.line:

            pos = cc.position()
            if self.prev_line>self.line:
                cc.movePosition(cc.Down,cc.KeepAnchor,self.prev_line-self.line)
            else:
                cc.movePosition(cc.Up,cc.KeepAnchor,self.line-self.prev_line)
            cc.select(cc.LineUnderCursor)
            line = str(cc.selectedText())
            self.new_include_file_list=[]            
            
            self.get_include_file_classes_and_members(line)
            #print self.new_include_file_list
            self.includefilethread.setfilelist(self.new_include_file_list)
            self.includefilethread.start()
                
            cc.setPosition(pos,cc.MoveAnchor)            
            
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
                    
                    if self.parent.combo_funcposarray[i] < pos:                        
                        self.parent.combo_func.setCurrentIndex(i)
                        break
                pass
            else:
                if self.filetype == 'C++ Project':
                    try:                        
                        if self.parent.combo_class.count() == 0:
                            for i in range(len(self.parent.combo_funcposarray)-1,-1,-1):
                                if self.parent.combo_funcposarray[i] < pos:
                                    self.parent.combo_func.setCurrentIndex(i)
                                    break
                        else:                            
                            min_diff= self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1][len(self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1])-1]
                            class_index=-1
                            func_index=-1
                            
                            for i in range(len(self.parent.combo_funcposarray)-1,-1,-1):
                                can_break = False
                                for j in range(len(self.parent.combo_funcposarray[i])-1,-1,-1):
                                    if self.parent.combo_funcposarray[i][j] < pos:                                       
                                        if min_diff > pos-self.parent.combo_funcposarray[i][j]:
                                            min_diff = pos -self.parent.combo_funcposarray[i][j]
                                            class_index = i
                                            func_index = j                                        
                                        break                               
                                
                            if class_index !=-1 and func_index!=-1:
                                self.parent.combo_class_item_activated(class_index)
                                self.parent.combo_class.setCurrentIndex(class_index)
                                self.parent.combo_func.setCurrentIndex(func_index)
                    except:
                        pass
                else:
                    if self.filetype == 'C++ File':
                        try:
                            if self.parent.combo_class.count() != 0:
                                for i in range(len(self.parent.combo_funcposarray)):
                                    can_break = False
                                    for j in range(len(self.parent.combo_funcposarray[i])-1,-1,-1):
                                        if self.parent.combo_funcposarray[i][j] < pos:
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

    def get_include_file_classes_and_members(self,text,file_path=''):

        ## Remember to include the library files 
        ## update the status bar to show which file it is currently at        
        
        if file_path != '':
            try:
                f = open(file_path,"r+")
                text = ''
                for s in f:
                    text += s
            except IOError:
                return
            
        regex_include_array=re.findall(r'#include+(.)+',text)
        if regex_include_array == []:
            return
        
        for search_iter in re.finditer(r'#include+(.)+',text):
            text = search_iter.group()                
            file_name = ''
            file_path = ''                
            if text.count('"') == 2:
                file_name = text[text.find('"')+1:text.rfind('"')]
                file_path = self.parent.filename
                file_path = file_path[:file_path.rfind('/')+1] + file_name                                       
            else:
                if text.count('>') == 1 and text.count('<'):
                #    file_name = text[text.find('<'):text.rfind('>')]
                    pass
            if file_path == "" or file_name == "":
                continue
            if file_path not in self.includefilenamearray:
                self.includefilenamearray.append(file_path)                 
                self.new_include_file_list.append(file_path)
                print file_path
                self.get_include_file_classes_and_members("",file_path)
                
    def fill_c_code_completion(self):

        try:
            self.document().contentsChange.disconnect(self.document_contents_change)
        except:
            pass        
        
        self.document().contentsChange.connect(self.document_contents_change)
        text = str(self.toPlainText())
        self.new_include_file_list=[]
        self.get_include_file_classes_and_members(text)
##      print self.new_include_file_list
        self.includefilethread.setfilelist(self.new_include_file_list)
        self.includefilethread.run()
        self.thread_finished()
        
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
                            #self.parent.combo_func.addItem(i+" "+d)
            for i in range(len(self.parent.combo_funcposarray)):
                for j in range(len(self.parent.combo_funcposarray)-1):
                    if self.parent.combo_funcposarray[j]>self.parent.combo_funcposarray[j+1]:
                        k = self.parent.combo_funcposarray[j+1]
                        self.parent.combo_funcposarray[j+1]=self.parent.combo_funcposarray[j]
                        self.parent.combo_funcposarray[j]=k
                        k=self.includefilefuncarray[j+1]
                        self.includefilefuncarray[j+1]=self.includefilefuncarray[j]
                        self.includefilefuncarray[j]=k
                        k=self.includefiledatatypearray[j+1]
                        self.includefiledatatypearray[j+1]=self.includefiledatatypearray[j]
                        self.includefiledatatypearray[j]=k
            for i in range(len(self.parent.combo_funcposarray)):
                self.parent.combo_func.addItem(self.includefiledatatypearray[i]+" "+self.includefilefuncarray[i])
        #print self.parent.combo_funcposarray

    def fill_cpp_code_completion(self):        
        
        text = str(self.toPlainText())
        self.new_include_file_list=[]
        self.includefileclassarray =[]
        self.includefilefuncarray =[]
        self.includefiledatatypearray =[]
        self.includefilenamearray=[]
        self.get_include_file_classes_and_members(text)
        #print self.new_include_file_list
        #print self.new_include_file_list
        
        
        self.includefilethread.setfilelist(self.new_include_file_list)
        self.includefilethread.run()
        self.thread_finished()

        
        ##There can be three cases, either there can be global functions in the file
        ## or there can be function definitions of classes
        ## or classes will be defined
        ## But these three cases are valid for projects only
        ## In a C++ File, there may be any combination of these three cases
        ## So for file let us first find the class definition and then
        ## find its functions definitions. Declaration of functions inside the
        ## class declaration will be ignored.
        ## Function definitions of classes outside the class declarations is extracted        
        print "CPP CODE COMPLETION"
        if self.filetype == 'C++ File':            
            self.parent.func_array = []            
            self.parent.combo_funcposarray=[]
            self.includefileclassarray = []
            self.parent.combo_class.clear()
            #print re.findall(r'\bclass\b\s*(\w+.+?\}\s*\;)',text,re.DOTALL)
            for class_search_iter in re.finditer(r'\bclass\b\s*(\w+.+?\}\s*\;)',text,re.DOTALL):
                class_definition = class_search_iter.group()
                class_name = ''
                
                if 'class' in class_definition:
                    if '>' in class_definition:
                        #class_definition = class_definition[class_definition.index('<')+1:]
                        pass
                    
                    class_definition = class_definition[class_definition.index('class')+len('class'):]
                    
                    class_definition = class_definition.lstrip()
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
                self.includefileclassarray.append(class_name)
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
            print self.includefileclassarray
            for i in range(len(self.includefileclassarray)):
                count = 0
                if self.includefileclassarray[i].find(')')!=-1:
                    continue
                if self.includefileclassarray[i].find('(')!=-1:
                    continue
                regex_arrW = re.findall(r'\b%s::\s*(\w\(*.*\))\s*{'%self.includefileclassarray[i],text)
                if regex_arrW!=[] or re.findall(r'\b%s::%s\(*.*\)'%(self.includefileclassarray[i],self.includefileclassarray[i]),text)!=[]:
                    #print regex_arrW
                    print "adding"+self.includefileclassarray[i]
                    self.parent.combo_class.addItem(self.includefileclassarray[i])
                    self.parent.combo_funcposarray.append([])
                    self.parent.func_array.append([])
                for search_iter in re.finditer(r'\b%s::\s*(\w\(*.*\))\s*{'%self.includefileclassarray[i],text):
                    #if count == 0:
                        #self.parent.combo_class.addItem(self.includefileclassarray[i])
                        #self.parent.combo_funcposarray.append([])
                        #self.parent.func_array.append([])
                    d = search_iter.group()
                    d = re.findall(r'::\s*(\w+.+)\s*{',d)[0]                    
                    d = d.strip()
                    if re.findall(r'(\w+.+)\s*\(',d) !=[] and self.includefileclassarray[i]==re.findall(r'(\w+.+)\s*\(',d)[0]:
                        continue
                        
                    if "(" in d and ")" in d and "=" not in d:
                        self.parent.func_array[len(self.parent.func_array)-1].append(d)
                        self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1].append(search_iter.start())
                    count +=1
                    contains_class_functions = True
                ##For constructor
                for search_iter in re.finditer(r'\b%s::%s\(*.*\)'%(self.includefileclassarray[i],self.includefileclassarray[i]),text):
                    d = search_iter.group()
                    d = d[d.index('::')+2:]
                    d=d.strip()
                    k=0
                    for j in range(len(self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1])):
                        if search_iter.start()<self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1][j]:
                            k=j                            
                            break
                    self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1].insert(k,search_iter.start())
                    self.parent.func_array[len(self.parent.combo_funcposarray)-1].insert(k,d)
                #For Destructor
                for search_iter in re.finditer(r'\b%s::~%s\(\)'%(self.includefileclassarray[i],self.includefileclassarray[i]),text):
                    d = search_iter.group()
                    d = d[d.index('::')+2:]                    
                    d=d.strip()
                    k=0
                    for j in range(len(self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1])):
                        if search_iter.start()<self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1][j]:
                            k=j                            
                            break
                    self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1].insert(k,search_iter.start())
                    self.parent.func_array[len(self.parent.combo_funcposarray)-1].insert(k,d)
                    contains_class_functions = True
                
                
                #print self.parent.func_array
                #print self.parent.combo_funcposarray
            #print self.parent.combo_funcposarray
            #print self.parent.func_array
            ##########################################
            count = 0
            ####For file containing class definition
            if contains_class_functions==False:
                self.contains_class_definitions = False
                ##Here no substring found could be removed, because it will change the
                ##position so I thought of replacing the sub string with the same length
                ##of a string containing only spaces.
                for class_search_iter in re.finditer(r'\bclass\b\s*(\w+.+?\}\s*\;)',text,re.DOTALL):
                    self.contains_class_definitions = True
                    class_definition = class_search_iter.group()
                    
                    self.parent.func_array.append([])
                    self.parent.combo_funcposarray.append([])
                    #print class_definition
                    
                    if 'class' in class_definition:                        
                        
                        class_definition = class_definition.replace('class','    ',1)
                        if re.findall(r'>\s*\bclass\b\s*\w+',class_definition)!=[]:
                        
                            class_definition = class_definition.replace('>',' ',1)
                            ###code to complete the class definition containing enum, class or struct
                            count = len(re.findall(r'\benum\b',class_definition)) + len(re.findall(r'\bclass\b',class_definition)) + len(re.findall(r'\bstruct\b',class_definition))
                            count -= len(re.findall(r'\}\s*;',class_definition))
                            i=0
                            while(count>0):
                                class_definition += re.findall(r'(?<=\}\;)\s*\w+.+?(?=\}\;)',text,re.DOTALL)[i]+'};'
                                count = len(re.findall(r'\benum\b',class_definition)) + len(re.findall(r'\bclass\b',class_definition)) + len(re.findall(r'\bstruct\b',class_definition))
                                count -= len(re.findall(r'\}\s*;',class_definition))                            
                                i+=1
                            class_name = re.findall(r'\bclass\b\s*(\w+)',class_definition)[0]                        
                        else:
                            ###code to complete the class definition containing enum, class or struct
                            count = len(re.findall(r'\benum\b',class_definition)) + len(re.findall(r'\bclass\b',class_definition)) + len(re.findall(r'\bstruct\b',class_definition))
                            count -= len(re.findall(r'\}\s*;',class_definition))
                            i=0
                            while(count>0):
                                class_definition += re.findall(r'(?<=\}\;)\s*\w+.+?(?=\}\;)',text,re.DOTALL)[i]+'};'
                                count = len(re.findall(r'\benum\b',class_definition)) + len(re.findall(r'\bclass\b',class_definition)) + len(re.findall(r'\bstruct\b',class_definition))
                                count -= len(re.findall(r'\}\s*;',class_definition))                            
                                i+=1 
                            class_name = re.findall(r'\s*(\w+)',class_definition)[0]
                    else:
                        class_name = ''
                        for j in class_definition:
                            if j == '\n' or j== '{' or j == ':' or j==' ':
                                break
                            else:
                                class_name = class_name + j
                    self.parent.combo_class.addItem(class_name)

                    class_definition = class_definition.replace('{',' ',1)
                    ##Converting all class,enums and structs definitions to spaces
                    class_definition_new = ""
                    end=0
                    for search_iter in re.finditer(r'\bclass\b\s*(\w+.+?\}\s*\;)',class_definition,re.DOTALL):
                        i=search_iter.start()
                        s=''
                        while i<search_iter.end():
                            s +=' '
                            i+=1                        
                        class_definition_new+=class_definition[end:search_iter.start()] + s
                        end=search_iter.end()
                    class_definition_new+=class_definition[end:]                
                    class_definition = class_definition_new
                    
                    class_definition_new = ""
                    end=0
                    for search_iter in re.finditer(r'\benum\b(.+?\}\s*\;)',class_definition,re.DOTALL):
                        i=search_iter.start()
                        s=''
                        while i<search_iter.end():
                            s +=' '
                            i+=1
                        class_definition_new+=class_definition[end:search_iter.start()]
                        end=search_iter.end()
                    class_definition_new+=class_definition[end:]
                    class_definition = class_definition_new                    

                    class_definition_new = ""
                    end=0
                    for search_iter in re.finditer(r'\bstruct\b\s*(\w+.+?\}\s*\;)',class_definition,re.DOTALL):
                        i=search_iter.start()
                        s=''
                        while i<search_iter.end():
                            s +=' '
                            i+=1
                        class_definition_new+=class_definition[end:search_iter.start()]
                        end=search_iter.end()
                    class_definition_new+=class_definition[end:]
                    class_definition = class_definition_new

                    ##Converting all inline functions body to whitespaces and inserting
                    ##a ; after all functions
                    ##This code has to be changed to work according to as defined
                    inline_function=""
                    bracket_array=[('{',i.start()) for i in re.finditer(r'\{',class_definition)]
                    bracket_array+=[('}',j.start()) for j in re.finditer(r'\}',class_definition)]                    
                    
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
                        a=bracket_array[0][1]
                        s=''
                        while a<n:
                            s +=' '
                            a+=1
                        class_definition_new += s
                        bracket_array = bracket_array[j+1:]
                    if bracket_array !=[]:
                        class_definition_new +=class_definition[n:bracket_array[len(bracket_array)-1][1]]
                    else:
                        class_definition_new+=class_definition[n:]
                    class_definition = class_definition_new                   
                  
                    ##Finding out all the members
                    for search_iter in re.finditer(r'\s+(.+\w+.+)\s*?\;',class_definition):
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
                                self.parent.func_array[len(self.parent.func_array)-1].append(((d.rstrip()).lstrip()).replace('\n',''))
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
        ###For getting created objects
        object_array = []
        class_array = []
        
        for class_name in self.includefileclassarray+[str(self.parent.combo_class.itemText(i)) for i in range(self.parent.combo_class.count())]:
            if class_name.find(')')!=-1:
                continue
            if class_name.find('(')!=-1:
                continue
            #print class_name
            for object_name in re.findall(r'\b%s\b\s*(\w+.+)\s*?\;'%class_name,text):
                for j in object_name.split(','):
                    object_array.append(j)
                    class_array.append(class_name)
        self.object_classarray = class_array
        self.object_namearray = object_array
        try:
            self.document().contentsChange.disconnect(self.document_contents_change)
        except:
            pass
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

        try:
            self.document().contentsChange.disconnect(self.document_contents_change)
        except:
            pass
        
        cc = self.textCursor()        
        cc.select(cc.LineUnderCursor)        
        self.setTextCursor(cc)       
        self.document().contentsChange.connect(self.document_contents_change)
        
    def setTextVisible(self,start_pos,end_pos):

        ## Here start_line and end_line are zero based, i.e. their smallest value can be 0 not 1

        try:
            self.document().contentsChange.disconnect(self.document_contents_change)
        except:
            pass        
        if end_pos == -1:
            text = str(self.toPlainTextWithHidden())[start_pos:]
            bracket_array=[('{',i.start()) for i in re.finditer(r'\{',text)]
            bracket_array+=[('}',j.start()) for j in re.finditer(r'\}',text)]                    

            _start_pos = start_pos
            start_pos += bracket_array[0][1]+1
            
            for i in range(len(bracket_array)):
                for k in range(len(bracket_array)-1):
                    if bracket_array[k][1]>bracket_array[k+1][1]:
                        o=bracket_array[k+1]
                        bracket_array[k+1]=bracket_array[k]
                        bracket_array[k]=o

            count = 0
            i=0
            for i,x in enumerate(bracket_array):
                if x[0]=='{':
                    count +=1
                else:
                    if x[0]== '}':
                        count -=1
                if count == 0:
                    break
            
            end_pos = _start_pos+bracket_array[i][1]-1
            text = text[:bracket_array[i][1]]
            end_pos = text.rfind('\n')+_start_pos+1          
            
        cc = self.textCursorWithHiddenText()

        cc.setPosition(start_pos,cc.MoveAnchor)        
        cc.setPosition(end_pos,cc.KeepAnchor)
        
        s = cc.selectedText()
        s = s.trimmed()
        
        self.runToPlainText=0
        if s.contains('...')==True and s.contains('}')== False:
            ##Then show the hidden text and pop it out from array
            if self.hidden_text_array !=[]:
                
                for i,x in enumerate(self.hidden_text_array):
                    if x.start_pos == start_pos:                    
                        break
              
                cc.removeSelectedText()
                cc.deleteChar()
                try:
                    self.hidden_text_array.remove(self.hidden_text_array[i])
                except:
                    pass
                
                cc.insertText(x.text)            
        else:
            ##Add the text in the array            
            cc.setPosition(end_pos,cc.MoveAnchor)
            cc.select(cc.LineUnderCursor)
            new_length = cc.selectedText().length()+len('\n...\n')
            cc.setPosition(start_pos,cc.MoveAnchor)
            cc.setPosition(end_pos,cc.KeepAnchor)
            
            hidden_text_object = HiddenText(str(self.toPlainTextWithHidden())[start_pos:end_pos+1],start_pos,end_pos,new_length)            
            self.hidden_text_array.append(hidden_text_object)
            cc.removeSelectedText()
            cc.insertText('\n...\n')

        self.document().contentsChange.connect(self.document_contents_change)
    
    def keyPressEvent(self,event):

        global indentct
        cc = self.textCursor()
        prev_pos = cc.position()
        if self.removeselectedtext == False:            
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
                            if self.filetype == 'C++ Project' and '.h' in self.parent.filename:                            
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
                            if d == ':':
                                if line.count(d) == 1:
                                    inc_count += 1
                            else:
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
            
            cc.movePosition(QTextCursor.StartOfLine,QTextCursor.MoveAnchor)
            maxleftposition = cc.position()+spaces
            cc.clearSelection()
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
        ##Show a list of all the matches for the object or function or class
                    
        if len(self.includefilefuncarray)!=0:            
            if event.key() == 32 or event.key() == 16777217 or event.key() == 16777220: #for Tab,space and enter key
                self.funcmatchlist.setVisible(False)
            else:            
                cc = self.textCursor()
                cc.select(QTextCursor.WordUnderCursor)
                word = str(cc.selectedText())
                self.funcmatchlist.setVisible(False)
                self.funcmatchlist.clear()
                
                if len(word)>=2:
                    if self.includefileclassarray == []: ##For C Project, C Files and C++ Files with only global functions, because they will not contain any classes
                        for i in range(len(self.includefilefuncarray)):
                            if word == self.includefilefuncarray[i][0:len(word)]:
                                x1,y1,x2,y2 = self.cursorRect().getCoords()
                                self.funcmatchlist.setGeometry(x2,y2,181,151)
                                self.funcmatchlist.addItem(self.includefiledatatypearray[i] + " "+ self.includefilefuncarray[i])
                                self.funcmatchlist.setVisible(True)
                    else:      ##For C++ Projects and C++ Files
                        for i in range(len(self.includefileclassarray)):
                            if word == self.includefilefuncarray[i][0:len(word)]:
                                x1,y1,x2,y2 = self.cursorRect().getCoords()
                                self.funcmatchlist.setGeometry(x2,y2,181,151)
                                self.funcmatchlist.addItem(includefileclassarray)
                                self.funcmatchlist.setVisible(True)
                        ### Don't forget to add scope rule for objects
                        for i in range(len(self.object_namearray)):
                            if word == self.object_namearray[i][0:len(word)]:
                                x1,y1,x2,y2 = self.cursorRect().getCoords()
                                self.funcmatchlist.setGeometry(x2,y2,181,151)
                                self.funcmatchlist.addItem(self.object_namearray)
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

class CodeRect(object):

    def __init__(self,x1,y1,x2,y2,start_pos,end_pos):

        self.x1=x1
        self.y1 = y1
        self.x2=x2
        self.y2=y2
        self.start_pos = start_pos
        self.end_pos = end_pos
        super(CodeRect,self).__init__()

    def is_point_inside(self,x,y):

        if x > self.x1 and x < self.x2:
            if y > self.y1 and y < self.y2:
                return True
        return False
        
class codewidget(QtGui.QWidget):

    class NumberBar(QtGui.QWidget):
 
        def __init__(self, parent= None, *args):
            
            QtGui.QWidget.__init__(self, parent,*args)
            self.edit = None            
            self.highest_line = 0
            self.rect_array = []
            self.parent = parent
            self.first_color = QtGui.QColor(0,0,0)
            
        def setTextEdit(self, edit):
            
            self.edit = edit
            
        def mouseReleaseEvent(self, mouse_event):

            inside_rect_array=[]
            
            for i,x in enumerate(self.rect_array):                                
                if x.is_point_inside(mouse_event.x(),mouse_event.y())==True:
                    inside_rect_array.append(x)
                    
            smallest_one = inside_rect_array[0]
            min_height=inside_rect_array[0].y2-inside_rect_array[0].y1
            for i,x in enumerate(inside_rect_array):
                if min_height > x.y2-x.y1:
                    print min_height
                    min_height=x.y2-x.y1
                    smallest_one = x
            
            self.edit.setTextVisible(smallest_one.start_pos,smallest_one.end_pos)           
            QtGui.QWidget.mouseReleaseEvent(self,mouse_event)
            
        def update(self, *args):
            
            width = self.fontMetrics().width(str(self.highest_line)) + 7
            if self.width() != width:
                self.setFixedWidth(width)
            QtGui.QWidget.update(self, *args)
 
        def paintEvent(self, event):
            
            contents_y = self.edit.verticalScrollBar().value()
            page_bottom = contents_y + self.edit.viewport().height()
            font_metrics = self.fontMetrics()
            current_block = self.edit.document().findBlock(self.edit.textCursorWithHiddenText().position())
            block_count = self.edit.document().blockCount()            
            painter = QtGui.QPainter(self)

            block = current_block
            line_count_prev = block.blockNumber()+1            
                
            while block.isValid():               
                
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()                            
                if position.y() < contents_y:
                    break                
                block = block.previous()               
                
            if not block.isValid():
                block = self.edit.document().findBlock(0)
            line_count_next = block.blockNumber()
            count = 0
            drawLine = False
            x1 = -1
            y1 = -1
            x2 = -1
            y2 = -1
            
            begining_block= block
            self.rect_array = []
            self.added_array=[]
            stack_point = []
            stack_begining_block=[]
            position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()
            last_used_color = self.first_color
            
            while block.isValid() and position.y() <= page_bottom:
                
                line_count_next += 1                
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()

                if position.y() >= contents_y and position.y() <=page_bottom:
                    bold = False
                    
                    ##For updating line numbers
                    for i,x in enumerate(self.parent.txtInput.hidden_text_array):
                        if block.position()>x.start_pos and i not in self.added_array:
                            self.added_array.append(i)
                            line_count_next += x.get_number_of_lines()
                    #########################
                    pen = painter.pen()
                    pen.setColor(self.first_color)
                    painter.setPen(pen)
                    if block == current_block:
                        bold = True
                        font = painter.font()
                        font.setBold(True)
                        painter.setFont(font)
                    painter.drawText(1, round(position.y()) - contents_y + font_metrics.ascent(), str(line_count_next))
                    
                    if bold:
                        font = painter.font()
                        font.setBold(False)
                        painter.setFont(font)

                    line = str(block.text())                    
                        
                    count += line.count('{') - line.count('}')
                    
                    if count == 0:
                        last_used_color = self.first_color
                        
                    if count <0:
                        
                        count = 0
                        last_used_color = self.first_color
                        block = block.next()
                        continue
                    
                    if line.find('{')!=-1:
                        if x2 != -1 and y2 !=-1:
                            pass
                            
                        #drawLine = True
                        stack_begining_block.append(block)
                        stack_point.append((0,round(position.y()) - contents_y)) # font_metrics.ascent()                                            
                    
                    if line.find('}')!=-1:                        
                        x2 = self.width()
                        y2 = round(position.y()) - contents_y + font_metrics.ascent()
                        pen = painter.pen()
                        pen.setWidth(2)                        
                        last_used_color = QtGui.QColor(random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))                        
                        pen.setColor(last_used_color)
                        painter.setPen(pen)                        

                        x1,y1 = stack_point.pop()
                        painter.drawLine(x1,y1,x2,y1)
                        painter.drawLine(x1,y1,x1,y2)
                        painter.drawLine(x1,y2,x2,y2)
                        begining_block = stack_begining_block.pop()
                        begining_text = str(begining_block.text())
                        self.rect_array.append(CodeRect(0,y1,x2,y2,begining_block.position()+begining_text.find('{')+1,block.position()))
                        
                block = block.next()
                
            while count > 0:
                x1,y1 = stack_point.pop()
                begining_block = stack_begining_block.pop()
                begining_text = str(begining_block.text())
                
                pen = painter.pen()
                pen.setWidth(2)
                painter.setPen(pen)        
                x2 = self.width()
                y2 = round(position.y()) - contents_y + font_metrics.ascent() 
                painter.drawLine(x1,y1,x2,y1)
                painter.drawLine(x1,y1,x1,y2)
                painter.drawLine(x1,y2,x2,y2)
                ##Here, remember the position of first character of block
                ##will be passed not 1+position of {
                self.rect_array.append(CodeRect(0,y1,x2,y2,begining_block.position(),-1)) 
                count -=1
                
            self.highest_line = line_count_next
            painter.end()
            QtGui.QWidget.paintEvent(self, event)
            
    def __init__(self,projtype,parent=None):

        QtGui.QWidget.__init__(self,parent)
        
        self.vbox = QtGui.QVBoxLayout(self)
        self.txtInput = txtInputclass(projtype,self)        

        self.number_bar = self.NumberBar(self)
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
        self.i=0
        self.filename=""
        
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
            self.i+=1
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
        cc = self.txtInput.textCursorWithHiddenText()
        #print self.combo_funcposarray
        if self.combo_class.count() == 0:
            pos = self.combo_funcposarray[i]+1            
        else:
            pos = self.combo_funcposarray[self.combo_class.currentIndex()][i]+1

        for i,x in enumerate(self.txtInput.hidden_text_array):
            if x.start_pos < pos:
                pos -= x.length-len('\n...\n')
                
        cc.setPosition(pos,cc.MoveAnchor)
        #print "GOING AT %i"%(pos)
        self.txtInput.setTextCursor(cc)
        self.txtInput.highlightcurrentline()        
