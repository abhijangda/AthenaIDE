#848 Lines
from PyQt4 import QtGui,QtCore
import syntaxcpp,syntaxc
import re

class winoptions(QtGui.QDialog):

    def __init__(self,parent=None):
        global encoding,indent
        QtGui.QMainWindow.__init__(self,parent)                      
        self.setGeometry(100,100,701,460)
        self.setWindowTitle('Options')

        indent = ''
        encoding=''
        gcccommand =''
        gppcommand=''
        indentwidth = ''
        inc_indent_syms = ''
        dec_indent_syms = ''
        autosavetimeout = ''
        autosavetabs = ''
        tabwidth = ''
        wordwrap = ''
        autosave = ''
        recentfiles = ''
        
        try:
            
            settings = ''
            settingsfile = open('./settings.ini','r')
            for line in settingsfile:
                settings = settings + line
            
            settingsfile.close()
            
            for i in range(settings.index('<indentwidth>')+len('<indentwidth>'),settings.index('</indentwidth>')):
                indentwidth = indentwidth + settings[i]
                
            for i in range(settings.index('<incindentsymbols>')+len('<incindentsymbols>'),settings.index('</incindentsymbols>')):
                inc_indent_syms = inc_indent_syms + settings[i]
                
            for i in range(settings.index('<decindentsymbols>')+len('<decindentsymbols>'),settings.index('</decindentsymbols>')):
                dec_indent_syms = dec_indent_syms + settings[i]

            for i in range(settings.index('<autosave>')+len('<autosave>'),settings.index('</autosave>')):
                autosave = autosave + settings[i]
                
            for i in range(settings.index('<autosavetimeout>')+len('<autosavetimeout>'),settings.index('</autosavetimeout>')):
                autosavetimeout = autosavetimeout + settings[i]
                
            for i in range(settings.index('<autosavetabs>')+len('<autosavetabs>'),settings.index('</autosavetabs>')):
                autosavetabs = autosavetabs + settings[i]
                
            for i in range(settings.index('<wordwrap>')+len('<wordwrap>'),settings.index('</wordwrap>')):
                wordwrap = wordwrap + settings[i]

            for i in range(settings.index('<tabwidth>')+len('<tabwidth>'),settings.index('</tabwidth>')):
                tabwidth = tabwidth + settings[i]
                
            for i in range(settings.index('<encoding>')+len('<encoding>'),settings.index('</encoding>')):
                encoding = encoding + settings[i]
            
            for i in range(settings.index('<indentation>')+len('<indentation>'),settings.index('</indentation>')):
                indent = indent + settings[i]
                
            for i in range(settings.index('<recent files>')+len('<recent files>'),settings.index('</recent files>')):
                recentfiles = recentfiles + settings[i]
                
            for i in range(settings.index('<gcc>') + len('<gcc>'),settings.index('</gcc>')):
                gcccommand = gcccommand + settings[i]

            for i in range(settings.index('<g++>') + len('<g++>'),settings.index('</g++>')):
                gppcommand = gppcommand + settings[i]

        except:
            pass

        if indent == '':
            indent = 'False'
        if encoding =='':
            encoding = 'PlainText'

        self.tabs = QtGui.QTabWidget(self)
        self.page_general = QtGui.QWidget(self)
        
        self.encodinglabel = QtGui.QLabel('Default Encoding',self.page_general)        
        self.radioc = QtGui.QRadioButton('C',self.page_general)        
        self.radiocpp = QtGui.QRadioButton('C++',self.page_general)        
        self.radioplain = QtGui.QRadioButton('Plain Text',self.page_general)        
        self.group_encoding = QtGui.QButtonGroup(self)
        self.group_encoding.addButton(self.radioc)
        self.group_encoding.addButton(self.radiocpp)
        self.group_encoding.addButton(self.radioplain)
        
        if encoding == 'C':
            self.radioc.setChecked(True)
        if encoding == 'C++':
            self.radiocpp.setChecked(True)
        if encoding == 'PlainText':
            self.radioplain.setChecked(True)
        
        self.chkindent = QtGui.QCheckBox('Indentation',self.page_general)
        self.lblindentwidth = QtGui.QLabel("Indent Width (number of spaces)",self.page_general)
        self.lblincindentsyms = QtGui.QLabel("Increase Indentation if line contains following symbols",self.page_general)
        self.lbldecindentsyms = QtGui.QLabel("Decrease Indentation if line contains following symbols",self.page_general)
        self.txtindentwidth = QtGui.QLineEdit(self.page_general)
        self.txtincindentsyms = QtGui.QLineEdit(self.page_general)
        self.txtdecindentsyms = QtGui.QLineEdit(self.page_general)

        if indent == 'True':
            self.chkindent.setChecked(True)
            self.txtindentwidth.setText(str(len(indentwidth)))
            self.txtincindentsyms.setText(inc_indent_syms)
            self.txtdecindentsyms.setText(dec_indent_syms)
        else:
            self.chkindent.setChecked(False)
            self.lblindentwidth.setEnabled(False)
            self.lblincindentsyms.setEnabled(False)
            self.lbldecindentsyms.setEnabled(False)
            self.txtindentwidth.setEnabled(False)
            self.txtincindentsyms.setEnabled(False)
            self.txtdecindentsyms.setEnabled(False)

        self.chkautosave = QtGui.QCheckBox("Auto Save",self.page_general)
        self.lblautosavetimeout = QtGui.QLabel("Auto Save current file after every (min)",self.page_general)
        self.optautosaveall = QtGui.QRadioButton("Auto Save all opened tabs",self.page_general)
        self.optautosavecurrent = QtGui.QRadioButton("Auto Save current tab",self.page_general)
        self.txtautosavetimeout = QtGui.QLineEdit(self.page_general)

        if autosave == 'True':
            self.chkautosave.setChecked(True)
            self.txtautosavetimeout.setText(autosavetimeout)
            if autosavetabs == 'all':
                self.optautosaveall.setChecked(True)
            if autosavetabs == 'current':
                self.optautosavecurrent.setChecked(True)
            
        else:
            self.chkautosave.setChecked(False)
            self.lblautosavetimeout.setEnabled(False)
            self.optautosaveall.setEnabled(False)
            self.optautosavecurrent.setEnabled(False)
            self.txtautosavetimeout.setEnabled(False)
                        
        self.lbltabwidth = QtGui.QLabel("Tab Width (Spaces per 1 Tab)",self.page_general)
        self.txttabwidth = QtGui.QLineEdit(self.page_general)

        self.txttabwidth.setText(tabwidth)
        
        self.chkwordwrap = QtGui.QCheckBox("Word Wrap",self.page_general)

        if wordwrap == 'True':
            self.chkwordwrap.setChecked(True)

        self.chkrecentfiles = QtGui.QCheckBox("Enable/Disable Recent Files",self.page_general)
        if recentfiles == 'True':
            self.chkrecentfiles.setChecked(True)
            
        self.chkindent.setGeometry(10,10,111,26)
        self.lblindentwidth.setGeometry(30,44,221,21)
        self.lblincindentsyms.setGeometry(30,80,361,21)
        self.lbldecindentsyms.setGeometry(30,120,361,21)
        self.txtindentwidth.setGeometry(263,39,113,31)
        self.txtincindentsyms.setGeometry(400,77,270,31)
        self.txtdecindentsyms.setGeometry(400,117,270,31)
        self.chkautosave.setGeometry(10,155,101,26)
        self.lblautosavetimeout.setGeometry(30,190,261,21)
        self.optautosaveall.setGeometry(30,228,211,20)
        self.optautosavecurrent.setGeometry(280,228,191,20)
        self.txtautosavetimeout.setGeometry(310,187,110,31)
        self.encodinglabel.setGeometry(10,260,131,21)
        self.radioc.setGeometry(270,260,108,26)
        self.radiocpp.setGeometry(400,260,108,26)
        self.radioplain.setGeometry(160,260,108,26)
        self.lbltabwidth.setGeometry(10,300,201,21)
        self.txttabwidth.setGeometry(240,300,113,31)
        self.chkwordwrap.setGeometry(10,330,121,26)
        self.chkrecentfiles.setGeometry(10,355,221,26)
        
        self.groupautosave = QtGui.QButtonGroup(self)
        self.groupautosave.addButton(self.optautosavecurrent)
        self.groupautosave.addButton(self.optautosaveall)

        self.connect(self.chkindent,QtCore.SIGNAL('clicked()'),self.chkindent_clicked)
        self.connect(self.chkautosave,QtCore.SIGNAL('clicked()'),self.chkautosave_clicked)
        
        self.cmdcancel = QtGui.QPushButton('Cancel',self)
        self.cmdcancel.setGeometry(500,426,98,31)
        self.cmdcancel.show()
        self.cmdok = QtGui.QPushButton('Ok',self)
        self.cmdok.setGeometry(600,426,98,31)
        self.cmdok.show()

        self.tabs.setGeometry(0,0,691,421)
        self.tabs.addTab(self.page_general,'General')        
        
        self.pagegcc = QtGui.QWidget(self)
                
        self.gcc_ansi = QtGui.QCheckBox("Support all C89 features(-ansi)",self.pagegcc)
        if gcccommand.count(' -ansi') ==1:
            self.gcc_ansi.setChecked(True)
            
        self.gcc_fhosted = QtGui.QCheckBox("Compile in hosted environment(-fhosted)",self.pagegcc)
        if gcccommand.count(' -fhosted') ==1:
            self.gcc_fhosted.setChecked(True)
            
        self.gcc_wformat = QtGui.QCheckBox("Check calls to format strings(-Wformat)",self.pagegcc)
        if gcccommand.count(' -wformat') ==1:
            self.gcc_wformat.setChecked(True)
            
        self.gcc_e = QtGui.QCheckBox("Preprocess Only(-E)",self.pagegcc)
        if gcccommand.count(' -E') ==1:
            self.gcc_e.setChecked(True)
            
        self.gcc_s = QtGui.QCheckBox("Compile Only; do not assemble or link(-S)",self.pagegcc)
        if gcccommand.count(' -S') ==1:
            self.gcc_s.setChecked(True)
            
        self.gcc_c = QtGui.QCheckBox("Compile and assemble but do not link(-c)",self.pagegcc)
        if gcccommand.count(' -c') ==1:
            self.gcc_c.setChecked(True)
            
        self.gcc_ffreestanding = QtGui.QCheckBox("Compile in freestanding environment (-ffreestanding)",self.pagegcc)
        if gcccommand.count(' -ffreestanding') ==1:
            self.gcc_ffreestanding.setChecked(True)
            
        self.gcc_fno_asm = QtGui.QCheckBox("Disables use of asm, inline, and typeof as keywords, \nallowing their use as identifiers.(-fno-asm)",self.pagegcc)
        if gcccommand.count(' -fno-asm') ==1:
            self.gcc_fno_asm.setChecked(True)
            
        self.gcc_trigraphs = QtGui.QCheckBox("Enables support for C89 trigraphs.(-trigraphs)",self.pagegcc)
        if gcccommand.count(' -trigraphs') ==1:
            self.gcc_trigraphs.setChecked(True)
            
        self.gcc_werror = QtGui.QCheckBox("Terminates compilation when warning occurs(-Werror)",self.pagegcc)
        if gcccommand.count(' -werror') ==1:
            self.gcc_werror.setChecked(True)
            
        self.gcc_std = QtGui.QCheckBox("Sets the Language to Value(-std)",self.pagegcc)
        self.gcc_std_line_edit = QtGui.QLineEdit('-std',self.pagegcc)
        ans = re.findall(r'\bstd\=.*\b',gcccommand)
        if ans != []:
            if ans[0].count('std') == 1:
                self.gcc_std.setChecked(True)
                self.gcc_std_line_edit.setText('-'+ans[0])
                
        self.gcc_o = QtGui.QCheckBox("Compile to file (-o <output>)",self.pagegcc)
        if gcccommand.count('-o <output>') == 1:
            self.gcc_o.setChecked(True)
            
        self.gcc_b = QtGui.QCheckBox("Add directory to compiler search path(-B <directory>)",self.pagegcc)
        self.gcc_b_line_edit = QtGui.QLineEdit('',self.pagegcc)
        ans = re.findall(r'\bB\b.+\w',gcccommand)
        if ans !=[]:
            if ans[0].count('-B') == 1:
                self.gcc_b.setChecked(True)
                self.gcc_b_line_edit,setText('-'+ans[0])
        self.gcc_b_add = QtGui.QPushButton('...',self.pagegcc)
        
        self.gcc_command_label = QtGui.QLabel('The following command will be executed to compile',self.pagegcc)
        self.gcc_command_line_edit = QtGui.QLineEdit(gcccommand,self.pagegcc)
        
        self.gcc_ansi.setGeometry(5,10,231,26)
        self.gcc_fhosted.setGeometry(5,40,291,26)
        self.gcc_wformat.setGeometry(5,80,291,26)
        self.gcc_e.setGeometry(5,110,281,26)
        self.gcc_s.setGeometry(5,140,301,26)
        self.gcc_c.setGeometry(5,170,291,26)
        self.gcc_ffreestanding.setGeometry(306,10,271,26)
        self.gcc_fno_asm.setGeometry(306,40,460,38)
        self.gcc_trigraphs.setGeometry(306,80,331,26)
        self.gcc_werror.setGeometry(306,110,391,26)
        self.gcc_std.setGeometry(306,140,241,26)
        self.gcc_std_line_edit.setGeometry(550,138,113,31)
        self.gcc_o.setGeometry(306,170,931,26)
        self.gcc_b.setGeometry(7,210,381,26)
        self.gcc_b_line_edit.setGeometry(10,240,621,31)
        self.gcc_b_add.setGeometry(640,240,41,31)
        self.gcc_command_label.setGeometry(10,300,341,26)
        self.gcc_command_line_edit.setGeometry(10,330,671,31)

        self.connect(self.gcc_ansi, QtCore.SIGNAL('clicked()'),self.gcc_ansi_clicked)
        self.connect(self.gcc_fhosted, QtCore.SIGNAL('clicked()'),self.gcc_fhosted_clicked)
        self.connect(self.gcc_wformat, QtCore.SIGNAL('clicked()'),self.gcc_wformat_clicked)
        self.connect(self.gcc_e, QtCore.SIGNAL('clicked()'),self.gcc_e_clicked)
        self.connect(self.gcc_s, QtCore.SIGNAL('clicked()'),self.gcc_s_clicked)
        self.connect(self.gcc_c, QtCore.SIGNAL('clicked()'),self.gcc_c_clicked)
        self.connect(self.gcc_ffreestanding, QtCore.SIGNAL('clicked()'),self.gcc_ffreestanding_clicked)
        self.connect(self.gcc_fno_asm, QtCore.SIGNAL('clicked()'),self.gcc_fno_asm_clicked)
        self.connect(self.gcc_trigraphs, QtCore.SIGNAL('clicked()'),self.gcc_trigraphs_clicked)
        self.connect(self.gcc_werror, QtCore.SIGNAL('clicked()'),self.gcc_werror_clicked)
        self.connect(self.gcc_std, QtCore.SIGNAL('clicked()'),self.gcc_std_clicked)
        self.connect(self.gcc_o, QtCore.SIGNAL('clicked()'),self.gcc_o_clicked)
        self.connect(self.gcc_b, QtCore.SIGNAL('clicked()'),self.gcc_b_clicked)
        self.connect(self.gcc_b_add, QtCore.SIGNAL('clicked()'),self.gcc_b_add_clicked)
                
        self.tabs.addTab(self.pagegcc,'GNU C Compiler Options')

        self.pagegpp = QtGui.QWidget(self)

        self.gpp_fcheck_new = QtGui.QCheckBox('Ensure that the pointer returned by the \nnew operator is not NULL(-fcheck-new)',self.pagegpp)
        if gppcommand.count(' -fcheck-new') ==1:
            self.gpp_fcheck_new.setChecked(True)        

        self.gpp_fconserve_space = QtGui.QCheckBox('Puts global variables initialized at runtime \nand unintialized global variables in the \ncommon segment(-fconserve-space)',self.pagegpp)
        if gppcommand.count(' -fconserve-space') ==1:
            self.gpp_fconserve_space.setChecked(True)

        self.gpp_fno_const_strings = QtGui.QCheckBox('Assign string constants to char * type\n(-fno-const-strings)',self.pagegpp)
        if gppcommand.count(' -fno-const-strings') ==1:
            self.gpp_fno_const_strings.setChecked(True)        
        
        self.gpp_fno_elide_constructors = QtGui.QCheckBox('Always call copy constructor rather than \nusing a temporary(-fno-elide-constructors)',self.pagegpp)
        if gppcommand.count(' -fno-elide-constructors') ==1:
            self.gpp_fno_elide_constructors.setChecked(True)
            
        self.gpp_ffor_scope = QtGui.QCheckBox('Limits the scope of variables declared \nin a for loop to the end of loop(-ffor-scope)',self.pagegpp)
        if gppcommand.count(' -ffor-scope') ==1:
            self.gpp_ffor_scope.setChecked(True)
            
        self.gpp_Wno_deprecated = QtGui.QCheckBox('Do not generate warnings for deprecated C++ \nfeatures(-Wno-deprecated)',self.pagegpp)
        if gppcommand.count(' -Wno-deprecated') ==1:
            self.gpp_Wno_deprecated.setChecked(True)
            
        self.gpp_fno_rtti = QtGui.QCheckBox('Disables generation of RTTI information for classes \nwith virtual functions(-fno-rtti)',self.pagegpp)
        if gppcommand.count(' -fno-rtti') ==1:
            self.gpp_fno_rtti.setChecked(True)
            
        self.gpp_nostdincpp = QtGui.QCheckBox('Disables searching for header files in standard \ndirectories to C++(-nostdinc++)',self.pagegpp)
        if gppcommand.count(' -nostdinc++') ==1:
            self.gpp_nostdincpp.setChecked(True)
            
        self.gpp_Wabi = QtGui.QCheckBox('Generate warning when the compiler generates code \nincompatible with standard C++ ABI(-Wabi)',self.pagegpp)
        if gppcommand.count(' -Wabi') ==1:
            self.gpp_Wabi.setChecked(True)

        self.gpp_o = QtGui.QCheckBox('Compile to file (-o <output>)',self.pagegpp)
        if gppcommand.count(' -o <output>') ==1:
            self.gpp_o.setChecked(True)
            
        self.gpp_fabi_version = QtGui.QCheckBox('Specify version of C++ application \nbinary interface of the compiled \ncode(-fabi-version)',self.pagegpp)
        self.gpp_fabi_version_line_edit = QtGui.QLineEdit('',self.pagegpp)
        if gppcommand.count(' -fabi-version') ==1:
            if re.findall(r'\bversion\b.+\w',gppcommand)!=[]:
                self.gpp_fabi_version.setChecked(True)
                self.gpp_fabi_version_line_edit.setText(' -fabi-'+re.findall(r'\bversion\b.+\w',gppcommand)[0])
                
        self.gpp_b = QtGui.QCheckBox('Add directory to compiler search path(-B <directory>)',self.pagegpp)
        ans = re.findall(r'\bB\b.+\w',gppcommand)
        if ans !=[]:
            if ans[0].count('-B') == 1:
                self.gcc_b.setChecked(True)
                self.gcc_b_line_edit,setText('-'+ans[0])
        self.gpp_b_add = QtGui.QPushButton('...',self.pagegpp) 
            
        self.gpp_b_line_edit = QtGui.QLineEdit('',self.pagegpp)
        self.gpp_command_label = QtGui.QLabel('The following command will be executed to compile',self.pagegpp)
        self.gpp_command_line_edit = QtGui.QLineEdit(gppcommand,self.pagegpp)

        self.gpp_fcheck_new.setGeometry(5,0,291,40)
        self.gpp_fconserve_space.setGeometry(5,45,296,56)
        self.gpp_fno_const_strings.setGeometry(5,109,281,32)
        self.gpp_fno_elide_constructors.setGeometry(5,145,304,39)
        self.gpp_ffor_scope.setGeometry(5,192,307,34)
        self.gpp_Wno_deprecated.setGeometry(305,0,381,39)
        self.gpp_fno_rtti.setGeometry(305,40,460,38)
        self.gpp_nostdincpp.setGeometry(305,80,331,31)
        self.gpp_Wabi.setGeometry(305,121,380,31)
        self.gpp_o.setGeometry(305,154,291,26)
        self.gpp_fabi_version.setGeometry(305,182,271,54)
        self.gpp_fabi_version_line_edit.setGeometry(555,195,130,31)
        self.gpp_b.setGeometry(7,233,381,25)
        self.gpp_b_line_edit.setGeometry(10,263,620,30)
        self.gpp_b_add.setGeometry(640,263,41,30)
        self.gpp_command_label.setGeometry(10,300,341,21)
        self.gpp_command_line_edit.setGeometry(10,330,671,31)

        self.tabs.addTab(self.pagegpp,"GNU C++ Compiler Options")
        self.tabs.show()

        self.connect(self.gpp_fcheck_new, QtCore.SIGNAL('clicked()'),self.gpp_fcheck_new_clicked)
        self.connect(self.gpp_fconserve_space, QtCore.SIGNAL('clicked()'),self.gpp_fconserve_space_clicked)
        self.connect(self.gpp_fno_const_strings, QtCore.SIGNAL('clicked()'),self.gpp_fno_const_strings_clicked)
        self.connect(self.gpp_fno_elide_constructors, QtCore.SIGNAL('clicked()'),self.gpp_fno_elide_constructors_clicked)
        self.connect(self.gpp_ffor_scope, QtCore.SIGNAL('clicked()'),self.gpp_ffor_scope_clicked)
        self.connect(self.gpp_Wno_deprecated, QtCore.SIGNAL('clicked()'),self.gpp_Wno_deprecated_clicked)
        self.connect(self.gpp_fno_rtti, QtCore.SIGNAL('clicked()'),self.gpp_fno_rtti_clicked)
        self.connect(self.gpp_nostdincpp, QtCore.SIGNAL('clicked()'),self.gpp_nostdincpp_clicked)
        self.connect(self.gpp_Wabi, QtCore.SIGNAL('clicked()'),self.gpp_Wabi_clicked)
        self.connect(self.gpp_fabi_version, QtCore.SIGNAL('clicked()'),self.gpp_fabi_version_clicked)
        self.connect(self.gpp_b, QtCore.SIGNAL('clicked()'),self.gpp_b_clicked)

        self.connect(self.cmdok, QtCore.SIGNAL('clicked()'),self.ok)
        self.connect(self.cmdcancel, QtCore.SIGNAL('clicked()'),self.cancel)

    def chkindent_clicked(self):
        
        if self.chkindent.isChecked():
            self.lblindentwidth.setEnabled(True)
            self.lblincindentsyms.setEnabled(True)
            self.lbldecindentsyms.setEnabled(True)
            self.txtindentwidth.setEnabled(True)
            self.txtincindentsyms.setEnabled(True)
            self.txtdecindentsyms.setEnabled(True)
        else:
            self.lblindentwidth.setEnabled(False)
            self.lblincindentsyms.setEnabled(False)
            self.lbldecindentsyms.setEnabled(False)
            self.txtindentwidth.setEnabled(False)
            self.txtincindentsyms.setEnabled(False)
            self.txtdecindentsyms.setEnabled(False)
            
    def chkautosave_clicked(self):

        if self.chkautosave.isChecked():
            self.lblautosavetimeout.setEnabled(True)
            self.optautosaveall.setEnabled(True)
            self.optautosavecurrent.setEnabled(True)
            self.txtautosavetimeout.setEnabled(True)
        else:
            self.lblautosavetimeout.setEnabled(False)
            self.optautosaveall.setEnabled(False)
            self.optautosavecurrent.setEnabled(False)
            self.txtautosavetimeout.setEnabled(False)
            
