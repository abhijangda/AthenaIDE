from PyQt4 import QtCore, QtGui

class SaveAsProjectDlg(QtGui.QDialog):
    
    def __init__(self, parent=None):

        QtGui.QDialog.__init__(self,parent)
        
        self.setWindowTitle("Save As Project")        
        self.resize(430, 125)
        
        self.cmdSaveAs = QtGui.QPushButton("Save As",self)
        self.cmdSaveAs.setGeometry(QtCore.QRect(334, 90, 95, 31))
        self.connect(self.cmdSaveAs, QtCore.SIGNAL("clicked()"),self.cmdSaveAsClicked)
        
        self.cmdCancel = QtGui.QPushButton("Cancel",self)
        self.cmdCancel.setGeometry(QtCore.QRect(233, 90, 95, 31))
        self.connect(self.cmdCancel, QtCore.SIGNAL("clicked()"),self.cmdCancelClicked)
        
        self.lblName = QtGui.QLabel("Name",self)
        self.lblName.setGeometry(QtCore.QRect(10, 15, 67, 21))
    
        self.lblLocation = QtGui.QLabel("Location",self)
        self.lblLocation.setGeometry(QtCore.QRect(10, 55, 67, 21))
   
        self.lineEditName = QtGui.QLineEdit(self)
        self.lineEditName.setGeometry(QtCore.QRect(90, 10, 281, 31))
      
        self.lineEditLocation = QtGui.QLineEdit(self)
        self.lineEditLocation.setGeometry(QtCore.QRect(90, 50, 281, 31))
  
        self.cmdShowDir = QtGui.QPushButton("...",self)
        self.cmdShowDir.setGeometry(QtCore.QRect(379, 50, 51, 31))
        self.connect(self.cmdShowDir, QtCore.SIGNAL("clicked()"),self.cmdShowDirClicked)
      
    def cmdSaveAsClicked(self):

        self.done(1)
                
    def cmdCancelClicked(self):

        self.done(0)
        
    def cmdShowDirClicked(self):

        loc = QtGui.QFileDialog.getExistingDirectory(self,"Save As",'')
        if loc!="":
            self.lineEditLocation.setText(loc)
            
