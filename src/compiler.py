#318 Lines
from PyQt4 import QtGui,QtCore
import subprocess,commands,runshell,threading,os,re
from only_message_box import *
import time

class Thread(threading.Thread):

    def __init__(self,command,call_back,args=[]):
        
        self._command = command
        self._call_back = call_back
        self.args = args
        super(Thread,self).__init__()
        
    def run(self):
        
        self._command(*self.args)
        self._call_back(*self.args)

class compilerclass(QtGui.QDialog):

    def __init__(self,parent = None):
        
        global g
        QtGui.QMainWindow.__init__(self,parent)
        
        self.setGeometry(50,50,600,465)
        self.setWindowTitle("Compile")
        
        self.listerroutput = QtGui.QListWidget(self)
        self.listerroutput.itemDoubleClicked.connect(self.lstitem_doubleclicked)
        
        self.lbl1 = QtGui.QLabel('Compiler',self)
        self.lbl2 = QtGui.QLabel('Source File',self)
        self.lbl3 = QtGui.QLabel('Compiled File',self)
        
        self.lblcompiler = QtGui.QLabel('',self)
        self.lblsource = QtGui.QLabel('',self)
        self.lblcompiled = QtGui.QLabel('',self)
        
        self.lbl1.setGeometry(10,20,101,17)
        self.lbl2.setGeometry(10,50,81,17)
        self.lbl3.setGeometry(10,80,91,17)
        
        self.lblcompiler.setGeometry(120,20,600,17)
        self.lblsource.setGeometry(120,50,600,17)
        self.lblcompiled.setGeometry(120,80,600,17)
        
        self.cmdClose = QtGui.QPushButton('Close',self)
        self.cmdClose.setGeometry(500,433,90,30)
        
        self.cmdRun = QtGui.QPushButton('Run',self)
        self.cmdRun.setGeometry(410,433,90,30)
        self.cmdRun.show()

        self.cmdRunDebug = QtGui.QPushButton('Run and Debug',self)
        self.cmdRunDebug.setGeometry(300,433,110,30)
        self.cmdRunDebug.show()
        
        self.connect(self.cmdRun, QtCore.SIGNAL('clicked()'),self.run)
        self.connect(self.cmdClose, QtCore.SIGNAL('clicked()'),self.cancel)
        self.connect(self.cmdRunDebug, QtCore.SIGNAL('clicked()'),self.run_debug)
        
        self.listerroutput.setGeometry(2,110,590,320)
        self.listerroutput.show()
        self.lbl1.show()
        self.lbl2.show()
        self.lbl3.show()        
        self.lblcompiler.show()
        self.lblsource.show()
        self.lblcompiled.show()
        self.gcccommand = ''
        self.gppcommand = ''
        self.compilerused =''
        self.olddir = ''
        self.previous_run = 0
        self.parent = parent
        self.projtimes=[]
        self.mode = ""
        self.run_automatically=False
        self.run_debug_automatically=False
        
    def cancel(self):
        
        self.close()
        
    def getdir(self,filename):

        a = filename.split('/')
        s = ''
        for i in range(0,len(a)-1):
            s = "%s%s%s" % (s ,a[i],'/')
        return s

    def closeEvent(self,event):

        if self.olddir.strip () != '':
            os.chdir(self.olddir)

    def run_debug(self):
        
        gdbConsoleDlg = self.parent.gdbConsoleDialog
        only_message_box = OnlyMessageBox("Setting File in GDB/MI",self)
        only_message_box.show()
        gdbConsoleDlg.gdbConsoleEdit.runCommand('file ' + self.compilefilename)
        only_message_box.setText("Setting Breakpoints")
        
        if self.mode=="File":
            for command in self.txtinputarray[self.tabs.currentIndex()].list_breakpoints_commands:
                gdbConsoleDlg.gdbConsoleEdit.runCommand(command)
                
        elif self.mode=="Project":
            gdbConsoleDlg.gdbConsoleEdit.runCommand('-exec-arguments '+ self.current_proj.params)
            gdbConsoleDlg.gdbConsoleEdit.runCommand('-environment-cd '+ self.current_proj.curr_dir)
            for txtinput in self.txtinputarray:                
                for command in txtinput.list_breakpoints_commands:
                    gdbConsoleDlg.gdbConsoleEdit.runCommand(command)
            for command in self.parent.list_gdb_commands:
                gdbConsoleDlg.gdbConsoleEdit.runCommand(command)

        only_message_box.setText("Running Program")
        only_message_box.close()
        
        gdbConsoleDlg.gdbConsoleEdit.runCommand('-exec-run')
        gdbConsoleDlg.showProcessTerminal()
        self.previous_run +=1
        
    def run(self):
        
        if self.compilefilename != '':
            self.olddir = os.getcwd()
            args = ''
            if self.mode == "Project":
                if os.path.exists(str(self.parent.current_proj.curr_dir))==False:
                    info = QtGui.QMessageBox.information(self,'Athena IDE','Current Directory specified in Project Preferences doesn\'t exists',QtGui.QMessageBox.Ok)
                    return
                os.chdir(str(self.parent.current_proj.curr_dir))
                args = self.parent.current_proj.params
                self.compilefilename += ' ' +args
            else:
                os.chdir(self.compilefilename[:self.compilefilename.rfind('/')])

            if self.parent.current_proj.run_on_ext_console==True:
                runshell.runccppprocess(self.compilefilename,self.olddir)
            else:
                runshell.run_independently(self.compilefilename,self.olddir)
        
        
    def lstitem_doubleclicked(self,item):

        text = unicode(item.text(),'utf-8')
        try:
            line_number = int(re.findall(":[0-9]*:",text)[0][1:len(re.findall(":[0-9]*:",text)[0])-1])-1
        except IndexError:
            line_number = 1
        filename = text[0:text.find(":")]
        if filename.find('/') != -1:
            filename = filename[filename.find('/')+1:]
        
        for i in range(len(self.txtinputarray)):            
            txt_filename = self.txtinputarray[i].filename
            txt_filename = txt_filename [txt_filename.rfind ('/') + 1:]            
            if txt_filename == filename:
                break
        
        if i != len(self.txtinputarray):            
            if self.tabstrackarray == []:
                self.tabs.setCurrentIndex(i)
                cc = self.txtinputarray[i].txtInput.textCursor()
                cc.setLine(line_number)
                self.txtinputarray[i].txtInput.setTextCursor(cc)
                self.txtinputarray[i].txtInput.highlightcurrentline()
            else:                
                for j in range(len(self.tabstrackarray)+1):
                    try:
                        if self.tabstrackarray[j]==i:
                            break
                    except:
                        pass
                if j != len(self.tabstrackarray):                    
                    tabindex = j
                    self.tabs.setCurrentIndex(tabindex)
                    cc = self.txtinputarray[tabindex].txtInput.textCursor()
                    cc.setLine(line_number)
                    self.txtinputarray[tabindex].txtInput.setTextCursor(cc)
                    self.txtinputarray[tabindex].txtInput.highlightcurrentline()
            
    def showerroutput(self,s):

        self.listerroutput.clear()
        err_array = s.split('\n')
        self.listerroutput.addItems(err_array)

    def gcccompiler_run_debug(self,filename,compilefilename,mode,txtinputarray,tabs,filepatharray,tabstrackarray,command=""):

        self.run_debug_automatically = True
        self.gcccompiler(filename,compilefilename,mode,txtinputarray,tabs,filepatharray,tabstrackarray,command)
        
    def gcccompiler_run(self,filename,compilefilename,mode,txtinputarray,tabs,filepatharray,tabstrackarray,command=""):

        self.run_automatically = True
        self.gcccompiler(filename,compilefilename,mode,txtinputarray,tabs,filepatharray,tabstrackarray,command)        
        
    def gcccompiler(self,filename,compilefilename,mode,txtinputarray,tabs,filepatharray,tabstrackarray,command=""):
        
        self.compilerused ='GCC'
        cmd = ''
        self.getcommand()
        self.mode = mode

        if self.gcccommand != '':            
            commandsplit = self.gcccommand.split(' ')
            self.compilefilename = ''
            self.txtinputarray = txtinputarray
            self.tabs = tabs
            self.filepatharray = filepatharray
            self.tabstrackarray = tabstrackarray           
            
            if mode == 'File':
                cmd = self.gcccommand
                cmd=cmd.replace('<input>',str(filename))
                cmd=cmd.replace('<output>',str(compilefilename))
                self.lblsource.setText(filename)
            
            if cmd !='':            
                self.compilefilename = compilefilename
                self.thread = Thread(self.runcompiler,self.callback,[cmd,compilefilename])
                self.thread.start()
                self.lblcompiler.setText('GNU C Compiler(GCC)')
                self.lblcompiled.setText(self.compilefilename)
                self.listerroutput.clear()
                self.listerroutput.addItem('Compiling, Please Wait...')
                self.show()
        else:        
            msg_box = QtGui.QMessageBox.information(self,'GNU C Compiler','Please set command for GNU C Compiler',QtGui.QMessageBox.Ok)

    def build_project(self,project,txtinputarray,tabs,tabstrackarray):

        if project.proj_path !="":
            self.project = project
            self.autogen_path = os.path.join(project.proj_path,"autogen.sh")
            self.configure_path = os.path.join(project.proj_path,"configure.ac")
            self.makefileam_path = os.path.join(project.proj_path,"Makefile.am")
            
            self.txtinputarray = txtinputarray
            self.tabs = tabs            
            self.tabstrackarray = tabstrackarray           
            
            compiler = ""
            f = open (self.configure_path, "r")
            s = f.read ()
            f.close ()
            
            if s.find ("AC_PROG_CC")!=-1:
                compiler = "GNU C Compiler(GCC) "
            if s.find ("AC_PROG_CXX")!=-1:
                compiler += "GNU C++ Compiler(G++)"
            self.lblcompiler.setText (compiler)
            compilefilename = ""
            
            f = open (self.makefileam_path, "r")
            s = f.read ()
            f.close ()
                    
            compilefilename = s [s.find ("bin_PROGRAMS")+len ("bin_PROGRAMS"):]
            compilefilename = compilefilename [:compilefilename.find ('\n')].replace ('=', '').strip ()            
            self.compilefilename = os.path.join (project.proj_path, compilefilename.split (' ') [0])           
            self.lblcompiled.setText(self.compilefilename)
            self.listerroutput.clear()
            self.listerroutput.addItem('Compiling Please Wait...')
            self.show()
            self.thread = Thread(self.begin_build,self.build_callback)
            self.thread.start()
            
    def begin_build(self):

        if self.autogen_path != '':
            curr_dir = os.getcwd()
            os.chdir(self.project.proj_path)
            p = subprocess.Popen(self.autogen_path,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            self.output = unicode(p.stderr.read(),'utf-8')            
            self.status = 0
            
            if self.output.find('configure: error: source directory already configured; run "make distclean" there first') != -1:
                p = subprocess.Popen('make distclean',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                p = subprocess.Popen(self.autogen_path,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                self.output = unicode(p.stderr.read(),'utf-8')
                if self.output.find('error:')==-1:
                    self.status = 0
            elif self.output.find('error:')!=-1:
                self.status = 1
                
            if self.status == 0:               
                p = subprocess.Popen('make',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)                
                self.output = unicode(p.stderr.read(),'utf-8')

            os.chdir(curr_dir)
           
    def build_callback(self):

        if self.output == '':
            self.showerroutput('Compilation Successful')
            #self.compilefilename = compilefilename   
            self.cmdRun.setEnabled(True)
            if self.run_automatically==True:
                self.run()
                self.run_automatically=False
            if self.run_debug_automatically==True:
                self.run_debug()
                self.run_debug_automatically=False
                
        else:
            if 'warning' in self.output and 'error' not in self.output:
                self.cmdRun.setEnabled(True)                
                self.showerroutput(self.output)        
            else:
                self.parent.compilefile = ''
                self.cmdRun.setDisabled(True)
                self.showerroutput(self.output)
        
    def callback(self,cmd,compilefilename):

        if cmd.find('-o')!=-1:
            if self.output == '':           
                self.showerroutput('Compilation Successful')
                self.compilefilename = compilefilename            
                self.cmdRun.setEnabled(True)
                if self.run_automatically==True:
                    self.run()
                    self.run_automatically=False
                if self.run_debug_automatically==True:
                    self.run_debug()
                    self.run_debug_automatically=False
                    
            else:
                if 'warning' in self.output and 'error' not in self.output:
                    self.cmdRun.setEnabled(True)                       
                    self.compilefilename = compilefilename
                    self.showerroutput(self.output)        
                else:
                    self.parent.compilefile = ''
                    self.cmdRun.setDisabled(True)
                    self.showerroutput(self.output)     
        
    def runcompiler(self,cmd,compilefilename):

        #print "running compiler with command " + cmd
        self.olddir = os.getcwd()
        compile_file_dir = compilefilename.replace('\\','')
        compile_file_dir = compile_file_dir[:compile_file_dir.rindex('/')+1]
        os.chdir(compile_file_dir)
        
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        self.output = unicode(p.stderr.read(),'utf-8')
        if self.olddir !='':
            os.chdir(self.olddir)

    def gppcompiler_run_debug(self,filename,compilefilename,mode,txtinputarray,tabs,filepatharray,tabstrackarray,projtimes=[],command=""):

        self.run_debug_automatically = True
        self.gppcompiler(filename,compilefilename,mode,txtinputarray,tabs,filepatharray,tabstrackarray,projtimes,command)        

    def gppcompiler_run(self,filename,compilefilename,mode,txtinputarray,tabs,filepatharray,tabstrackarray,projtimes=[],command=""):

        self.run_automatically = True
        self.gppcompiler(filename,compilefilename,mode,txtinputarray,tabs,filepatharray,tabstrackarray,projtimes,command)        
        
    def gppcompiler(self,filename,compilefilename,mode,txtinputarray,tabs,filepatharray,tabstrackarray,projtimes=[],command=""):
        
        self.compilerused ='G++' 
        cmd = ''
        cmd_lib='' 
        self.getcommand()
        self.mode = mode
        if self.gppcommand !='':            
            commandsplit = self.gppcommand.split(' ')
            self.compilefilename = ''
            self.txtinputarray = txtinputarray
            self.tabs = tabs
            self.filepatharray = filepatharray
            self.tabstrackarray = tabstrackarray
            
            for d in commandsplit:
                if d == '<input>':
                    cmd = cmd + ' ' + str(filename)
                if d == '<output>':
                    cmd = cmd + ' ' + str(compilefilename)
                if d != '<input>' and d != '<output>':
                    cmd = cmd + ' ' + d
            self.lblsource.setText(filename)
            self.compilefilename = compilefilename
            
            if cmd != '':
                thread = Thread(self.runcompiler,self.callback,[cmd,compilefilename])
                thread.start()                        
                self.lblcompiler.setText('GNU C++ Compiler(G++)')
                self.listerroutput.clear()
                self.lblcompiled.setText(self.compilefilename)
                self.listerroutput.addItem('Compiling, Please Wait...')
                self.show()
        else:
            msg_box = QtGui.QMessageBox.information(self,'GNU C++ Compiler','Please set command for GNU C++ Compiler',QtGui.QMessageBox.Ok)
        
    def getcommand(self):

        self.gcccommand = ''
        self.gppcommand = ''
                        
        try:
            
            settings = ''
            settingsfile = open('./settings.ini','r')
            for line in settingsfile:
                settings = settings + line
            settingsarray = settings.split(' ')
            settingsfile.close()
            
            for i in range(settings.index('<gcc>') + len('<gcc>'),settings.index('</gcc>')):
                self.gcccommand = self.gcccommand + settings[i]

            for i in range(settings.index('<g++>') + len('<g++>'),settings.index('</g++>')):
                self.gppcommand = self.gppcommand + settings[i]

        except:
            pass
