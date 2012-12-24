#40 Lines
from PyQt4 import QtGui,QtCore

class aboutide_dialog(QtGui.QDialog):

    def __init__(self,parent = None):

        QtGui.QDialog.__init__(self,parent)
        
        self.setWindowTitle('About AthenaIDE')
        self.lblabout = QtGui.QLabel("AthenaIDE is an Integrated Development Environment\nfor C and C++. \nIt is written in Python and uses PyQt. \nDeveloped by Abhinav.\nPlease mail bugs at abhijangda@hotmail.com",self)
        self.cmdok = QtGui.QPushButton('OK',self)

        self.lblabout.setGeometry(10,10,360,131)
        self.cmdok.setGeometry(290,150,95,31)

        self.connect(self.cmdok,QtCore.SIGNAL('clicked()'),self.func_ok)

    def func_ok(self):

        self.close()
        
class aboutdb_dialog(QtGui.QDialog):

    def __init__(self,parent = None):

        QtGui.QDialog.__init__(self,parent)

        self.setWindowTitle('About AthenaDB')        
        self.lblabout = QtGui.QLabel("AthenaDB is a GUI front end for gdb \nand is part of AthenaIDE. \nIt is written in Python and uses PyQt. \nDeveloped by Abhinav.\nPlease mail bugs at abhijangda@hotmail.com",self)
        self.cmdok = QtGui.QPushButton('OK',self)

        self.lblabout.setGeometry(10,10,360,131)
        self.cmdok.setGeometry(290,150,95,31)

        self.connect(self.cmdok,QtCore.SIGNAL('clicked()'),self.func_ok)

    def func_ok(self):

        self.close()