###############For GNU C++ Compiler######################        
    def gpp_fcheck_new_clicked(self):

        text = str(self.gpp_command_line_edit.text())
        if self.gpp_fcheck_new.isChecked():
            text = text + " -fcheck-new"
        else:
            i = text.find(" -fcheck-new")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -fcheck-new"):]
                text = text2
        self.gpp_command_line_edit.setText(text)
        
    def gpp_fconserve_space_clicked(self):

        text = str(self.gpp_command_line_edit.text())
        if self.gpp_fconserve_space.isChecked():
            text = text + " -fconserve-space"
        else:
            i = text.find(" -fconserve-space")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -fconserve-space"):]
                text = text2
        self.gpp_command_line_edit.setText(text)
        
    def gpp_fno_const_strings_clicked(self):

        text = str(self.gpp_command_line_edit.text())
        if self.gpp_fno_const_strings.isChecked():
            text = text + " -fno-const-strings"
        else:
            i = text.find(" -fno-const-strings")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -fno-const-strings"):]
                text = text2
        self.gpp_command_line_edit.setText(text)
        
    def gpp_fno_elide_constructors_clicked(self):

        text = str(self.gpp_command_line_edit.text())
        if self.gpp_fno_elide_constructors.isChecked():
            text = text + " -fno-elide-constructors"
        else:
            i = text.find(" -fno-elide-constructors")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -fno-elide-constructors"):]
                text = text2
        self.gpp_command_line_edit.setText(text)
        
    def gpp_ffor_scope_clicked(self):

        text = str(self.gpp_command_line_edit.text())
        if self.gpp_ffor_scope.isChecked():
            text = text + " -ffor-space"
        else:
            i = text.find(" -ffor-space")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -ffor-space"):]
                text = text2
        self.gpp_command_line_edit.setText(text)
        
    def gpp_Wno_deprecated_clicked(self):

        text = str(self.gpp_command_line_edit.text())
        if self.gpp_Wno_deprecated.isChecked():
            text = text + " -Wno-deprecated"
        else:
            i = text.find(" -Wno-deprecated")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -Wno-deprecated"):]
                text = text2
        self.gpp_command_line_edit.setText(text)
        
    def gpp_fno_rtti_clicked(self):

        text = str(self.gpp_command_line_edit.text())
        if self.gpp_fno_rtti.isChecked():
            text = text + " -fno-rtti"
        else:
            i = text.find(" -fno-rtti")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -fno-rtti"):]
                text = text2
        self.gpp_command_line_edit.setText(text)
        
    def gpp_nostdincpp_clicked(self):

        text = str(self.gpp_command_line_edit.text())
        if self.gpp_nostdincpp.isChecked():
            text = text + " -nostdincpp"
        else:
            i = text.find(" -nostdincpp")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -nostdincpp"):]
                text = text2
        self.gpp_command_line_edit.setText(text)
        
    def gpp_Wabi_clicked(self):

        text = str(self.gpp_command_line_edit.text())
        if self.gpp_Wabi.isChecked():
            text = text + " -Wabi"
        else:
            i = text.find(" -Wabi")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -Wabi"):]
                text = text2
        self.gpp_command_line_edit.setText(text)

    def gpp_fabi_version_clicked(self):

        text = str(self.gpp_command_line_edit.text())

        if self.gpp_fabi_version.isChecked():
            if str(self.gpp_fabi_version_line_edit.text()) != '':
                text = text + str(self.gpp_fabi_version_line_edit.text())
            else:
                self.gpp_fabi_version.setChecked(False)
                
        else:
            ans = re.findall(r'\bversion\b.+\w',text)
            if ans !=[]:
                i = text.find('-fabi-'+ans[0])
                if i!=-1:
                    text2 = text[:i]
                    text2 = text2 + text[i+len(" -fabi-"+ans[0]):]
                    text = text2

        self.gpp_command_line_edit.setText(text)

    def gpp_b_clicked(self):

        text = str(self.gpp_command_line_edit.text())
        
        if self.gpp_b.isChecked():
            if str(self.gpp_b_line_edit.text()) != '':
                text = text + " -B " + str(self.gpp_b_line_edit.text())
            else:
                self.gpp_b.setChecked(False)
        else:
            ans = re.findall(r'\bB\b.+\w',text)
            if ans!=[]:
                i = text.find('-'+ans[0])
                if i!=-1:
                    text2 = text[:i]
                    text2 = text2 + text[i+len(" -"+ans[0]):]
                    text = text2
        
        self.gpp_command_line_edit.setText(text)

