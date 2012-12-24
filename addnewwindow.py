#102 Lines
from PyQt4 import QtCore,QtGui

class addnewwin(QtGui.QDialog):

    def __init__(self,parent= None):

        QtGui.QMainWindow.__init__(self,parent)
        self.setWindowTitle('Add New File')
        self.setGeometry(50,50,400,300)
        
        filetype = QtGui.QLabel('File Type',self)
        filename = QtGui.QLabel('File Name',self)
        filepath = QtGui.QLabel('File Path',self)

        self.radiosourcefile = QtGui.QRadioButton('C/C++ File',self)
        self.radioheaderfile = QtGui.QRadioButton('Header File(*.h)',self)
        self.txtfilename = QtGui.QLineEdit('',self)
        self.txtfilepath = QtGui.QLabel('',self)
        self.cmdOk = QtGui.QPushButton('Ok',self)
        self.cmdCancel = QtGui.QPushButton('Cancel',self)
        
        filetype.setGeometry(30,20,66,17)
        filename.setGeometry(30,123,66,17)
        filepath.setGeometry(30,187,66,17)
        self.radiosourcefile.setGeometry(205,20,160,22)
        self.radioheaderfile.setGeometry(205,70,131,22)
        self.radioheaderfile.setVisible(False)
        self.txtfilename.setGeometry(130,120,231,35)
        self.txtfilepath.setGeometry(130,183,231,27)
        self.cmdOk.setGeometry(260,260,98,27)
        self.cmdCancel.setGeometry(150,260,98,27)
        self.connect(self.cmdOk,QtCore.SIGNAL('clicked()'),self.create)
        self.connect(self.cmdCancel,QtCore.SIGNAL('clicked()'),self.close)

    def openaddwin(self,projpath,projtype):

        self.projtype = projtype
        self.allowpass = False
        if projtype == 'C Project':
            self.radiosourcefile.setText('C Source File (*.c)')
            self.radioheaderfile.setVisible(True)
            self.sourcefileext = '.c'
        if projtype == 'C++ Project':
            self.radiosourcefile.setText('C++ Source File (*.cpp)')
            self.radioheaderfile.setVisible(True)
            self.sourcefileext = '.cpp'
        
        self.projfile = open(projpath,'a')
        self.projstring = ''
        d = projpath.split('/')
        self.projpath = ''
        for i in range(0,len(d) - 1):
            self.projpath = str(self.projpath) + d[i] + '/'
        self.txtfilepath.setText(self.projpath)
        self.show()
        
        
    def create(self):

        if self.radiosourcefile.isChecked() == True:
            self.txtfilepath.setText(self.projpath + str(self.txtfilename.text()) + self.sourcefileext)
            self.filepath = self.projpath + str(self.txtfilename.text()) + self.sourcefileext
            
        if self.radioheaderfile.isChecked() == True:
            self.txtfilepath.setText(self.projpath + str(self.txtfilename.text()) + '.h')
            self.filepath = self.projpath + str(self.txtfilename.text()) + '.h'

        self.projstring = '\n<file>' + self.filepath + '</file>'
        self.projfile.write(self.projstring)
        self.projfile.close()
        self.allowpassfileinf()
        self.allowpass = True
        self.projfile = open(str(self.filepath),'w')
        self.projfile.write('')
        self.projfile.close()
        self.close()

    def allowpassfileinf(self):

        if self.allowpass == True:
            return True
            self.allowpass = False
        else:
            return False
        
    def passfileinf(self):
        
        if self.radiosourcefile.isChecked() == True:
            return str(self.txtfilename.text()) + self.sourcefileext
            
        if self.radioheaderfile.isChecked() == True:
            return str(self.txtfilename.text()) + '.h'

    def passfilepath(self):

        return self.filepath      
    
    def closeEvent(self,event):
        
        self.emit(QtCore.SIGNAL('destroy()'))
