from PyQt4 import QtGui,QtCore
import re

class BacktraceWidget(QtGui.QTreeWidget):
    
    def __init__(self, parent = None):
        
        super(BacktraceWidget, self).__init__(parent)

        stringlist = QtCore.QStringList ()
        stringlist.append ("Level")
        stringlist.append ("Function")
        stringlist.append ("Source")
        stringlist.append ("Line")
        
        self.setHeaderLabels(stringlist)
    
    def setupListFromString(self, string):
        for s in re.findall(r'frame={.+?}', str(string)):
            start = s.find ('level="') + len('level="')
            level = s [start:s.find('"', start + 1)]
            start = s.find ('func="') + len('func="')
            func = s[start:s.find('"', start + 1)]
            start = s.find ('fullname="')
            source = ""
            line = ""
            if start != -1:
                start += len('fullname="')
                source = s[start:s.find('"', start + 1)]
                start = s.find ('line="') + len('line="')
                line = s[start:s.find('"', start + 1)]
            else:                       
                start = s.find ('from="')
                if start != -1:
                    start += len('from="')
                    source = s[start:s.find('"', start + 1)]
            
            stringlist = QtCore.QStringList ()
            stringlist.append (level)
            stringlist.append (func)
            stringlist.append (source)
            stringlist.append (line)
            item = QtGui.QTreeWidgetItem(stringlist)
            self.addTopLevelItem(item)

class BacktraceDialog(QtGui.QDialog):
    
    def __init__(self, parent = None):
        
        super(BacktraceDialog, self).__init__(parent)
        self.setWindowTitle('Backtrace')

        self.backtraceWidget = BacktraceWidget(self)
        
        self.setGeometry (100, 100, 500, 400)
        self.backtraceWidget.setGeometry (0, 0, 500, 400)   
    
    def setupListFromString(self, string):
        
        self.backtraceWidget.setupListFromString(string)
        