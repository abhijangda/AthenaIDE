#177 Lines
from PyQt4 import QtGui,QtCore
import addnewwindow

class ProjectManager(QtGui.QDialog):
    
    def __init__(self,projfilepath,parent=None):
        
        QtGui.QDialog.__init__(self,parent)
        
        self.projpath = projfilepath
        self.lblname = QtGui.QLabel("Project Name",self)
        self.txtname = QtGui.QLineEdit(self)
        self.lbltype = QtGui.QLabel("Project Type",self)
        self.txttype = QtGui.QLineEdit(self)
        self.lblfiles = QtGui.QLabel("Files",self)
        self.lstfiles = QtGui.QListWidget(self)
        self.cmdAdd = QtGui.QPushButton("Add File",self)
        self.cmdRemove = QtGui.QPushButton("Remove File",self)
        self.cmdRemoveAll = QtGui.QPushButton("Remove All",self)
        self.cmdClose = QtGui.QPushButton("Close",self)
        self.cmdOk = QtGui.QPushButton("Ok",self)
        self.cmdApply = QtGui.QPushButton("Apply",self)
        
        self.lblname.setGeometry(10,30,121,21)
        self.txtname.setGeometry(120,20,363,31)
        self.lbltype.setGeometry(10,70,101,21)
        self.txttype.setGeometry(120,66,363,31)
        self.lblfiles.setGeometry(10,110,66,21)
        self.lstfiles.setGeometry(120,110,256,221)
        self.cmdAdd.setGeometry(390,180,95,31)
        self.cmdRemove.setGeometry(390,220,95,31)
        self.cmdRemoveAll.setGeometry(390,260,95,31)
        self.cmdClose.setGeometry(170,350,95,31)
        self.cmdOk.setGeometry(280,350,95,31)
        self.cmdApply.setGeometry(390,350,95,31)
        
        self.resize(492,385)
        self.setModal(True)
        
        ###################Load Project File########################
        self.openprojfile = open(str(self.projpath),'r+')
        self.openprojstring = ''
        
        for d in self.openprojfile:
            self.openprojstring = self.openprojstring + d
        self.openprojfile.close()

        if self.projpath != '':
            self.projtype = ''
            self.projname = ''
            for i in range(self.openprojstring.index('<name>')+6, self.openprojstring.index('</name>')):
                self.projname = self.projname + self.openprojstring[i]
	    self.txtname.setText(self.projname)

            for i in range(self.openprojstring.index('<type>')+6, self.openprojstring.index('</type>')):
                self.projtype = self.projtype + self.openprojstring[i]
            self.txttype.setText(self.projtype)

            self.projfilesstartarray=[]
            self.projfilesendarray=[]
            j = 0
            index = -1
            
            try:
                for i in range(0,self.openprojstring.count('<file>')):
                    index = self.openprojstring.index('<file>',index+1,len(self.openprojstring))
                    self.projfilesstartarray.append(index)
                index = -1
                for i in range(0,self.openprojstring.count('</file>')):
                    index = self.openprojstring.index('</file>',index+1,len(self.openprojstring))
                    self.projfilesendarray.append(index)
                    
            except ValueError:
                pass
                
            self.projfilepatharray = []
            for i in range(0,len(self.projfilesendarray)):
                s = '' 
                for j in range(int(self.projfilesstartarray[i])+6,int(self.projfilesendarray[i])):
                    s = s + self.openprojstring[j]
                self.projfilepatharray.append(s)
                self.lstfiles.addItem(s)
        ######################################################
            
        self.connect(self.cmdAdd,QtCore.SIGNAL('clicked()'),self.funcadd)
        self.connect(self.cmdRemove,QtCore.SIGNAL('clicked()'),self.funcremove)
        self.connect(self.cmdRemoveAll,QtCore.SIGNAL('clicked()'),self.funcremoveall)
        self.connect(self.cmdOk,QtCore.SIGNAL('clicked()'),self.funcok)
        self.connect(self.cmdClose,QtCore.SIGNAL('clicked()'),self.funccancel)
        self.connect(self.cmdApply,QtCore.SIGNAL('clicked()'),self.funcapply)
            
    def funcadd(self):
        
        def addnew_destroy():
            
            self.lstfiles.addItem(self.addnewwin.passfilepath())
            
        def existing():
            
            if str(self.txttype.text()) == "C Project":
                self.addexistingfilepath = QtGui.QFileDialog.getOpenFileName(self,'Add File',"/home",('C Files(*.c);;Header Files(*.h);;All Files(*.*)'))
            if str(self.txttype.text()) == "C++ Project":
                self.addexistingfilepath = QtGui.QFileDialog.getOpenFileName(self,'Add File',"/home",('C++ Files(*.cpp);;Header Files(*.h);;All Files(*.*)'))
            if str(self.txttype.text()) == "C# Project":
                self.addexistingfilepath = QtGui.QFileDialog.getOpenFileName(self,'Add File',"/home",('C# Files(*.cs);;All Files(*.*)'))
            self.lstfiles.addItem(self.addexistingfilepath)
        
        def new():
            
            self.addnewwin = addnewwindow.addnewwin(dialog)
            self.connect(self.addnewwin,QtCore.SIGNAL('destroy()'),addnew_destroy)
            self.addnewwin.openaddwin(self.projpath,str(self.txttype.text()))
            
        dialog = QtGui.QDialog(self)
        label = QtGui.QLabel("You want to:",dialog)
        frame = QtGui.QFrame(dialog)
        cmdexisting = QtGui.QPushButton("Add an existing file",frame)
        cmdnew = QtGui.QPushButton("Add a new file",frame)
        self.connect(cmdexisting,QtCore.SIGNAL('clicked()'),existing)
        self.connect(cmdnew,QtCore.SIGNAL('clicked()'),new)
        hboxlayout = QtGui.QHBoxLayout(dialog)
        hboxlayout.addWidget(cmdexisting)
        hboxlayout.addWidget(cmdnew)
        frame.setLayout(hboxlayout)
        vbox = QtGui.QVBoxLayout(dialog)
        vbox.addWidget(label)
        vbox.addWidget(frame)
        dialog.show()
        
    def funcremove(self):
        
        row = self.lstfiles.currentRow()
        filelistarray = []
        for i in range(self.lstfiles.count()):
            filelistarray.append(self.lstfiles.item(i).text())
        self.lstfiles.clear()            
        for i in range(len(filelistarray)):
            if i != row:
                self.lstfiles.addItem(filelistarray[i])
    
    def funcremoveall(self):
        
        for i in range(self.lstfiles.count()):
            self.lstfiles.removeItemWidget(self.lstfiles.item(i))
    
    def save(self):
        
        self.projname = self.txtname.text()
        self.projtype = self.txttype.text()
        self.projfilepatharray = []
        for i in range(self.lstfiles.count()):
            self.projfilepatharray.append(self.lstfiles.item(i).text())
        self.openprojfile = open(str(self.projpath),'w')
        string = "<name>"+str(self.txtname.text())+"</name>\n"+"<type>"+str(self.txttype.text())+"</type>"
        for i in range(self.lstfiles.count()):
            string = string + "<file>"+self.lstfiles.item(i).text()+"</file>"
        self.openprojfile.write(string)
        self.openprojfile.close()
    
    def funcapply(self):
        
        self.save()
    
    def funcok(self):
        
        self.save()
        self.funccancel()
    
    def closeEvent(self,event):
        
        self.emit(QtCore.SIGNAL('destroy()'))
        
    def funccancel(self):
        
        self.close() 
