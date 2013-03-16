from PyQt4 import QtCore, QtGui

class BreakpointsDialog(QtGui.QDialog):
    
    def __init__(self, parent=None):

        QtGui.QDialog.__init__(self,parent)
        self.setWindowTitle("Breakpoints")
        self.parent=parent
        self.resize(600, 444)
        self.label = QtGui.QLabel('Breakpoints:',self)
        self.label.setGeometry(248,5,81,21)
        
        self.tableView = QtGui.QTableWidget(self)
        self.tableView.setGeometry(QtCore.QRect(0, 34, 597, 371))
        self.tableView.setColumnCount(8)
        self.tableView.setRowCount(0)
        self.tableView.setHorizontalHeaderLabels(['ID','File Name','Line','Function','Address','Expression','Condition','Enabled','Type'])
        
        self.cmdEnable = QtGui.QPushButton("Enable",self)
        self.cmdEnable.setGeometry(QtCore.QRect(173, 410, 95, 31))
        self.connect(self.cmdEnable,QtCore.SIGNAL('clicked()'),self.cmdEnableClicked)
        
        self.cmdDisable = QtGui.QPushButton("Disable",self)
        self.cmdDisable.setGeometry(QtCore.QRect(283, 410, 95, 31))
        self.connect(self.cmdDisable,QtCore.SIGNAL('clicked()'),self.cmdDisableClicked)
        
        self.cmdRemove = QtGui.QPushButton("Remove",self)
        self.cmdRemove.setGeometry(QtCore.QRect(393, 410, 95, 31))
        self.connect(self.cmdRemove,QtCore.SIGNAL('clicked()'),self.cmdRemoveClicked)

        self.cmdClose = QtGui.QPushButton("Close",self)
        self.cmdClose.setGeometry(QtCore.QRect(503, 410, 95, 31))
        #self.connect(self.cmdClose,QtCore.SIGNAL('clicked()'),self.done(0))

        for i,break_pt in enumerate(self.parent.list_breakpoints):
            
            self.tableView.insertRow(i)
            
            self.item = QtGui.QTableWidgetItem(str(break_pt.id))            
            self.tableView.setItem(i,0,self.item)
            
            if break_pt.type=='LineBreakpoint':
                self.item = QtGui.QTableWidgetItem()
                self.item.setText(break_pt.filename)
                self.tableView.setItem(i,1,self.item)
                self.item = QtGui.QTableWidgetItem()
                self.item.setText(break_pt.line)
                self.tableView.setItem(i,2,self.item)
                self.item = QtGui.QTableWidgetItem()
                self.item.setText('Breakpoint')
                self.tableView.setItem(i,7,self.item)
            if break_pt.type=='AddressBreakpoint':
                self.item = QtGui.QTableWidgetItem()
                self.item.setText(break_pt.address)
                self.tableView.setItem(i,4,self.item)
                self.item = QtGui.QTableWidgetItem()
                self.item.setText('Breakpoint')
                self.tableView.setItem(i,7,self.item)
            if break_pt.type=='FunctionBreakpoint':
                self.item = QtGui.QTableWidgetItem()
                self.item.setText(break_pt.func)
                self.tableView.setItem(i,3,self.item)
                self.item = QtGui.QTableWidgetItem()
                self.item.setText('Breakpoint')
                self.tableView.setItem(i,7,self.item)
            if break_pt.type=='Watchpoint':
                self.item = QtGui.QTableWidgetItem()
                self.item.setText(break_pt.condition)
                self.tableView.setItem(i,5,self.item)
                self.item = QtGui.QTableWidgetItem()
                self.item.setText('Watchpoint')
                self.tableView.setItem(i,7,item)
            if 'Catchpoint' in break_pt.type:
                self.item = QtGui.QTableWidgetItem()
                self.item.setText('Catchpoint')
                self.tableView.setItem(i,7,self.item)
                self.item = QtGui.QTableWidgetItem()
                self.item.setText(break_pt.type)
                self.tableView.setItem(i,5,self.item) 
            if break_pt.state==1:
                self.item = QtGui.QTableWidgetItem()
                self.item.setText('Enabled')
                self.tableView.setItem(i,6,self.item) 
            else:
                self.item = QtGui.QTableWidgetItem()
                self.item.setText('Disabled')
                self.tableView.setItem(i,6,self.item)
            
    def cmdEnableClicked(self):

        pass
    def cmdDisableClicked(self):
        pass
    def cmdRemoveClicked(self):
        pass