##############For GNU C Compiler##############################
        
    def gcc_ansi_clicked(self):

        text = str(self.gcc_command_line_edit.text())
        if self.gcc_ansi.isChecked():
            text = text + " -ansi"
        else:
            i = text.find(" -ansi")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -ansi"):]
                text = text2
        self.gcc_command_line_edit.setText(text)

    def gcc_fhosted_clicked(self):

        text = str(self.gcc_command_line_edit.text())
        if self.gcc_fhosted.isChecked():
            text = text + " -fhosted"
        else:
            i = text.find(" -fhosted")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -fhosted"):]
                text = text2
        self.gcc_command_line_edit.setText(text)

    def gcc_wformat_clicked(self):

        text = str(self.gcc_command_line_edit.text())
        if self.gcc_wformat.isChecked():
            text = text + " -Wformat"
        else:
            i = text.find(" -Wformat")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -Wformat"):]
                text = text2
        self.gcc_command_line_edit.setText(text)

    def gcc_e_clicked(self):

        text = str(self.gcc_command_line_edit.text())
        if self.gcc_e.isChecked():
            text = text + " -E"
        else:
            i = text.find(" -E")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -E"):]
                text = text2
        self.gcc_command_line_edit.setText(text)

    def gcc_s_clicked(self):

        text = str(self.gcc_command_line_edit.text())
        if self.gcc_s.isChecked():
            text = text + " -S"
        else:
            i = text.find(" -S")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -S"):]
                text = text2
        self.gcc_command_line_edit.setText(text)

    def gcc_c_clicked(self):

        text = str(self.gcc_command_line_edit.text())
        if self.gcc_c.isChecked():
            text = text + " -C"
        else:
            i = text.find(" -C")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -C"):]
                text = text2
        self.gcc_command_line_edit.setText(text)

    def gcc_ffreestanding_clicked(self):

        text = str(self.gcc_command_line_edit.text())
        if self.gcc_ffreestanding.isChecked():
            text = text + " -ffreestanding"
        else:
            i = text.find(" -ffreestanding")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -ffreestanding"):]
                text = text2
        self.gcc_command_line_edit.setText(text)

    def gcc_fno_asm_clicked(self):

        text = str(self.gcc_command_line_edit.text())
        if self.gcc_fno_asm.isChecked():
            text = text + " -fno-asm"
        else:
            i = text.find(" -fno-asm")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -fno-asm"):]
                text = text2
        self.gcc_command_line_edit.setText(text)

    def gcc_trigraphs_clicked(self):

        text = str(self.gcc_command_line_edit.text())
        if self.gcc_trigraphs.isChecked():
            text = text + " -trigraphs"
        else:
            i = text.find(" -trigraphs")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -trigraphs"):]
                text = text2
        self.gcc_command_line_edit.setText(text)

    def gcc_werror_clicked(self):

        text = str(self.gcc_command_line_edit.text())
        if self.gcc_werror.isChecked():
            text = text + " -Werror"
        else:
            i = text.find(" -Werror")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -Werror"):]
                text = text2
        self.gcc_command_line_edit.setText(text)

    def gcc_std_clicked(self):

        text = str(self.gcc_command_line_edit.text())
        if self.gcc_std.isChecked():
            if str(self.gcc_std_line_edit.text())!='-std':
                text = text + ' ' + str(self.gcc_std_line_edit.text())
            else:
                self.gcc_std.setChecked(False)
        else:
            ans = re.findall(r'\bstd\=.*\b',text)
            if ans !=[]:
                i = text.find('-'+ans[0])
                if i!=-1:
                    text2 = text[:i]
                    text2 = text2 + text[i+len(ans[0])+1:]
                    text = text2
        self.gcc_command_line_edit.setText(text)

    def gcc_o_clicked(self):

        text = str(self.gcc_command_line_edit.text())
        if self.gcc_o.isChecked():
            text = text + " -o <output>"
        else:
            i = text.find(" -o <output>")
            if i!=-1:
                text2 = text[:i]
                text2 = text2 + text[i+len(" -o <output>"):]
                text = text2
        self.gcc_command_line_edit.setText(text)

    def gcc_b_clicked(self):
        
        text = str(self.gcc_command_line_edit.text())
        if self.gcc_b.isChecked():
            if str(self.gcc_b_line_edit.text()) != '':
                text = text + " -B " + str(self.gcc_b_line_edit.text())
            else:
                self.gcc_b.setChecked(True)
        else:
            ans = re.findall(r'\bB\b.+\w',text)
            if ans !=[]:
                i = text.find('-'+ans[0])
                if i!=-1:
                    text2 = text[:i]
                    text2 = text2 + text[i+len("-"+ans[0]):]
                    text = text2
        self.gcc_command_line_edit.setText(text)
        
    def gcc_b_add_clicked(self):

        folder = str(QtGui.QFileDialog.getExistingDirectory(self,"Open Folder"))
        self.gcc_b_line_edit.setText(folder)

    def document(self,txtInput):
        
        self.txtInput = txtInput
    
    def cancel(self):
            
        #self.close()        
        self.destroy()

    def ok(self):
            
        global encoding,indent,gcccommmand,gppcommand
            
        if self.radiocpp.isChecked():                
            encoding = 'C++'
                            
        if self.radioc.isChecked():               
            encoding = 'C'
            
        if self.radioplain.isChecked():
            encoding = 'PlainText'
                        
        indent_width = ''
        inc_indent_syms = ''
        dec_indent_syms = ''       
        if self.chkindent.isChecked():
            indent='True'
            for i in range(int(self.txtindentwidth.text())):
                indent_width = indent_width + ' '
            
            inc_indent_syms = str(self.txtincindentsyms.text())
            dec_indent_syms = str(self.txtdecindentsyms.text())
        else:
            indent='False'

        autosavetimeout = ''
        autosavetabs = ''

        if self.chkautosave.isChecked():
            autosave = 'True'
            autosavetimeout = self.txtautosavetimeout.text()
            if self.optautosaveall.isChecked():
                autosavetabs = 'all'
            if self.optautosavecurrent.isChecked():
                autosavetabs = 'current'
        else:
            autosave = 'False'
        tabwidth = str(self.txttabwidth.text())
        if self.chkwordwrap.isChecked():
            wordwrap = 'True'
        else:
            wordwrap = 'False'
        if self.chkrecentfiles.isChecked():
            recentfiles = 'True'
        else:
            recentfiles = 'False'
        gcccommand = self.gcc_command_line_edit.text()
        gppcommand = self.gpp_command_line_edit.text()
        settings = '<encoding>' + encoding + '</encoding>'+ '\n<indentation>' + indent + '</indentation>'
        settings = settings + '\n<indentwidth>' + indent_width+'</indentwidth>'+'\n<incindentsymbols>'+inc_indent_syms+'</incindentsymbols>'+'\n<decindentsymbols>' +dec_indent_syms + '</decindentsymbols>'
        settings = settings + '\n<autosave>' + autosave + '</autosave>' + '\n<autosavetimeout>' + autosavetimeout + '</autosavetimeout>' + '\n<autosavetabs>' + autosavetabs + '</autosavetabs>'
        settings = settings + '\n<wordwrap>' + wordwrap + '</wordwrap>' + '\n<tabwidth>' + tabwidth + '</tabwidth>'
        settings = settings + '\n<recent files>'+recentfiles+'</recent files>'
        settings = settings +'\n<gcc>' + gcccommand + '</gcc>' +'\n<g++>' + gppcommand+'</g++>'
                               
        try:
            os.remove('./settings.ini')
        except:
            pass
            
        settingsfile = open('./settings.ini','w')
        settingsfile.write(settings)
        settingsfile.close()
        
        self.emit(QtCore.SIGNAL('closed()'))
        self.destroy()
