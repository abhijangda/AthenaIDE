from PyQt4 import QtGui, QtCore
import Queue,os

class TerminalTextEdit(QtGui.QTextEdit):

    def __init__(self,parent=None):

        QtGui.QTextEdit.__init__(self,parent)        
        self.command = ''
        self.min_pos = 0
        self.parent = parent
        self.connect(self,QtCore.SIGNAL('cursorPositionChanged()'),self.cursorPositionChanged)
        self.remaining_command_queue = []
        self.last_command_completed = True
        
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
                self.emit(QtCore.SIGNAL('writeCommand(QString)'),QtCore.QString(str(cc.selectedText())+'\n'))
            else:
                QtGui.QTextEdit.keyPressEvent(self,event)

    def appendOutput(self,text):

        text = str(text)
        if text.find("(gdb) (gdb)")!=-1:
            text = text.replace("(gdb) (gdb)","(gdb)")
        if text.find("(gdb)")!=-1 or text.find("y or n")!=-1:
            self.last_command_completed=True
            #print self.remaining_command_queue
            if len(self.remaining_command_queue) > 0:
                self.command = self.remaining_command_queue.pop(0)
                command = self.command
                if command[len(command)-1]!='\n':
                    command += '\n'
                self.emit(QtCore.SIGNAL('writeCommand(QString)'),command)
                self.last_command_completed=False
        cc = self.textCursor()
        self.append(text)
        self.min_pos = cc.position()
        self.setTextCursor(cc)

    def runCommand(self,command):

        if command[len(command)-1]!='\n':
            command+='\n'
            
        if self.last_command_completed==False:
            self.remaining_command_queue.append(command)
        else:
            self.command=command
            self.emit(QtCore.SIGNAL('writeCommand(QString)'),command)
            self.appendOutput(command)
        self.last_command_completed=False
