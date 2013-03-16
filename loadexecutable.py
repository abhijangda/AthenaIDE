#61 Lines
from PyQt4 import QtGui,QtCore

class load_executable_window(QtGui.QDialog):

    def __init__(self,parent=None):

        QtGui.QDialog.__init__(self,parent)

        self.setWindowTitle('Load Executable File')
        
        lbl_executable = QtGui.QLabel('Executable File Path',self)
        lbl_executable.setGeometry(10,6,100,21)
        lbl_working_directory = QtGui.QLabel('Working Directory',self)
        lbl_working_directory.setGeometry(10,77,120,21)
        lbl_arguments = QtGui.QLabel('Arguments',self)
        lbl_arguments.setGeometry(10,146,100,21)
        
        self.txt_executable_path = QtGui.QLineEdit(self)
        self.txt_executable_path.setGeometry(10,37,311,31)
        self.txt_working_directory_path = QtGui.QLineEdit(self)
        self.txt_working_directory_path.setGeometry(10,108,311,31)
        self.txt_arguments_path = QtGui.QLineEdit(self)
        self.txt_arguments_path.setGeometry(10,176,311,31)

        cmd_open_executable = QtGui.QPushButton('...',self)
        cmd_open_executable.setGeometry(340,37,51,31)
        self.connect(cmd_open_executable,QtCore.SIGNAL('clicked()'),self.func_open_executable)
        cmd_working_directory = QtGui.QPushButton('...',self)
        cmd_working_directory.setGeometry(340,108,51,31)
        self.connect(cmd_working_directory,QtCore.SIGNAL('clicked()'),self.func_open_working)

        cmd_run = QtGui.QPushButton('Load',self)
        cmd_run.setGeometry(300,220,95,31)
        self.connect(cmd_run,QtCore.SIGNAL('clicked()'),self.func_run)
        cmd_cancel = QtGui.QPushButton('Cancel',self)
        cmd_cancel.setGeometry(190,220,95,31)
        self.connect(cmd_cancel,QtCore.SIGNAL('clicked()'),self.func_cancel)

    def func_open_executable(self):

        filename = str(QtGui.QFileDialog.getOpenFileName(self,'Open File'))
        if filename !='':
            self.txt_executable_path.setText(filename)
            
    def func_open_working(self):
        
        foldername = str(QtGui.QFileDialog.getExistingDirectory(self,'Open Folder'))
        if foldername !='':
            self.txt_executable_path.setText(foldername)
        
    def func_run(self):

        self.emit(QtCore.SIGNAL('run_gdb()'))
        self.destroy()
    
    def func_cancel(self):
        
        self.destroy()
    