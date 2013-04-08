from PyQt4 import QtCore, QtGui

class SetBreakpointDialog(QtGui.QDialog):
    
    def __init__(self, parent=None):

        QtGui.QDialog.__init__(self,parent)
        self.setWindowTitle("Set Breakpoint")
        
        self.resize(296, 269)
        
        self.rbFunction = QtGui.QRadioButton("Function",self)
        self.rbFunction.setGeometry(QtCore.QRect(20, 12, 108, 26))
        self.connect(self.rbFunction,QtCore.SIGNAL('toggled(bool)'),self.rbFunctionToggled)
        
        self.lineEditFunction = QtGui.QLineEdit(self)
        self.lineEditFunction.setGeometry(QtCore.QRect(180, 10, 113, 31))
        
        self.rbSourceFile = QtGui.QRadioButton("Source File",self)
        self.rbSourceFile.setGeometry(QtCore.QRect(20, 44, 108, 26))
        self.connect(self.rbSourceFile,QtCore.SIGNAL('toggled(bool)'),self.rbSourceFileToggled)
        
        self.lblFileName = QtGui.QLabel("File Name",self)
        self.lblFileName.setGeometry(QtCore.QRect(50, 84, 67, 21))
        
        self.lblLineNumber = QtGui.QLabel("Line Number",self)
        self.lblLineNumber.setGeometry(QtCore.QRect(50, 132, 81, 21))
        
        self.lineEditFileName = QtGui.QLineEdit(self)
        self.lineEditFileName.setGeometry(QtCore.QRect(180, 81, 113, 31))
        
        self.lineEditLineNumber = QtGui.QLineEdit(self)
        self.lineEditLineNumber.setGeometry(QtCore.QRect(180, 128, 113, 31))
        
        self.rbAddress = QtGui.QRadioButton("Address",self)
        self.rbAddress.setGeometry(QtCore.QRect(20, 177, 141, 26))
        self.connect(self.rbAddress,QtCore.SIGNAL('toggled(bool)'),self.rbAddressToggled)
        
        self.lineEditAddress = QtGui.QLineEdit(self)
        self.lineEditAddress.setGeometry(QtCore.QRect(180, 175, 113, 31))
        
        self.cmdSet = QtGui.QPushButton("Set",self)
        self.cmdSet.setGeometry(QtCore.QRect(199, 230, 95, 31))
        self.connect(self.cmdSet,QtCore.SIGNAL('clicked()'),self.cmdSetClicked)
        
        self.cmdCancel = QtGui.QPushButton("Cancel",self)
        self.cmdCancel.setGeometry(QtCore.QRect(93, 230, 95, 31))
        self.connect(self.cmdCancel,QtCore.SIGNAL('clicked()'),self.cmdCancelClicked)

        self.rbSourceFile.setChecked(True)
        
    def rbFunctionToggled(self, value):
        
        if value==True:
            self.lineEditFunction.setEnabled(True)
            
            self.lblFileName.setEnabled(False)
            self.lblLineNumber.setEnabled(False)
            self.lineEditLineNumber.setEnabled(False)
            self.lineEditFileName.setEnabled(False)
            
            self.lineEditAddress.setEnabled(False)
            
    def rbAddressToggled(self, value):

        if value==True:
            self.lineEditFunction.setEnabled(False)
            
            self.lblFileName.setEnabled(False)
            self.lblLineNumber.setEnabled(False)
            self.lineEditLineNumber.setEnabled(False)
            self.lineEditFileName.setEnabled(False)
            
            self.lineEditAddress.setEnabled(True)
    
    def rbSourceFileToggled(self, value):

        if value==True:
            self.lineEditFunction.setEnabled(False)
            
            self.lblFileName.setEnabled(True)
            self.lblLineNumber.setEnabled(True)
            self.lineEditLineNumber.setEnabled(True)
            self.lineEditFileName.setEnabled(True)
            
            self.lineEditAddress.setEnabled(False)
    
    def cmdSetClicked(self):

        if self.rbFunction.isChecked()==True:
            if self.lineEditFunction.text()=="":
                ask=QtGui.QMessageBox.information(self,'Debugger','Enter Function Name',QtGui.QMessageBox.Ok)
                return
            self.done(1)
            
        if self.rbSourceFile.isChecked()==True:
            if self.lineEditLineNumber.text()=="":
                ask=QtGui.QMessageBox.information(self,'Debugger','Enter Line Number',QtGui.QMessageBox.Ok)
                return
            if self.lineEditFileName.text()=="":
                ask=QtGui.QMessageBox.information(self,'Debugger','Enter File Name',QtGui.QMessageBox.Ok)
                return
            self.done(1)
            
        if self.rbAddress.isChecked()==True:
            if self.lineEditAddress.text()=="":
                ask=QtGui.QMessageBox.information(self,'Debugger','Enter Memory Address',QtGui.QMessageBox.Ok)
                return
            self.done(1)
            
    def cmdCancelClicked(self):

        self.done(0)
      
