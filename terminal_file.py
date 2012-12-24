#49 Lines
from PyQt4 import QtGui,QtCore

class TextShell(QtGui.QTextEdit):

    def __init__(self,main_window,parent=None):

        QtGui.QTextEdit.__init__(self,parent)
        self.output_cursor_pos = -1
        self.main_window = main_window
        
    def set_output(self,output):

        self.append(output)
        self.output_cursor_pos = self.textCursor().position()
        self.main_window.process.write('\n')
        
    def keyPressEvent(self,event):

        cc = self.textCursor()
        if cc.position() >= self.output_cursor_pos and self.main_window.direct_to_terminal == True:
            if event.key() == 16777220: #When Enter Key is pressed                
                    cc.setPosition(self.output_cursor_pos,cc.KeepAnchor)
                    text = unicode(cc.selectedText(),'utf-8')
                    self.main_window.process.write(text+'\n')
            QtGui.QTextEdit.keyPressEvent(self,event)
                
class terminal(QtGui.QDialog):

    def __init__(self,parent=None):

        QtGui.QDialog.__init__(self,parent)

        self.txtShell = TextShell(parent,self)     
        self.setGeometry(100,100,600,400)
        self.vbox = QtGui.QVBoxLayout(self)
        self.vbox.addWidget(self.txtShell)
        self.setLayout(self.vbox)
        self.parent = parent
        self.setWindowTitle('Terminal')
        
    def closeEvent(self,event):

        self.parent.direct_to_terminal = False
        
    def set_output_text(self,output):

        self.txtShell.set_output('\n' + output)     
