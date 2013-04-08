from PyQt4 import QtGui, QtCore

import sip,sys,os,pty,time
from PyQt4 import QtGui,QtCore
from PyQt4.Qt import QTextCursor
import select,fcntl,termios
global argv       
        
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
                self.emit(QtCore.SIGNAL('writeCommand(QString)'),cc.selectedText())
            else:
                QtGui.QTextEdit.keyPressEvent(self,event)

    def appendOutput(self,text):

        cc = self.textCursor()
        self.append(text)
        self.min_pos = cc.position()
        self.setTextCursor(cc)
        
class ProcessTerminal(QtGui.QDialog):

    def __init__(self,parent=None):

        QtGui.QDialog.__init__(self,parent)
        self.setWindowTitle('Terminal')
        self.setGeometry(100,100,600,400)

        self.terminalEdit = txtInputclass(self)
        self.terminalEdit.setGeometry(0,0,600,400)
        self.connect(self.terminalEdit,QtCore.SIGNAL('writeCommand(QString)'),self.terminalEditWriteCommand)
        self.parent=parent
        
    def appendOutput(self,text):

        self.terminalEdit.appendOutput(text)

    def terminalEditWriteCommand(self,command):

        command = str(command)
        self.parent.writeCommand(command+'\n')
        
