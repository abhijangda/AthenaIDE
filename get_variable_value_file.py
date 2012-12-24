#31 Lines

from PyQt4 import QtGui,QtCore

class get_variable_value_dialog(QtGui.QDialog):

    def __init__(self,parent=None):

        QtGui.QDialog.__init__(self,parent)

        self.setWindowTitle('Print Variable')
        self.lblfunction = QtGui.QLabel('Variable',self)
        self.lblfunction.setGeometry(20,10,141,21)
        self.txtvariable = QtGui.QLineEdit(self)
        self.txtvariable.setGeometry(20,50,211,31)
        
        cmdcancel = QtGui.QPushButton('Cancel',self)
        cmdcancel.setGeometry(20,100,95,31)
        cmdprint = QtGui.QPushButton('Print',self)
        cmdprint.setGeometry(130,100,95,31)

        self.connect(cmdcancel,QtCore.SIGNAL('clicked()'),self.cmdcancel_clicked)
        self.connect(cmdprint,QtCore.SIGNAL('clicked()'),self.cmdprint_clicked)

    def cmdprint_clicked(self):

        self.emit(QtCore.SIGNAL('print()'))
        self.close()

    def cmdcancel_clicked(self):

        self.close()
