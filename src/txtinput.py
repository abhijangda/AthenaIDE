#1849 lines
## Correct Adding functions also
## print at 405
## if a class definition contains objects, in a CPP
## for C struct in C File/Project and C++ class self.includeclassarray is used

from PyQt4 import QtGui
from PyQt4.Qt import QTextCursor
from PyQt4 import QtGui,QtCore 
import re,os
global indentct,indentTF
indentct = 0
import time,random
import includefilethread
from number_bar_widget import *
from breakpoints_bar import *
from c_cpp_types import *
from helper_functions import *

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
        
        self.includefilenamearray = []
        self.includefilefuncarray = []
        self.includefiletypedefarray = []
        
        global_scope = CPPClass()
        global_scope.name="Global Scope"
        self.includefileclassarray = []
        
        self.curr_file_class_array=[]
        self.curr_file_func_array = []

        self.list_objects=[]
        self.list_pointers = []
        self.list_references = []
        
        self.tooltip_stack=[]
        
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
        self.main_win = parent.parent
        
        self.setFont(QtGui.QFont("Courier 10 Pitch", 10))

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

    def setFileType(self,filetype):

        self.filetype = filetype
        self.includefilethread.filetype=filetype
        
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
        #print 'thread finished'
        #print self.includefileclassarray
        self.includefilefuncarray += self.includefilethread.includefilefuncarray
        self.includefiletypedefarray += self.includefilethread.list_typedef

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
                        
        s=unicode(self.toPlainTextWithHidden(),'utf-16',errors='ignore')
        
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
##                        for d in str(self.includefilefuncarray[start_index-1]):
##                            if d == '*' or d == '(' or d==')'or d=='[' or d==']':
##                                func += '\\'+d
##                            else:
##                                func += d
##                        #data_type = self.includefiledatatypearray[start_index-1]
##                        
##                        if re.findall(r'\b%s\s*%s'%(data_type,func),s)==[]:
##                            del self.includefilefuncarray[start_index-1]
##                            del self.includefiledatatypearray[start_index-1]
##                            del self.parent.combo_funcposarray[start_index-1]
##                            self.parent.combo_func.removeItem(start_index-1)
                        
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
                        start_index=current_class_index
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
            line = unicode(cc.selectedText(),'utf-8',errors='ignore')
            new_include_file_list=[]                        
            self.get_include_file_classes_and_members(line,new_include_file_list)
            #print new_include_file_list
            if new_include_file_list == self.includefilethread.includefileslist:
                #print 'llll'
                #print self.includefilethread.includefileslist
                #print new_include_file_list
                self.includefilethread.setfilelist(new_include_file_list)
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
                try:
                    current_index = self.parent.combo_func.currentIndex()
                    for i in range(len(self.parent.combo_funcposarray)-1,-1,-1):
                        
                        if self.parent.combo_funcposarray[i] < pos:                  
                            self.parent.combo_func.setCurrentIndex(i)
                            if i!=current_index:
                                self.parent.find_curr_func_objects()
                            break
                except AttributeError:
                    pass
                
                
            elif self.filetype == 'C++ Project' or self.filetype=="C++ File":
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
                self.parent.find_curr_func_objects()
            
        self.prev_line = self.line

    def get_include_file_classes_and_members(self,text,new_include_file_list=[],file_path=''):

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
                file_path = os.path.join (file_path[:file_path.rfind('/')+1],
                                          file_name)
            else:
                if text.count('>') == 1 and text.count('<'):
                #    file_name = text[text.find('<'):text.rfind('>')]
                    pass
            if file_path == "" or file_name == "":
                continue
            
            if file_path not in self.includefilenamearray:
                self.includefilenamearray.append(file_path)                 
                new_include_file_list.append(file_path)                
                self.get_include_file_classes_and_members("",new_include_file_list,file_path)
                
    def fill_c_code_completion(self):
        
        if self.filetype == 'C Project' or self.filetype == 'C File':                
            try:
                self.document().contentsChange.disconnect(self.document_contents_change)
            except:
                pass        
            #print 'C1'    
            self.document().contentsChange.connect(self.document_contents_change)
            text = unicode(self.toPlainText(),'utf-8',errors='ignore')
            #text = str(self.toPlainText())
            #print 'C2'
            self.new_include_file_list=[]
            self.includefilenamearray = []
            new_include_file_list=[]
            self.includefilefuncarray = []
            self.includefiletypedefarray = []
            self.includefileclassarray = []
            self.get_include_file_classes_and_members(text,new_include_file_list)
            #print new_include_file_list
            self.includefilethread.setfilelist(new_include_file_list)
            self.includefilethread.run()
            self.thread_finished()
            self.curr_file_func_array = []
            self.curr_file_typedef_array = []
            self.parent.combo_funcposarray=[]
            self.parent.combo_func.clear()

            cpp_reg_array = re.findall(r'\bstruct\b\s*\w+.+?\}\s*\;',text,re.DOTALL)
            text_copy = text
            
            if cpp_reg_array!=[]:
                for class_definition in cpp_reg_array:
                    
                    if class_definition.count('{')>class_definition.count('}'):
                        regex_array = re.findall(r'(?<=\}\;)\s*\w+.+?(?=\}\;)',text_copy,re.DOTALL)
                        count = class_definition.count('{')-class_definition.count('}')
                        i=0
                        while count>0 and i<len(regex_array):
                           class_definition += regex_array[i] + '};'
                           count = class_definition.count('{')-class_definition.count('}')

                    class_definition = class_definition[class_definition.find('struct'):]

                    text_copy = text_copy.replace(class_definition,'')

                    c_struct = CStruct()
                    c_struct.createFromDeclaration(class_definition)
                    self.curr_file_class_array.append(c_struct)

            for struct in self.includefileclassarray + self.curr_file_class_array:

                d = re.findall(r'\btypedef\s+%s\s+.+'%struct.getDeclaration(),text)
                for s in d:
                    s = s.replace(';','')
                    typedef = CTypedef()
                    typedef.createFromDeclaration(s)
                    typedef.typedef_with = struct
                    struct.list_typedef.append(typedef)
                    self.curr_file_typedef_array.append(struct)
                    
            for search_iter in re.finditer(r'\w+[\s*\*]*\s+[\s*\*]*\w+\s*\(.*\s*.*\)\s*?{',text):
                    
                    d = search_iter.group()

                    if d.find('\n')!=-1:
                        d = d[:d.rfind('\n')]
                    
                    func = CFunction()
                    func.createFromDeclaration(d)
                    
                    if isThisAFunction(d)==False:
                        print 'lll'
                        continue
                    
                    should_continue = False
                    for _func in self.includefilefuncarray:
                        if _func.isEqualTo(func)==True:
                            should_continue = True
                            break
                    if should_continue==True:
                        continue                       
                    
                    self.curr_file_func_array.append(func)                    
                    self.parent.combo_funcposarray.append(search_iter.start())
                    
            for i in range(len(self.parent.combo_funcposarray)):
                self.parent.combo_func.addItem(self.curr_file_func_array[i].getDeclaration())
        #print self.parent.combo_funcposarray

    def fill_combo_boxes(self,_class):

        text = str(self.toPlainText())
        if _class == None:
            for __class in self.curr_file_class_array:
                self.fill_combo_boxes(__class)
        else:            
            for _var in _class.list_public_members+_class.list_private_members+_class.list_protected_members:
                for search_iter in re.search_iter(r'%s'%(getRegExpString(_var.type)+'\s*' +
                                                         getRegExpString(_var.return_type)+'\s*'+
                                                         getRegExpString(_var.name)),text):
                    self.parent.combo_funcposarray.append((search_iter.start()+search_iter.end())/2)

            for nested_class in _class.list_nested_class_structs:
                self.fill_combo_boxes(nested_class)
                
    def fill_cpp_code_completion(self):        
        
        text = str(self.toPlainText())
        full_text = text
        self.new_include_file_list=[]
        self.includefileclassarray =[]      
        self.includefilenamearray=[]
        self.new_include_file_list=[]
        new_include_file_list=[]
        self.get_include_file_classes_and_members(text,new_include_file_list)
        
        self.includefilethread.setfilelist(new_include_file_list)       
        self.includefilethread.run()
        self.thread_finished()
       
        if self.filetype == 'C++ File' or self.filetype == 'C++ Project':
            
            self.parent.combo_class.clear()
            self.parent.func_array = [[]]      
            self.parent.combo_funcposarray=[[]]
            global_scope = CPPClass()
            global_scope.name="Global Scope"            
            self.curr_file_class_array=[global_scope]
            self.curr_file_func_array = []
            self.parent.combo_class.addItem(self.curr_file_class_array[0].name)            
            
            ##Find all the class definitions and fill them in the array
            for class_search_iter in re.finditer(r'[\btemplate\s*<class\s+\w+\s*>]*\bclass\b\s*\w+.+?\}\s*\;',text,re.DOTALL):
                class_definition = class_search_iter.group()

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
                cpp_class.createFromDeclaration(class_definition)
                self.curr_file_class_array.append(cpp_class)

            for _class in self.includefileclassarray+self.curr_file_class_array:
                ###Member functions defined will be displayed
                class_name = _class.name                
                count = 0
                
                for search_iter in re.finditer(r'\w+\s+%s::+.+\(.*\)\s*{'%(class_name),text):
                    
                    d = search_iter.group()
                    
                    if d.find('\n') != -1:
                        if d.find('{') > d.find('\n'):
                            d = d[d.find('::')+2:d.find('\n')]
                        if d.find('{') < d.find('\n'):
                            d = d[d.find('::')+2:d.find('{')]
                    else:
                        d = d[d.find('::')+2:d.find('{')]

                    if d.count('(')>1:
                        continue
                    
                    if "(" in d and ")" in d and "=" not in d:
                        if count ==0:
                            self.parent.combo_class.addItem(class_name)
                            self.parent.combo_funcposarray.append([])
                            self.parent.func_array.append([])
                        self.parent.func_array[len(self.parent.func_array)-1].append(d)
                        self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1].append(search_iter.start())
                        count +=1                
                
                ##For constructor
                for search_iter in re.finditer(r'\b%s::%s\s*\(.*\)'%(class_name,class_name),text):
                    
                    d = search_iter.group()                    
                    d = d[d.index('::')+2:]
                    d=d.strip()
                    k=0
                    for j in range(len(self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1])):
                        if search_iter.start()<self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1][j]:
                            k=j                            
                            break
                    if count ==0:
                        self.parent.combo_class.addItem(class_name)
                        self.parent.combo_funcposarray.append([])
                        self.parent.func_array.append([])
                    count +=1
                    self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1].insert(k,search_iter.start())
                    self.parent.func_array[len(self.parent.combo_funcposarray)-1].insert(k,d)
                #For Destructor
                for search_iter in re.finditer(r'\b%s::~%s\(\)'%(class_name,class_name),text):
                    d = search_iter.group()
                    d = d[d.index('::')+2:]                    
                    d=d.strip()
                    k=0
                    for j in range(len(self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1])):
                        if search_iter.start()<self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1][j]:
                            k=j                            
                            break
                    if count ==0:
                        self.parent.combo_class.addItem(class_name)
                        self.parent.combo_funcposarray.append([])
                        self.parent.func_array.append([])
                    count +=1
                    self.parent.combo_funcposarray[len(self.parent.combo_funcposarray)-1].insert(k,search_iter.start())                    
                    self.parent.func_array[len(self.parent.combo_funcposarray)-1].insert(k,d)            
                    
            ##For Global functions       
            for search_iter in re.finditer(r'\w+[\s*\*]*\s+[\s*\*]*\w+\s*\(.*\s*.*\)\s*?{',text):                
                d = search_iter.group()                
                d = d[:d.rfind('{')]
                d = d.strip()
                
                if "(" in d and ")" in d and "=" not in d and '::' not in d: 
                    func = CFunction()
                    func.createFromDeclaration(d)
                    self.curr_file_class_array[0].list_public_members.append(func)
                    self.parent.combo_funcposarray[0].append(search_iter.start())
                    self.parent.func_array[0].append(func.getDeclaration())
            
            ############################################
            ###Linking base classes with child classes
            for _class in (self.includefileclassarray + self.curr_file_class_array):
                for __class in (self.includefileclassarray + self.curr_file_class_array):
                    for base_class_name in _class.list_public_base_classes_name:
                        if base_class_name == __class.name:
                            _class.list_public_base_classes.append(__class)
                    for base_class_name in _class.list_private_base_classes_name:
                        if base_class_name == __class.name:
                            _class.list_private_base_classes.append(__class)                    

            ##Link gtkmm classes here
                            
        ##For getting created objects in class definition
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
            print text
            for i in range (len (self.tooltip_stack) -1, 0, -1):
               if isinstance (self.tooltip_stack [i], tuple) == False:                    
                    del self.tooltip_stack [i]
            
            self.tooltip_stack.insert(0,text)
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
                if space_rindex == -1:
                    space_rindex = 0
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
            
            hidden_text_object = HiddenText(unicode(self.toPlainTextWithHidden(),'utf-8',errors='ignore')[start_pos:end_pos+1],start_pos,end_pos,new_length)            
            self.hidden_text_array.append(hidden_text_object)
            cc.removeSelectedText()
            cc.insertText('\n...\n')

        self.document().contentsChange.connect(self.document_contents_change)

    #This function returns a tuple (pos, line_no, full_pos)
        
    def get_matching_bracket_pos (self, open_bracket, close_bracket):

        cc = self.textCursor()            
        pos = cc.columnNumber()
        curr_pos = cc.position ()
        last_pos = curr_pos
        
        cc.select(QTextCursor.LineUnderCursor)
        line = str(cc.selectedText())
        if close_bracket == '};':
            close_bracket = '}'
            pos1 = line.find ('}') + 1
            last_pos -= pos - pos1
            pos = pos1

        line_no = cc.blockNumber ()
        
        last_line = line_no
        open_count = 0
        close_count = 0
        
        #Trying to implement do while loop here
        while True:
            
            pos -= 1
            last_pos -=1
            
            if pos < 0:                
                if line_no == 0:
                    break
                cc.movePosition (cc.Up)
                last_pos -=1
                cc.select (QTextCursor.LineUnderCursor)
                line = str (cc.selectedText ())
                cc.movePosition (cc.EndOfLine)
                pos = cc.columnNumber () - 1
                line_no = cc.blockNumber ()
                if pos == -1: #To Handle case if line contains nothing
                    continue  #then pos becomes -1

            if line[pos] == open_bracket:
                open_count += 1
            elif line[pos] == close_bracket:
                close_count += 1

            if open_count == close_count:
                break
        pos +=1
        last_pos +=1
        if pos !=-1 and open_count == close_count:

            return (pos, line_no, last_pos)

        return (-1, -1, -1)
    
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

        if event.modifiers () != QtCore.Qt.NoModifier and event.key() != 40 and event.key() != 41 and event.key () != 93:
            QtGui.QTextEdit.keyPressEvent(self,event)
            return

        if self.funcmatchlist.isVisible () == True:
            if event.modifiers () != QtCore.Qt.NoModifier: #Qt.NoModifiers
                self.funcmatchlist.setVisible (False)

            elif event.key () == 16777237: #For Down key
                self.funcmatchlist.setCurrentRow (
                    self.funcmatchlist.currentRow () + 1)
                return
              
            elif event.key () == 16777235: #For Up key                
                self.funcmatchlist.setCurrentRow (
                    self.funcmatchlist.currentRow () - 1)
                return
            
            elif event.key () == 16777216: #For Esc key
                self.funcmatchlist.setVisible (False)
                return
            
            elif event.key () == 16777217: #For Tab Key
                self.funcmatchlistdoubleclicked (
                    self.funcmatchlist.currentItem ())
                return
            
            else:
                #funcmatchlist should be invisible if any other key is pressed
                self.funcmatchlist.setVisible (False)

        if event.key() == 16777217 and not self.funcmatchlist.isVisible ():# and self.parent.parent.spacesontabs == "True": #For Tab Key
            self.textCursor().insertText("    ")
            return
            
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
                
        if self.indentTF == 'True' or self.indentTF==True:
            if (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter)and indentct>=0:
                
                cc = self.textCursor()                
                #cc.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
                cc.movePosition(QTextCursor.StartOfLine,QTextCursor.KeepAnchor)
                line = str(cc.selectedText())                
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
                        curr_pos = cc.position ()
                        pos, line_no, last_pos = -1, -1, -1
                        if line.find ('};') == -1:
                            pos, line_no, last_pos = self.get_matching_bracket_pos \
                                                     ('{', '}')
                        else:
                            pos, line_no, last_pos = self.get_matching_bracket_pos \
                                                     ('{', '};')
                            print 'fff'

                        del_indentct = 1
                        
                        if pos != -1:
                            cc.setPosition (last_pos, cc.MoveAnchor)
                            cc.select (cc.LineUnderCursor)
                            line1 = cc.selectedText ()
                            print line1
                            indent1 = 0
                            for c in line1:
                                if c == ' ':
                                    indent1 += 1
                                else:
                                    break                            

                            del_indentct = indentct - indent1 / len (self.indentwidth)
                            cc.setPosition (curr_pos, cc.MoveAnchor)

                            indentct -= 1
                        cc.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)

                        if line.count (' ') >= len(self.indentwidth):
                            for i in range (del_indentct * len (self.indentwidth)):                                
                                cc.deleteChar ()

                        cc.movePosition(QTextCursor.EndOfLine,QTextCursor.MoveAnchor)
                        
                        if indentct == 0:
                            QtGui.QTextEdit.keyPressEvent(self,event)
                        else:                            
                            QtGui.QTextEdit.keyPressEvent(self,event)
                            cc.movePosition(QTextCursor.StartOfLine,
                                            QTextCursor.MoveAnchor)
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

        if event.key() == QtCore.Qt.Key_Home: #Home key has 16777232
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
            if cc.position () >= self.tooltip_stack[0][1]:                
                x1,y1,x2,y2 = self.cursorRect().getCoords()
                self.tooltip_x = self.mapToGlobal(QtCore.QPoint(x2,y2)).x()
                self.tooltip_y = self.mapToGlobal(QtCore.QPoint(x2,y2)).y()
                QtGui.QToolTip.showText (QtCore.QPoint (self.tooltip_x, self.tooltip_y),
                                         self.tooltip_stack[0][0], self)
            
        if event.key() == 40: #40 is for (
            cc = self.textCursor()
            curr_pos = cc.position ()
            cc.movePosition(cc.PreviousWord,cc.KeepAnchor,2)
            selected_text = str(cc.selectedText())            
            
            if len(self.tooltip_stack)!=0:
                
                text = self.tooltip_stack [0]
                if isinstance (text, tuple) == False:
                    self.tooltip_stack [0] = (text, curr_pos)
                
                self.showtooltip = True
           
        if event.key() == 41 or event.key() == 93: ##41 is for ) and 93 for ]
            open_bracket = '['
            close_bracket = ']'
            if event.key () == 41:
                open_bracket = '('
                close_bracket = ')'
                
            curr_pos = cc.position ()
            pos, line_no, last_pos = self.get_matching_bracket_pos (open_bracket,
                                                                    close_bracket)
            if pos != -1:                
                self.setTextCursor (cc)
                cc.setPosition (last_pos - 1, cc.MoveAnchor)
                cc.setPosition (curr_pos, cc.KeepAnchor)
                self.setTextCursor (cc)
                
                if open_bracket == '(':                    
                    if self.showtooltip==True and self.tooltip_stack[0][1] == last_pos:
                        self.tooltip_stack.pop(0)
                            
                    if len(self.tooltip_stack) == 0:
                        QtGui.QToolTip.hideText()
                        self.showtooltip = False

                self.removeselectedtext = False
                    
        ##Show a list of all the matches for the object or function or class
                    
        if len(self.includefileclassarray)!=0 or len(self.includefilefuncarray)!=0 or len(self.curr_file_func_array)!=0:
            if event.key() == 32 or event.key() == 16777217 or event.key() == 16777250: #for Tab,space and enter key
                self.funcmatchlist.setVisible(False)
            else:
                #print 'list all matches'
                self.show_word_completion()
                
        #If dot . is pressed then check whether there's an object and whether it is available
        if event.key() == 46 and (self.list_objects !=[] or self.list_references !=[]):
            cc = self.textCursor()
            cc.movePosition(cc.WordLeft,cc.MoveAnchor,2)
            cc.select(QTextCursor.WordUnderCursor)
            word = cc.selectedText()
            try:
                for _object in self.list_objects+self.list_references:
                    if _object.name == word:                                                
                        x1,y1,x2,y2 = self.cursorRect().getCoords()
                        self.funcmatchlist.setGeometry(x2,y2,250,160)
                        self.funcmatchlist.clear()
                        self.funcmatchlist.setVisible(True)                        
                        for _func in _object.class_type.getFullPublicList():                            
                            self.funcmatchlist.addItem(_func)
            except:
                pass

        
        if event.key() == 62 and self.list_pointers!=[]:
            cc = self.textCursor()
            curr_pos = cc.position()
            cc.movePosition(cc.WordLeft,cc.KeepAnchor,1)
            cc.select(QTextCursor.WordUnderCursor)
            if str(cc.selectedText())== '->':
                cc.movePosition(cc.WordLeft,cc.KeepAnchor,2)
                cc.select(QTextCursor.WordUnderCursor)
                word = str(cc.selectedText())
                try:
                    for _object in self.list_pointers:
                        if _object.name == word:                                                
                            x1,y1,x2,y2 = self.cursorRect().getCoords()
                            self.funcmatchlist.setGeometry(x2,y2,250,160)
                            self.funcmatchlist.clear()
                            self.funcmatchlist.setVisible(True)                        
                            for _func in _object.class_type.getFullPublicList():                            
                                self.funcmatchlist.addItem(_func)
                except:
                    pass
            
        #if scope resolution operator :: is inserted        
        if event.key() == 58 and self.includefileclassarray !=[]:
            cc = self.textCursor()
            curr_pos = cc.position()
            cc.movePosition(cc.WordLeft,cc.KeepAnchor,1)
            cc.select(QTextCursor.WordUnderCursor)
            
            if str(cc.selectedText()) == '::':
                cc.movePosition(cc.WordLeft,cc.KeepAnchor,2)
                cc.select(QTextCursor.WordUnderCursor)
                prev_word = str(cc.selectedText())
                #print str(cc.selectedText())
                cc.select(QTextCursor.LineUnderCursor)
                line = cc.selectedText()
                
                _class =None
                for __class in self.includefileclassarray:
                    
                    if __class.name == prev_word:
                        _class = __class

                for __class in self.curr_file_class_array:
                    
                    if __class.name == prev_word:
                        _class = __class

                if _class != None:
                    x1,y1,x2,y2 = self.cursorRect().getCoords()
                    self.funcmatchlist.setGeometry(x2,y2,250,160)
                    self.funcmatchlist.clear()
                    self.funcmatchlist.setVisible(True) 
                    for func in _class.getFullList():    
                        self.funcmatchlist.addItem(func)
                        
    def show_word_completion(self):

        cc = self.textCursor()
        cc.select(QTextCursor.WordUnderCursor)
        word = str(cc.selectedText())
        self.funcmatchlist.setVisible(False)
        self.funcmatchlist.clear()
        
        if len(word)>=2:
            if self.filetype == 'C Project' or self.filetype == 'C File': ##For C Project, C Files and C++ Files with only global functions, because they will not contain any classes
                
                include_func_match_list = []
                func_name_match_list = []
                
                for i in range(len(self.curr_file_func_array)):                            
                    if word == self.curr_file_func_array[i].name[0:len(word)]:
                        include_func_match_list.append(self.curr_file_func_array[i].getDeclaration())
                        func_name_match_list.append (self.curr_file_func_array[i].name)

                #print "(((",include_func_match_list,")))"
                
                for i in range(len(self.includefilefuncarray)):                            
                    if word == self.includefilefuncarray[i].name[0:len(word)] and\
                       self.includefilefuncarray[i].name not in func_name_match_list:
                        include_func_match_list.append(self.includefilefuncarray[i].getDeclaration())

                #print "[[[[[",include_func_match_list,"]]]]"
                
                for struct in self.includefileclassarray+self.curr_file_class_array:
                    if word == struct.name[0:len(word)]:
                        include_func_match_list.append(struct.getDeclaration())
                    for typedef in struct.list_typedef:
                        if word == typedef.name[0:len(word)]:
                            include_func_match_list.append(typedef.name)

                if self.main_win.current_proj.proj_gtk_type == 'gtk+':
                    include_func_match_list += self.main_win.gtk_support_structs.get_all_struct_with_str (word)
                    include_func_match_list += self.main_win.gtk_support_defines.get_all_define_with_str (word)
                
                for _object in self.list_objects+self.list_references+self.list_pointers:
                    if word == _object.name[0:len(word)]:                                
                        x1,y1,x2,y2 = self.cursorRect().getCoords()
                        self.funcmatchlist.setGeometry(x2,y2,250,160)                                
                        self.funcmatchlist.setVisible(True)                                
                        self.funcmatchlist.addItem(_object.getDeclaration())

                if self.main_win.current_proj.proj_gtk_type == "gtk+":
                    include_func_match_list += self.main_win.gtk_support_functions.get_similar_funcs (word)
                
                if include_func_match_list!=[]:
                    x1,y1,x2,y2 = self.cursorRect().getCoords()
                    self.funcmatchlist.setGeometry(x2,y2,250,160)
                    self.funcmatchlist.setVisible(True)
                    for string in include_func_match_list:
                        self.funcmatchlist.addItem(string)
                    self.funcmatchlist.setCurrentRow (0)
            else:                    
                ##For C++ Projects and C++ Files
                
                ##Find the scope also, if cursor is in a class only then display its all members
                class_name = str(self.parent.combo_class.currentText())
                for _class in (self.includefileclassarray + self.curr_file_class_array):
                    if class_name == _class.name:
                        for var in _class.list_public_members + _class.list_private_members + _class.list_protected_members:
                            if word in var.getDeclaration():
                                x1,y1,x2,y2 = self.cursorRect().getCoords()
                                self.funcmatchlist.setGeometry(x2,y2,250,160)
                                self.funcmatchlist.addItem(var.getDeclaration())
                                self.funcmatchlist.setVisible(True)
                            
                for _class in (self.includefileclassarray + self.curr_file_class_array+self.curr_file_func_array):
                    if word in _class.name and _class.name != class_name:
                        x1,y1,x2,y2 = self.cursorRect().getCoords()
                        self.funcmatchlist.setGeometry(x2,y2,250,160)
                        self.funcmatchlist.addItem(_class.getDeclaration())
                        self.funcmatchlist.setVisible(True)
                
                ### Don't forget to add scope rule for objects
                
                for _object in self.list_objects+self.list_references+self.list_pointers:
                    if word == _object.name[0:len(word)]:                                
                        x1,y1,x2,y2 = self.cursorRect().getCoords()
                        self.funcmatchlist.setGeometry(x2,y2,250,160)                                
                        self.funcmatchlist.setVisible(True)                                
                        self.funcmatchlist.addItem(_object.getDeclaration())
        cc.clearSelection()
                
