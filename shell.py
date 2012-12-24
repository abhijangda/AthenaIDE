#116 Lines
#!usr/bin/python

import sip,sys,os,pty,time
from PyQt4 import QtGui,QtCore
from PyQt4.Qt import QTextCursor
import select,fcntl,termios
global argv

class ReadingThread(QtCore.QThread):

    def __init__(self,fd,parent=None):

        QtCore.QThread.__init__(self,parent)
        self.fd=fd
        self.parent=parent

    def run(self):

        while True:
            r,w,e = select.select([self.fd],[],[])
            s=''
            d='1'
            try:                
                while d != '':                
                    d = os.read(r[0],1)
                    s+=d
            except OSError:
                pass
            self.emit(QtCore.SIGNAL('readOutput(QString)'),QtCore.QString(s))        
        
class txtInputclass(QtGui.QTextEdit):

    def __init__(self,parent=None):

        QtGui.QTextEdit.__init__(self,parent)        
        self.command = ''
        self.min_pos = 0
        self.parent = parent
        self.connect(self,QtCore.SIGNAL('cursorPositionChanged()'),self.cursorPositionChanged)

    def cursorPositionChanged(self):

        cc = self.textCursor()
        if cc.position() < self.min_pos:
            cc.setPosition(self.min_pos)
            self.setTextCursor(cc)
            
    def keyPressEvent(self,event):
        
        cc = self.textCursor()
        
        if cc.position() >= self.min_pos:
            
            if event.key() == 16777220:
                cc.setPosition(self.min_pos,cc.KeepAnchor)
                os.write(self.parent.fd,str(cc.selectedText())+'\n')
            else:
                QtGui.QTextEdit.keyPressEvent(self,event)

    def appendOutput(self,text):

        cc = self.textCursor()
        self.append(text)
        self.min_pos = cc.position()
        self.setTextCursor(cc)
        
class shell(QtGui.QMainWindow):

    def __init__(self,parent=None):
        
        return_val = pty.fork()      

        if return_val[0] == 0:
            
            os.execv("/usr/bin/bash",["/usr/bin/bash"])
            
        QtGui.QMainWindow.__init__(self,parent)
        
        self.setWindowTitle('Shell')
        self.setGeometry(50,50,600,400)

        self.txtInput = txtInputclass(self)       
        self.setCentralWidget(self.txtInput) 
        
        self.process = QtCore.QProcess(self)
        self.state = 0
        self.fd = return_val[1]
        tc_attr = termios.tcgetattr(self.fd)
        tc_attr[3] = tc_attr[3] & ~termios.ECHO
        termios.tcsetattr(self.fd,termios.TCSANOW,tc_attr)
        fl = fcntl.fcntl(self.fd,fcntl.F_GETFL)
        fcntl.fcntl(self.fd,fcntl.F_SETFL,fl|os.O_NONBLOCK)
        
        self.thread = ReadingThread(self.fd,self)
        self.connect(self.thread,QtCore.SIGNAL('readOutput(QString)'),self.readOutput)
        
        self.thread.start()    

        if len(sys.argv)>1:
            os.write(self.fd,sys.argv[1]+'\n')
            
            
    def readOutput(self,string):
        
        self.txtInput.appendOutput(string)

#def start(_argv=''):
    
#    global argv
#    argv = _argv
app = QtGui.QApplication(sys.argv)
sh = shell()
sh.show()
app.exec_()

