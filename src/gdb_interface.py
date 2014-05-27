from PyQt4 import QtGui,QtCore
from terminal_text_edit import *
from gdb_reading_thread import *
from gdb_process_terminal_dlg import ProcessTerminal
import re

class GdbConsoleDlg(QtGui.QDialog):

    def __init__(self,fd,parent=None):

        QtGui.QDialog.__init__(self,parent)
        self.setWindowTitle('GDB Console')
        self.setGeometry(100,100,600,400)
        
        self.fd = fd
        self.gdbConsoleEdit = TerminalTextEdit(self)
        self.gdbConsoleEdit.setGeometry(0,0,600,400)
        #self.setCentralWidget(self.gdbConsoleEdit)
        
        self.readingThread=ReadingThread(self.fd,self)
        self.connect(self.readingThread,QtCore.SIGNAL('readOutput(QString)'),self.readOutput)
        self.connect(self.gdbConsoleEdit,QtCore.SIGNAL('writeCommand(QString)'),self.writeCommand)

        self.readingThread.start()
        
        os.write(self.fd,'gdb --interpreter=mi\n')

        self.process_terminal = ProcessTerminal(self)
        
    def readOutput(self,string):

        string=str(string)
        self.gdbConsoleEdit.appendOutput(string)
        s = string
        d = re.findall(r'\[+.+@+.+\]+\$',string)
        if d!=[]:
            s=s.replace(d[0],'')
        for d in re.findall(r'=+.+',string):
            s = s.replace(d,'')
        for d in re.findall(r'~+.+',s):
            s=s.replace(d,'')
        for d in re.findall(r'&+.+',s):
            s=s.replace(d,'')
        for d in re.findall(r'\*+.+',s):
            s=s.replace(d,'')
        for d in re.findall(r'\(gdb\)',s):
            s=s.replace(d,'')
        for d in re.findall(r'\^+.+',s):
            s=s.replace(d,'')
            
        s=s.strip()
        self.process_terminal.appendOutput(s)

        if string.find('*stopped,reason=')!=-1:
            if string.find('reason="exited-normally"')!=-1:
                self.process_terminal.appendOutput("Process Terminated Successfully")
                self.emit(QtCore.SIGNAL('processTerminatedSuccessfully()'))

            elif string.find('*stopped,reason="breakpoint-hit"')!=-1:
                filepath = string[string.find('fullname="')+len('fullname="'):string.find('"',string.find('fullname="')+len('fullname="')+2)]
                line = int(string[string.find('line="')+len('line="'):string.find('"',string.find('line="')+len('line="')+1)])
                self.process_terminal.appendOutput('Program Stopped, Breakpoint Reached')
                self.emit(QtCore.SIGNAL('processStoppedBreakpointHit(QString,int)'),QtCore.QString(filepath),line)

            elif string.find('*stopped,reason="signal-received"')!=-1:
                signal_name = string[string.find('signal-name="')+len('signal-name="'):string.find('"',string.find('signal-name="')+len('signal-name="')+2)]
                filepath = string[string.find('fullname="')+len('fullname="'):string.find('"',string.find('fullname="')+len('fullname="')+2)]
                line = -1
                if string.find ('line="') != -1:
                    line = int(string[string.find('line="')+len('line="'):string.find('"',string.find('line="')+len('line="')+1)])
                self.process_terminal.appendOutput('Program Stopped, Signal Reached')                
                self.emit(QtCore.SIGNAL('processStoppedSignalRecieved(QString,QString,int)'),QtCore.QString(signal_name),QtCore.QString(filepath),line)
        
            else:
                self.process_terminal.appendOutput('Program Stopped, Unexpectedly')
                self.emit(QtCore.SIGNAL('processStopped()'))

        if string.find('variables=')!=-1:
            s = string[string.find('variables=')+len('variables='):]
            s=s.replace('[','',1)
            s=s.replace(']','')
            s=s.replace('(gdb)','')
            self.emit(QtCore.SIGNAL('showLocals(QString)'),QtCore.QString(s))

        elif string.find("^done,stack=[frame=") != -1:
            self.emit(QtCore.SIGNAL('showBacktrace(QString)'),QtCore.QString(string))
            
    def writeCommand(self,string):

        os.write(self.fd,str(string))

    def showProcessTerminal(self):

        self.process_terminal.show()
