#80 Lines
from PyQt4 import Qt,QtGui,QtCore

class newprojectwin(QtGui.QDialog):

    def __init__(self,parent=None):
        
        QtGui.QMainWindow.__init__(self,parent)
        
        self.canreturn = False
        self.setGeometry(50,50,440,297)
        self.setWindowTitle('New Project')

        name = QtGui.QLabel('Name',self)
        projecttype = QtGui.QLabel('Project Type',self)
        saveto = QtGui.QLabel('Save To',self)

        self.txtname = QtGui.QLineEdit('',self)
        self.cproject = QtGui.QRadioButton('C Project',self)
        self.cppproject = QtGui.QRadioButton('C++ Project',self)
        self.txtsavepath = QtGui.QLineEdit('',self)
        self.cmdshowpath = QtGui.QPushButton('...',self)
        self.cmdCancel = QtGui.QPushButton('Cancel',self)
        self.cmdOk = QtGui.QPushButton('OK',self)
        
        name.setGeometry(10,30,81,17)
        projecttype.setGeometry(10,90,101,17)
        saveto.setGeometry(10,210,66,17)
        self.txtname.setGeometry(80,20,281,35)
        self.cproject.setGeometry(250,90,113,22)
        self.cppproject.setGeometry(250,120,113,22)        
        self.txtsavepath.setGeometry(80,200,281,35)
        self.cmdshowpath.setGeometry(370,200,41,31)
        self.cmdCancel.setGeometry(195,260,98,31)
        self.cmdOk.setGeometry(313,260,98,31)
        
        self.connect(self.cmdOk,QtCore.SIGNAL('clicked()'),self.create)
        self.connect(self.cmdCancel,QtCore.SIGNAL('clicked()'),self.cancel)
        self.connect(self.cmdshowpath,QtCore.SIGNAL('clicked()'),self.showpath)

    def create(self):
        
        try:
            filename = self.txtsavepath.text()
            if self.cproject.isChecked() == True:
                self.projectType = 'C Project'
            if self.cppproject.isChecked() == True:
                self.projectType = 'C++ Project'
            projectstring = '<name>' + str(self.txtname.text()) + '</name>'+'\n<type>' + self.projectType + '</type>'
            savefile = open(filename,'w')
            savefile.write(projectstring)
            savefile.close()
            self.close()
            self.canreturn = True
            self.passprojname()
        except:
            pass
        
    def passprojname(self):
        
        if self.canreturn == False:
            return False
        else:
            return True
            self.canreturn = False
        
    def cancel(self):

        self.close()

    def showpath(self):

        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save To','',('All Files(*.*);;C Project Files(*.cproj);;C++ Project Files(*.cppproj)'))
        self.txtsavepath.setText(filename)

    def returnprojtype(self):

        return self.projectType
