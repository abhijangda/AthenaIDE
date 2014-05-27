from PyQt4 import QtCore, QtGui
from helper_functions import *

class ProjManagerDlg(QtGui.QDialog):

    def __init__(self, proj_file, parent= None):

        QtGui.QDialog.__init__(self,parent)
        self.parent = parent
        self.setWindowTitle("Project Manager")
        self.resize(769, 546)
        
        self.cmdOk = QtGui.QPushButton("Ok",self)
        self.cmdOk.setGeometry(QtCore.QRect(561, 507, 95, 31))
        self.connect(self.cmdOk, QtCore.SIGNAL('clicked()'),self.cmdOkClicked)
        
        self.cmdCancel = QtGui.QPushButton('Cancel',self)
        self.cmdCancel.setGeometry(QtCore.QRect(451, 507, 95, 31))
        self.connect(self.cmdCancel, QtCore.SIGNAL('clicked()'),self.cmdCancelClicked)
        
        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setGeometry(QtCore.QRect(5, 5, 761, 491))
        
        self.tabGeneral = QtGui.QWidget()
        
        self.cmdRemoveAll = QtGui.QPushButton("Remove All",self.tabGeneral)
        self.cmdRemoveAll.setGeometry(QtCore.QRect(650, 310, 95, 31))
        self.connect (self.cmdRemoveAll, QtCore.SIGNAL ('clicked()'), self.cmdRemoveAllClicked)
        
        self.cmdRemoveFile = QtGui.QPushButton("Remove File",self.tabGeneral)
        self.cmdRemoveFile.setGeometry(QtCore.QRect(650, 260, 95, 31))        
        self.connect (self.cmdRemoveFile, QtCore.SIGNAL ('clicked()'), self.cmdRemoveFileClicked)
        
        self.lblFiles = QtGui.QLabel("Files",self.tabGeneral)
        self.lblFiles.setGeometry(QtCore.QRect(20, 150, 67, 21))
        
        self.lblName = QtGui.QLabel("Name",self.tabGeneral)
        self.lblName.setGeometry(QtCore.QRect(20, 30, 67, 21))
        
        self.lblType_1 = QtGui.QLabel("Type",self.tabGeneral)
        self.lblType_1.setGeometry(QtCore.QRect(20, 80, 67, 21))
        
        self.lineEditName = QtGui.QLineEdit(self.tabGeneral)
        self.lineEditName.setGeometry(QtCore.QRect(100, 26, 571, 31))
        
        self.lblType = QtGui.QLabel('',self.tabGeneral)
        self.lblType.setGeometry(QtCore.QRect(100, 80, 381, 21))
        
        self.cmdAddFile = QtGui.QPushButton("Add New File",self.tabGeneral)
        self.cmdAddFile.setGeometry(QtCore.QRect(650, 160, 95, 31))
        self.connect(self.cmdAddFile,QtCore.SIGNAL('clicked()'),self.cmdAddFileClicked)
        
        self.cmdAddFiles = QtGui.QPushButton("Add Files",self.tabGeneral)
        self.cmdAddFiles.setGeometry(QtCore.QRect(650, 210, 95, 31))
        self.connect(self.cmdAddFiles,QtCore.SIGNAL('clicked()'),self.cmdAddFilesClicked)
        
        self.listViewFiles = QtGui.QListWidget(self.tabGeneral)
        self.listViewFiles.setGeometry(QtCore.QRect(100, 130, 541, 301))
        
        self.tabWidget.addTab(self.tabGeneral, "General")
        self.tabCompile = QtGui.QWidget()
        
        self.lineEditCommand = QtGui.QLineEdit(self.tabCompile)
        self.lineEditCommand.setGeometry(QtCore.QRect(110, 410, 640, 31))
        
        self.lblCommand = QtGui.QLabel("Compiler Command",self.tabCompile)
        self.lblCommand.setGeometry(QtCore.QRect(10, 413, 91, 21))
        
        self.lineEditSymbols = QtGui.QLineEdit(self.tabCompile)
        self.lineEditSymbols.setGeometry(QtCore.QRect(150, 90, 321, 31))
        
        self.chkAnsi = QtGui.QCheckBox("Support all C89 features (-ansi)",self.tabCompile)
        self.chkAnsi.setGeometry(QtCore.QRect(480, 40, 241, 26))
        self.connect(self.chkAnsi,QtCore.SIGNAL('stateChanged(int)'),self.chkAnsiStateChanged)
        
        self.chkWerror = QtGui.QCheckBox("Treats warning as errors(-Werror)",self.tabCompile)
        self.chkWerror.setGeometry(QtCore.QRect(480, 10, 261, 26))
        self.connect(self.chkWerror,QtCore.SIGNAL('stateChanged(int)'),self.chkWerrorStateChanged)
        
        self.chkS = QtGui.QCheckBox("Compile only, do not assemble or link(-S)",self.tabCompile)
        self.chkS.setGeometry(QtCore.QRect(10, 10, 301, 26))
        self.connect(self.chkS,QtCore.SIGNAL('stateChanged(int)'),self.chkSStateChanged)
        
        self.chkC = QtGui.QCheckBox("Compile and assemble, do not link(-c)",self.tabCompile)
        self.chkC.setGeometry(QtCore.QRect(480, 70, 271, 26))
        self.connect(self.chkC,QtCore.SIGNAL('stateChanged(int)'),self.chkCStateChanged)
        
        self.chkfnoasm = QtGui.QCheckBox("Disable use of inline, asm and typeof as keywords(-fno-asm)",self.tabCompile)
        self.chkfnoasm.setGeometry(QtCore.QRect(10, 50, 421, 26))
        self.connect(self.chkfnoasm,QtCore.SIGNAL('stateChanged(int)'),self.chkfnoasmStateChanged)
        
        self.chkDefineSymbols = QtGui.QCheckBox("Define Symbols",self.tabCompile)
        self.chkDefineSymbols.setGeometry(QtCore.QRect(10, 90, 131, 26))
        self.connect(self.chkDefineSymbols,QtCore.SIGNAL('stateChanged(int)'),self.chkDefineSymbolsStateChanged)
        
        self.chkO = QtGui.QCheckBox("Optimize with level (-O)",self.tabCompile)
        self.chkO.setGeometry(QtCore.QRect(480, 100, 191, 31))
        self.connect(self.chkO,QtCore.SIGNAL('stateChanged(int)'),self.chkOStateChanged)
        
        self.spinBoxOptimize = QtGui.QSpinBox(self.tabCompile)
        self.spinBoxOptimize.setGeometry(QtCore.QRect(670, 100, 59, 31))
        
        self.chkAddDirectories = QtGui.QCheckBox("Add Directories to compiler search paths ( -B <directory>)",self.tabCompile)
        self.chkAddDirectories.setGeometry(QtCore.QRect(10, 130, 411, 26))
        self.connect(self.chkAddDirectories,QtCore.SIGNAL('stateChanged(int)'),self.chkAddDirectoriesStateChanged)
        
        self.cmdAddDir = QtGui.QPushButton('Add',self.tabCompile)
        self.cmdAddDir.setGeometry(QtCore.QRect(620, 260, 95, 31))
        self.connect(self.cmdAddDir,QtCore.SIGNAL('clicked()'),self.cmdAddDirClicked)
        
        self.cmdRemoveDir = QtGui.QPushButton('Remove',self.tabCompile)
        self.cmdRemoveDir.setGeometry(QtCore.QRect(620, 200, 95, 31))
        self.connect(self.cmdRemoveDir,QtCore.SIGNAL('clicked()'),self.cmdRemoveDirClicked)
            
        self.listViewDirs = QtGui.QListWidget(self.tabCompile)
        self.listViewDirs.setGeometry(QtCore.QRect(10, 160, 591, 181))
        
        self.lineEditOtherArgs = QtGui.QLineEdit(self.tabCompile)
        self.lineEditOtherArgs.setGeometry(QtCore.QRect(110, 360, 640, 31))
        self.lineEditOtherArgs.textEdited.connect(self.lineEditOtherArgsEdited)
                                                          
        self.lblOtherArgs = QtGui.QLabel('Other Arguments',self.tabCompile)
        self.lblOtherArgs.setGeometry(QtCore.QRect(10, 350, 91, 41))
        self.lblOtherArgs.setWordWrap(True)
        
        self.tabWidget.addTab(self.tabCompile, 'Compile')
        self.tabExecution = QtGui.QWidget()
        
        self.lblParam = QtGui.QLabel('Parameters',self.tabExecution)
        self.lblParam.setGeometry(QtCore.QRect(10, 70, 67, 21))
        
        self.lineEditParams = QtGui.QLineEdit(self.tabExecution)
        self.lineEditParams.setGeometry(QtCore.QRect(140, 60, 601, 31))
        
        self.chkRunOnExternalConsole = QtGui.QCheckBox('Run on external console',self.tabExecution)
        self.chkRunOnExternalConsole.setGeometry(QtCore.QRect(10, 410, 191, 26))
        
        self.lblCurrDir = QtGui.QLabel('Current Directory',self.tabExecution)
        self.lblCurrDir.setGeometry(QtCore.QRect(10, 370, 121, 21))
        
        self.lineEditCurrDir = QtGui.QLineEdit(self.tabExecution)
        self.lineEditCurrDir.setGeometry(QtCore.QRect(140, 370, 601, 31))
        
        self.lblOutputDir = QtGui.QLabel('Output Directory',self.tabExecution)
        self.lblOutputDir.setGeometry(QtCore.QRect(10, 20, 121, 21))
        
        self.lineEditOutDir = QtGui.QLineEdit(self.tabExecution)
        self.lineEditOutDir.setGeometry(QtCore.QRect(140, 14, 601, 31))
        
        self.cmdAddEnv = QtGui.QPushButton('Add',self.tabExecution)
        self.cmdAddEnv.setGeometry(QtCore.QRect(620, 200, 95, 31))
        
        self.lblEnvVars = QtGui.QLabel(self.tabExecution)
        self.lblEnvVars.setGeometry(QtCore.QRect(10, 114, 181, 21))
        
        self.cmdRemoveEnv = QtGui.QPushButton('Remove',self.tabExecution)
        self.cmdRemoveEnv.setGeometry(QtCore.QRect(620, 240, 95, 31))
        
        self.tableEnvVar = QtGui.QTableWidget(self.tabExecution)
        self.tableEnvVar.setGeometry(QtCore.QRect(10, 140, 581, 211))
        
        self.tableEnvVar.setColumnCount(0)
        self.tableEnvVar.setRowCount(0)
        self.tabWidget.addTab(self.tabExecution, "Execution")

        self.proj_file = proj_file
        self.load_project(proj_file)

        self.lineEditOtherArgsEdited(self.lineEditOtherArgs.text())

    def cmdOkClicked(self):

        self.done(1)
        
    def cmdCancelClicked(self):

        self.done(0)

    def cmdAddFilesClicked(self):

        filenames = QtGui.QFileDialog.getOpenFileNames(self,'Open File',self.parent.current_proj.proj_path,('C Files(*.c);;C++ Files(*.cpp);;Header Files(*h);;All Files(*.*)'))
        filenames=list(filenames)
        for _file in  filenames:
            self.listViewFiles.insertItem(self.listViewFiles.count(),_file)
        
    def cmdAddFileClicked(self):

        filename = str(QtGui.QFileDialog.getSaveFileName(self,'Save File',self.parent.current_proj.proj_path,('C Files(*.c);;C++ Files(*.cpp);;Header Files(*h);;All Files(*.*)')))
        if filename!='':
            self.listViewFiles.insertItem(self.listViewFiles.count(),filename)
            
    def cmdAddDirClicked(self):

        add_dir = str(QtGui.QFileDialog.getExistingDirectory(self, 'Add Directory',''))
        if add_dir!="":
            self.listViewDirs.insertItem(self.listViewDirs.count()-1,add_dir)

    def cmdRemoveAllClicked (self):

        self.listViewFiles.clear ()

    def cmdRemoveFileClicked (self):

        self.listViewFiles.removeItemWidget(self.listViewFiles.currentItem())
        self.listViewFiles.show()
        
    def cmdRemoveDirClicked(self):

        self.listViewDirs.removeItemWidget(self.listViewDirs.currentItem())
        
    def chkAnsiStateChanged(self,state):

        text = str(self.lineEditCommand.text())
        
        if self.chkAnsi.isChecked()==False:
            text = text.replace('-ansi','')
            self.lineEditCommand.setText(text)
        else:
            self.lineEditCommand.setText(text+' -ansi')          

    def chkWerrorStateChanged(self,state):

        text = str(self.lineEditCommand.text())
        
        if self.chkWerror.isChecked()==False:
            text = text.replace('-Werror','')
            self.lineEditCommand.setText(text)
        else:
            self.lineEditCommand.setText(text+' -Werror')
            
    def chkSStateChanged(self,state):

        text = str(self.lineEditCommand.text())
        
        if self.chkS.isChecked()==False:
            text = text.replace('-S','')
            self.lineEditCommand.setText(text)
        else:
            self.lineEditCommand.setText(text+' -S')
            
    def chkCStateChanged(self,state):

        text = str(self.lineEditCommand.text())
        
        if self.chkC.isChecked()==False:
            text = text.replace('-c','')
            self.lineEditCommand.setText(text)
        else:
            self.lineEditCommand.setText(text+' -c')
            
    def chkfnoasmStateChanged(self,state):
        
        text = str(self.lineEditCommand.text())
        
        if self.chkfnoasm.isChecked()==False:
            text = text.replace('-fno-asm','')
            self.lineEditCommand.setText(text)
        else:
            self.lineEditCommand.setText(text+' -fno-asm')
            
    def chkDefineSymbolsStateChanged(self,state):

        text = str(self.lineEditCommand.text())
        
        if self.chkDefineSymbols.isChecked()==False:
            i = text.find('-',text.find('-D')+1)
            if i == -1:
                i=len(text)
            text = text.replace(text[text.find('-D'):i],'')
            self.lineEditCommand.setText(text)
        else:
            self.lineEditCommand.setText(text+' -D '+str(self.lineEditSymbols.text()))
            
    def chkOStateChanged(self,state):

        text = str(self.lineEditCommand.text())
        
        if self.chkO.isChecked()==False:
            i = text.find('-',text.find('-O')+1)
            if i == -1:
                i=len(text)
            text = text.replace(text[text.find('-O'):i],'')
            self.lineEditCommand.setText(text)
        else:
            self.lineEditCommand.setText(text+' -O'+str(self.spinBoxOptimize.value()))
            
    def chkAddDirectoriesStateChanged(self,state):

        text = str(self.lineEditCommand.text())
        
        if self.chkAddDirectories.isChecked()==False:
            i = text.find('-',text.find('-B')+1)
            if i == -1:
                i=len(text)
            text = text.replace(text[text.find('-B'):i],'')
            self.lineEditCommand.setText(text)
        else:
            s=''
            for i in range(self.listViewDirs.count()):
                s += str(self.listViewDirs.item(i).text())
            self.lineEditCommand.setText(text+' -B ' + s)

    def lineEditOtherArgsEdited(self,text):

        prev_command = str(self.lineEditCommand.text())
        command = ""
        if str(self.lblType.text())=='C Project':
            command='gcc <input> -o <output>'
        else:
            command='g++ <input> -o <output>'    
        
        if self.chkAnsi.isChecked()==True:        
            command+=' -ansi' 

        if self.chkWerror.isChecked()==True:           
           command+=' -Werror'
           
        if self.chkS.isChecked()==True:            
           command+=' -S'
           
        if self.chkC.isChecked()==True:           
           command+=' -c'
           
        if self.chkfnoasm.isChecked()==True:            
            command+=' -fno-asm'
            
        if self.chkDefineSymbols.isChecked()==True:            
            command+=' -D '+str(self.lineEditSymbols.text())
            
        if self.chkO.isChecked()==True:           
            command+=' -O'+str(self.spinBoxOptimize.value())
            
        if self.chkAddDirectories.isChecked()==True:            
            s=''
            for i in range(self.listViewDirs.count()):
                s += str(self.listViewDirs.item(i).text())
            command+=' -B ' + s

        command += str(text)
        self.lineEditCommand.setText(command)
        
    def load_project(self,proj_file):

        f = open(proj_file,'r')
        string = ''
        for s in f:
            string+=s
        f.close()

        pos_start = string.find("<name>")+6
        pos_end= string.find("</name>")    
        self.lineEditName.setText(string[pos_start:pos_end])
        
        pos_start = string.find("<type>")+6
        pos_end = string.find("</type>")    
        self.lblType.setText(string[pos_start:pos_end])      
                
        pos_start = 0
        pos_end = 0
        pos_start=string.find("<file>",pos_start+1)
        pos_end=string.find("</file>",pos_end+1)
        while  pos_start!=-1 and pos_end!=-1:
            self.listViewFiles.insertItem(self.listViewFiles.count(),string[pos_start+6:pos_end])
            pos_start=string.find("<file>",pos_start+1)
            pos_end=string.find("</file>",pos_end+1)
            
        pos_start = string.find("<run_on_ext_console>")+20
        pos_end=string.find("</run_on_ext_console>")
        self.chkRunOnExternalConsole.setChecked(str_to_bool(string[pos_start:pos_end]))
        
        pos_start = string.find("<optimize>")+10
        pos_end=string.find("</optimize>")
        self.chkO.setChecked(str_to_bool(string[pos_start:pos_end]))
        optimize = str_to_bool(string[pos_start:pos_end])
        
        if optimize==True:
            pos_start = string.find("<optimize_level>")+16
            pos_end=string.find("</optimize_level>")
            self.spinBoxOptimize.setValue(int(string[pos_start:pos_end]))
        else:
            self.spinBoxOptimize.setValue(-1)
        
        pos_start = string.find("<compile_assemble>")+18
        pos_end=string.find("</compile_assemble>")
        self.chkC.setChecked(str_to_bool(string[pos_start:pos_end]))       
        
        pos_start = string.find("<support_c89>")+13
        pos_end=string.find("</support_c89>")
        self.chkAnsi.setChecked(str_to_bool(string[pos_start:pos_end]))       
        
        pos_start = string.find("<warning_as_errors>")+19
        pos_end=string.find("</warning_as_errors>")
        self.chkWerror.setChecked(str_to_bool(string[pos_start:pos_end]))
        
        pos_start = string.find("<add_dir>")+9
        pos_end=string.find("</add_dir>")
        self.chkAddDirectories.setChecked(str_to_bool(string[pos_start:pos_end]))
        
        if str_to_bool(string[pos_start:pos_end])==True:
              
            pos_start = 0
            pos_end = 0
            pos_start=string.find("<dir>",pos_start+1)
            pos_end=string.find("</dir>",pos_end+1)
            while pos_start!=-1 and pos_end!=-1:
                self.listViewDirs.insertItem(self.listViewDirs.count()-1,string[pos_start+5:pos_end-pos_start-5])
                pos_start=string.find("<dir>",pos_start+1)
                pos_end=string.find("</dir>",pos_end+1)
                  
        pos_start = string.find("<define_symbols>")+16
        pos_end=string.find("</define_symbols>")
        self.chkDefineSymbols.setChecked(str_to_bool(string[pos_start:pos_end]))
        
        pos_start = string.find("<symbols>")+9
        pos_end=string.find("</symbols>")
        self.lineEditSymbols.setText(string[pos_start:pos_end])
        
        pos_start = string.find("<disable_inline>")+16
        pos_end=string.find("</disable_inline>")
        self.chkfnoasm.setChecked(str_to_bool(string[pos_start:pos_end]))
        
        pos_start = string.find("<compile_only>")+14
        pos_end=string.find("</compile_only>")
        self.chkS.setChecked(str_to_bool(string[pos_start:pos_end]))
        
        pos_start = string.find("<params>")+8
        pos_end=string.find("</params>")    
        self.lineEditParams.setText(string[pos_start:pos_end])
        
        pos_start = string.find("<curr_dir>")+10
        pos_end=string.find("</curr_dir>")    
        self.lineEditCurrDir.setText(string[pos_start:pos_end])      
        
        pos_start = string.find("<out_dir>")+9
        pos_end=string.find("</out_dir>")
        self.lineEditOutDir.setText(string[pos_start:pos_end])       
        
        pos_start = string.find("<other_args>")+12
        pos_end=string.find("</other_args>")
        self.lineEditOtherArgs.setText(string[pos_start:pos_end])      
        
        pos_start = 0
        pos_end = 0
        pos_start=string.find("<env>",pos_start+1)
        pos_end=string.find("</env>",pos_end+1)
        while pos_start!=-1 and pos_end!=-1:
            #self.tableEnvVar.append(env_var(string[pos_start+5,pos_end-pos_start-5]))
            pos_start=string.find("<env>",pos_start+1)
            pos_end=string.find("</env>",pos_end+1)
