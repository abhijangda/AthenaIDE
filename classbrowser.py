#35 Lines 
from PyQt4 import QtGui,QtCore

class ClassBrowser(QtGui.QDialog):

    def __init__(self,_class_list,_members_list, parent = None):

        super(ClassBrowser,self).__init__()

        self.setGeometry(100,100,558,338)
        self.setWindowTitle("Class Browser")       

        self.lblclass = QtGui.QLabel("Class",self)
        self.lblmembers = QtGui.QLabel("Members",self)
        self.lst_class = QtGui.QListWidget(self)
        self.lst_members = QtGui.QListWidget(self)

        self.lblclass.setGeometry(10,10,66,21)
        self.lblmembers.setGeometry(240,10,66,21)
        self.lst_class.setGeometry(10,40,221,291)
        self.lst_members.setGeometry(240,40,311,291)

        self.class_list = _class_list
        self.members_list = _members_list

        for i in range(len(self.class_list)):
            self.lst_class.addItem(self.class_list[i])

        self.lst_class.itemActivated.connect(self.lst_class_clicked)
        
    def lst_class_clicked(self,item):

        self.lst_members.clear()
        for i in self.members_list[self.lst_class.currentRow()]:
            self.lst_members.addItem(i)       
