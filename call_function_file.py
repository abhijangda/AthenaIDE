#32 Lines
from PyQt4 import QtCore,QtGui

class call_function_dialog(QtGui.QDialog):

    def __init__(self,parent= None):

        QtGui.QDialog.__init__(self,parent)

        self.setWindowTitle('Call Function')
        self.lblfunction = QtGui.QLabel('Function to call',self)
        self.lblfunction.setGeometry(20,10,141,21)
        self.txtfunction = QtGui.QLineEdit(self)
        self.txtfunction.setGeometry(20,50,211,31)
        
        cmdcancel = QtGui.QPushButton('Cancel',self)
        cmdcancel.setGeometry(20,100,95,31)
        cmdcall = QtGui.QPushButton('Call',self)
        cmdcall.setGeometry(130,100,95,31)

        self.connect(cmdcancel,QtCore.SIGNAL('clicked()'),self.cmdcancel_clicked)
        self.connect(cmdcall,QtCore.SIGNAL('clicked()'),self.cmdcall_clicked)

    def cmdcall_clicked(self):

        self.emit(QtCore.SIGNAL('call()'))
        self.close()

    def cmdcancel_clicked(self):

        self.close()
