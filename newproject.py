#80 Lines
from PyQt4 import Qt,QtGui,QtCore

class newprojectwin(QtGui.QDialog):

    def __init__(self,parent=None):
        
        QtGui.QMainWindow.__init__(self,parent)
        
        self.canreturn = False
        self.setGeometry(50,50,811,550)
        self.setWindowTitle('New Project')
        
        lblname = QtGui.QLabel('Name',self)        
        lblsaveto = QtGui.QLabel('Save To',self)

        self.txtname = QtGui.QLineEdit('',self)        
        self.txtlocation = QtGui.QLineEdit('',self)
        self.cmdshowpath = QtGui.QPushButton('...',self)
        self.cmdCancel = QtGui.QPushButton('Cancel',self)
        self.cmdOk = QtGui.QPushButton('OK',self)
        self.lbl_proj_info = QtGui.QLabel('',self)
        
        self.list_widget_first_proj_type = QtGui.QListWidget(self)
        self.list_widget_second_proj_type = QtGui.QListWidget(self)
        
        item = QtGui.QListWidgetItem("C")        
        self.list_widget_first_proj_type.insertItem(0,item)

        item = QtGui.QListWidgetItem("C++")        
        self.list_widget_first_proj_type.insertItem(1,item)

        self.list_widget_first_proj_type.itemClicked.connect(self.list_widget_first_proj_type_item_clicked)
        self.list_widget_second_proj_type.itemClicked.connect(self.list_widget_second_proj_type_item_clicked)
        
        self.list_widget_first_proj_type.setGeometry(4,2,171,391)
        self.list_widget_second_proj_type.setGeometry(180,2,441,391)
        self.lbl_proj_info.setGeometry(630,10,171,381)
        
        lblname.setGeometry(10,412,46,21)        
        lblsaveto.setGeometry(10,452,61,21)
        
        self.txtname.setGeometry(80,410,661,31)
        self.txtlocation.setGeometry(80,450,661,31)
        self.cmdshowpath.setGeometry(750,450,51,31)
        self.cmdCancel.setGeometry(700,500,95,31)
        self.cmdOk.setGeometry(580,500,95,31)
        
        self.connect(self.cmdOk,QtCore.SIGNAL('clicked()'),self.create)
        self.connect(self.cmdCancel,QtCore.SIGNAL('clicked()'),self.cancel)
        self.connect(self.cmdshowpath,QtCore.SIGNAL('clicked()'),self.showpath)

    def list_widget_second_proj_type_item_clicked(self,item):

        self.lbl_proj_info.setAlignment(QtCore.Qt.AlignTop)
        if str(item.text())=="C Project":
            self.lbl_proj_info.setText('Create a C Project')
            self.proj_type = 'C Project'
        if str(item.text())=="C++ Project":
            self.lbl_proj_info.setText('Create a C++ Project')
            self.proj_type = 'C++ Project'
        if str(item.text())=="GTK+ Project":
            self.lbl_proj_info.setText('Create a GTK+ Project')
            self.proj_type = 'GTK+ Project'
        if str(item.text())=="gtkmm Project":
            self.lbl_proj_info.setText('Create a gtkmm Project')
            self.proj_type = 'gtkmm Project'
            
    def list_widget_first_proj_type_item_clicked(self, item):

        self.list_widget_second_proj_type.clear()
        self.list_widget_second_proj_type.setIconSize(QtCore.QSize(50,50))
        
        if str(item.text())=="C":
            item = QtGui.QListWidgetItem(QtGui.QIcon("c_file.png"),"C Project")
            self.list_widget_second_proj_type.insertItem(0,item)
            
            item = QtGui.QListWidgetItem(QtGui.QIcon("gtk.png"),"GTK+ Project")
            self.list_widget_second_proj_type.insertItem(1,item)

        else:
            item = QtGui.QListWidgetItem(QtGui.QIcon("cpp_file.png"),"C++ Project")
            self.list_widget_second_proj_type.insertItem(0,item)

            item = QtGui.QListWidgetItem(QtGui.QIcon("gtk.png"),"gtkmm Project")
            self.list_widget_second_proj_type.insertItem(1,item)
            
    def create(self):

        self.done(1)        
        
    def cancel(self):

        self.done(0)

    def showpath(self):

        filename = QtGui.QFileDialog.getExistingDirectory(self, 'Save To','')
        if filename!="":
            self.txtlocation.setText(str(filename)+'/'+str(self.txtname.text()))

    def returnprojtype(self):

        return self.projectType
