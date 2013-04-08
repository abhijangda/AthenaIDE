from PyQt4 import QtGui,QtCore

class OnlyMessageBox(QtGui.QDialog):

    def __init__(self,text,parent=None):

        QtGui.QDialog.__init__(self,parent)

        self.setGeometry(100,100,100,50)

        self.label = QtGui.QLabel(text,self)
        self.label.setGeometry(0,0,100,50)

    def setText(self,text):

        self.label.setText(text)