class codewidget(QtGui.QWidget):    
            
    def __init__(self,projtype,parent=None):

        QtGui.QWidget.__init__(self,parent)
        self.parent = parent
        self.vbox = QtGui.QVBoxLayout(self)
        self.txtInput = txtInputclass(projtype,self)        

        self.number_bar = NumberBar(self)
        self.number_bar.setTextEdit(self.txtInput)

        self.breakpoints_bar = BreakpointsBar(self)
        self.breakpoints_bar.setTextEdit(self.txtInput)
        
        self.hbox_textedit = QtGui.QHBoxLayout(self)
        self.hbox_textedit.setSpacing(0)
        self.hbox_textedit.setMargin(0)
        self.hbox_textedit.addWidget(self.breakpoints_bar)
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

        self.list_breakpoints=[]
        self.drawLinePointer = False
        self.linePointer=-1
        self.list_breakpoints_commands=[]
        
    def eventFilter(self, object, event):
                
        if object in (self.txtInput, self.txtInput.viewport()):
            self.number_bar.update()
            self.breakpoints_bar.update()
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

    def find_curr_func_objects(self):

        try:
            text = ""
            
            ##Whenever a current function changes then all objects declared in that
            ##function will be found.
            self.txtInput.list_objects = []
            self.txtInput.list_pointers = []
            self.txtInput.list_references = []
            if self.combo_funcposarray == []:
                return
            
            current_func_text = str(self.combo_func.currentText())
            _current_func = CFunction()
            _current_func.createFromDeclaration(current_func_text)
            
            if self.txtInput.filetype=="C Project" or self.txtInput.filetype=="C File":

                i = self.combo_func.currentIndex()
                if len(self.combo_funcposarray)!=i+1:
                    text = unicode(self.txtInput.toPlainText(),'utf-8',errors='ignore')[self.combo_funcposarray[i]+1:self.combo_funcposarray[i+1]+1]
                else:
                    text = unicode(self.txtInput.toPlainText(),'utf-8',errors='ignore')[self.combo_funcposarray[i]+1:]

                current_func = None
                for func in self.txtInput.includefilefuncarray + self.txtInput.curr_file_func_array:
                    if _current_func.getDeclaration() == func.getDeclaration():
                        current_func = func

                ###For getting struct objects
                if current_func!=None:
                    
                    for struct in self.txtInput.includefileclassarray+self.txtInput.curr_file_class_array:
                        typedef_object_list = []
                        for typedef in struct.list_typedef:
                            typedef_object_list += re.findall(r'\b%s\b\s+\w+.+\s*?\;'%typedef.name,text)
                        
                        for object_name in re.findall(r'\b%s\b\s+\w+.+\s*?\;'%struct.getDeclaration(),text)+typedef_object_list: 
                            if ',' not in object_name:
                                _object = CObject()
                                _object.createFromDeclaration(object_name)
                                _object.scope = current_func
                                _object.class_type = struct
                                _object.isObject=True
                                self.txtInput.list_objects.append(_object)
                            else:
                                object_name_split = object_name.split(',')
                                _object = CObject()
                                _object.createFromDeclaraion(object_name)
                                _object.class_type = struct
                                _object.isObject=True
                                self.txtInput.list_objects.append(_object)
                                for j in object_name_split[1:]:
                                    _object = CObject()
                                    _object.createFromDeclaration(_object.type+' '+j)
                                    _object.class_type = struct
                                    _object.isObject=True
                                    self.txtInput.list_objects.append(_object)
                        #print [_object.name for _object in self.txtInput.list_objects]
                        
                        ###For pointers
                        typedef_pointers_list = []
                        for typedef in struct.list_typedef:
                            typedef_pointers_list += re.findall(r'\b%s\s*\*\s*\w+.+'%typedef.name,text)
                            
                        #print typedef_pointers_list
                        
                        for object_name in re.findall(r'\b%s\s*\*\s*\w+.+'%struct.name,text) + typedef_pointers_list:                    
                            if ',' not in object_name:
                                _object = CObject()
                                _object.createFromDeclaration(object_name)
                                _object.scope = current_func
                                _object.class_type = struct
                                _object.isPointer=True
                                self.txtInput.list_pointers.append(_object)
                            else:
                                object_name_split = object_name.split(',')
                                _object = CObject()
                                _object.createFromDeclaration(object_name)
                                _object.class_type = struct
                                _object.isPointer=True
                                self.txtInput.list_pointers.append(_object)
                                for j in object_name_split[1:]:
                                    _object = CObject()
                                    _object.createFromDeclaration(_object.type+' '+j)
                                    _object.class_type = struct
                                    _object.isPointer=True
                                    self.txtInput.list_pointers.append(_object)
                        #print [_object.name for _object in self.txtInput.list_pointers]
                ###########################
                                    
                    ###For getting primitive types objects
                    for _type in list_primitive_types:                        
                        for object_name in re.findall(r'\b%s\b\s+\w+.+\s*?\;'%_type.name,text):
                            
                            if ',' not in object_name:
                                _object = CVariable()
                                _object.createFromDeclaration(object_name)
                                _object.scope = current_func
                                _object.type=_type.name
                                _object.isObject=True
                                self.txtInput.list_objects.append(_object)
                            else:                                
                                object_name_split = object_name.split(',')
                                _object = CVariable()
                                _object.createFromDeclaration(object_name_split[0])
                                _object.scope = current_func
                                _object.type=_type.name
                                _object.isObject=True
                                self.txtInput.list_objects.append(_object)
                                for j in object_name_split[1:]:
                                    _object = CVariable()
                                    _object.createFromDeclaration(_type.name+' '+j)
                                    _object.scope = current_func
                                    _object.type=_type.name
                                    _object.isObject=True
                                    self.txtInput.list_objects.append(_object)                        
                        
                        ###For pointers  
                        for object_name in re.findall(r'\b%s\s*\*\s*\w+.+'%_type.name,text):
                            if ',' not in object_name:
                                _object = CVariable()
                                _object.createFromDeclaration(object_name)
                                _object.scope = current_func
                                _object.type=_type.name
                                _object.isPointer=True
                                self.txtInput.list_pointers.append(_object)
                            else:
                                object_name_split = object_name.split(',')
                                _object = CVariable()
                                _object.createFromDeclaration(object_name_split[0])
                                _object.scope = current_func
                                _object.type=_type.name
                                _object.isPointer=True
                                self.txtInput.list_pointers.append(_object)
                                for j in object_name_split[1:]:
                                    _object = CVariable()
                                    _object.createFromDeclaration(_type.name+'* '+object_name)
                                    _object.scope = current_func
                                    _object.type=_type.name
                                    _object.isPointer=True
                                    self.txtInput.list_pointers.append(_object)                        
            else:
                class_current_index = self.combo_class.currentIndex()
                i = self.combo_func.currentIndex()
                    
                if len(self.combo_funcposarray[class_current_index])!=i+1:
                    text = str(self.txtInput.toPlainText())[self.combo_funcposarray[class_current_index][i]+1:self.combo_funcposarray[class_current_index][i+1]+1]
                else:
                    text = str(self.txtInput.toPlainText())[self.combo_funcposarray[class_current_index][i]+1:]

                for _class in self.txtInput.includefileclassarray+self.txtInput.curr_file_class_array:
                    ##First find the scope of the variable, i.e. the function where
                    ##variable is declared            
                    current_func = None
                    __class=None
                    
                    for __class in self.txtInput.includefileclassarray+self.txtInput.curr_file_class_array:
                        if __class.name == str(self.combo_class.currentText()):
                            for func in __class.list_public_members+__class.list_private_members+__class.list_protected_members:
                                #print func.name
                                if func.var_type=="Function":                            
                                    if _current_func.getDeclaration()==func.getDeclaration():                                
                                        current_func = func
                                        break
                        
                    ###Found the scope in current_func

                    ###For objects                
                    for object_name in re.findall(r'\b%s\b\s+\w+.+\s*?\;'%_class.name,text):                
                        if ',' not in object_name:
                            _object = CPPObject()
                            _object.createFromDeclaration(object_name)
                            _object.scope = current_func
                            _object.class_type = _class
                            _object.isObject=True
                            self.txtInput.list_objects.append(_object)
                        else:
                            object_name_split = object_name.split(',')
                            _object = CPPObject()
                            _object.createFromDeclaraion(object_name)
                            _object.class_type = _class
                            _object.isObject=True
                            self.txtInput.list_objects.append(_object)
                            for j in object_name_split[1:]:
                                _object = CPPObject()
                                _object.createFromDeclaration(_object.type+' '+j)
                                _object.class_type = _class
                                _object.isObject=True
                                self.txtInput.list_objects.append(_object)

                    ###For pointers
                    for object_name in re.findall(r'\b%s\b\*\s+\w+.+\s*?\;'%_class.name,text):                    
                        if ',' not in object_name:
                            _object = CPPObject()
                            _object.createFromDeclaration(object_name)
                            _object.scope = current_func
                            _object.class_type = _class
                            _object.isPointer=True
                            self.txtInput.list_pointers.append(_object)
                        else:
                            object_name_split = object_name.split(',')
                            _object = CPPObject()
                            _object.createFromDeclaraion(object_name)
                            _object.class_type = _class
                            self.txtInput.list_pointers.append(_object)
                            for j in object_name_split[1:]:
                                _object = CPPObject()
                                _object.createFromDeclaration(_object.type+' '+j)
                                _object.class_type = _class
                                _object.isPointer=True
                                self.txtInput.list_pointers.append(_object)

                    ###For References                
                    for object_name in re.findall(r'\b%s\b\&\s+\w+.+\s*?\;'%_class.name,text):                    
                        if ',' not in object_name:
                            _object = CPPObject()
                            _object.createFromDeclaration(object_name)
                            _object.scope = current_func
                            _object.class_type = _class
                            _object.isReference=True
                            self.txtInput.list_references.append(_object)
                        else:
                            object_name_split = object_name.split(',')
                            _object = CPPObject()
                            _object.createFromDeclaraion(object_name)
                            _object.class_type = _class
                            _object.isReference=True
                            self.txtInput.list_references.append(_object)
                            for j in object_name_split[1:]:
                                _object = CPPObject()
                                _object.createFromDeclaration(_object.type+' '+j)
                                _object.class_type = _class
                                _object.isReference=True
                                self.txtInput.list_references.append(_object)

        except AttributeError:
             pass
        
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

        self.find_curr_func_objects()
        cc.setPosition(pos,cc.MoveAnchor)
        #print "GOING AT %i"%(pos)
        self.txtInput.setTextCursor(cc)
        self.txtInput.highlightcurrentline()        

    def sendSetBreakpointSignal(self,line):

        self.emit(QtCore.SIGNAL('setBreakpoint(int)'),line)
        self.list_breakpoints_commands.append('-break-insert '+self.filename+':'+str(line))
        
    def breakpointChange(self,breakpoint):

        self.emit(QtCore.SIGNAL('breakpointStateChanged(int,int)'),int(breakpoint.line),int(breakpoint.state))

        if breakpoint.state==BREAKPOINT_STATE_DISABLED:            
            for command in self.list_breakpoints_commands:
                if command.find(str(breakpoint.line))!=-1:
                    self.list_breakpoints_commands.remove(command)
                    break
        else:
            for _breakpoint in self.list_breakpoints:
                if int(_breakpoint.line)==int(breakpoint.line):
                    self.list_breakpoints_commands.append('-break-insert '+ self.filename+':'+str(breakpoint.line))
                    break                    

    def hideLinePointer(self):

        self.drawLinePointer = False
        self.breakpoints_bar.repaint()
        
    def setLinePointerAtLine(self,line):

        self.linePointer=line
        self.drawLinePointer = True
        print "setlinepointer", line
        self.breakpoints_bar.repaint()
