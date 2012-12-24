#77 Lines
from PyQt4 import QtGui,QtCore

class jump_win(QtGui.QDialog):

    def __init__(self,parent=None):

        QtGui.QDialog.__init__(self,parent)
        lblbreakpoint = QtGui.QLabel("Jump to",self)
        lblbreakpoint.setGeometry(20,10,131,21)
        
        self.radio_func = QtGui.QRadioButton("Function",self)
        self.radio_func.setGeometry(20,50,108,26)
        self.connect(self.radio_func,QtCore.SIGNAL('clicked()'),self.radio_func_clicked)
        self.radio_line = QtGui.QRadioButton("Line",self)
        self.radio_line.setGeometry(20,110,108,26)
        self.connect(self.radio_line,QtCore.SIGNAL('clicked()'),self.radio_line_clicked)
        self.radio_address = QtGui.QRadioButton("Address",self)
        self.connect(self.radio_address,QtCore.SIGNAL('clicked()'),self.radio_address_clicked)
        self.radio_address.setGeometry(20,220,108,26)
        
        self.txtfunc = QtGui.QLineEdit(self)
        self.txtfunc.setGeometry(190,50,181,31)
        self.txtfile = QtGui.QLineEdit(self)
        self.txtfile.setGeometry(190,110,181,31)
        self.txtline = QtGui.QLineEdit(self)
        self.txtline.setGeometry(190,160,181,31)
        self.txtaddress = QtGui.QLineEdit(self)
        self.txtaddress.setGeometry(190,220,181,31)
        lblfile = QtGui.QLabel("File",self)
        lblfile.setGeometry(100,116,66,21)
        lbllinenumber = QtGui.QLabel("Line Number",self)
        lbllinenumber.setGeometry(100,160,91,21)
        
        cmdjump = QtGui.QPushButton("Jump",self)
        cmdjump.setGeometry(261,270,111,31)
        self.connect(cmdjump,QtCore.SIGNAL('clicked()'),self.cmdjump_clicked)
        cmdcancel = QtGui.QPushButton("Cancel",self)
        cmdcancel.setGeometry(150,270,95,31)
        self.connect(cmdcancel,QtCore.SIGNAL('clicked()'),self.cmdcancel_clicked)

        self.radio_func.setChecked(True)
        self.radio_func_clicked()

    def radio_address_clicked(self):
        
        if  self.radio_address.isChecked()== True:
            self.txtaddress.setEnabled(True)
            self.txtfunc.setEnabled(False)
            self.txtfile.setEnabled(False)
            self.txtline.setEnabled(False)
            
    def radio_func_clicked(self):

        if self.radio_func.isChecked() == True:
            self.txtfunc.setEnabled(True)
            self.txtfile.setEnabled(False)
            self.txtline.setEnabled(False)           
            self.txtaddress.setEnabled(False)
            
    def radio_line_clicked(self):

        if self.radio_line.isChecked() == True:
            self.txtfile.setEnabled(True)
            self.txtline.setEnabled(True)
            self.txtfunc.setEnabled(False)        
            self.txtaddress.setEnabled(False)
            
    def cmdjump_clicked(self):

        self.emit(QtCore.SIGNAL('jump()'))
        self.destroy()

    def cmdcancel_clicked(self):

        self.close()
