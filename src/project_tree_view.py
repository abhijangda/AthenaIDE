from PyQt4 import QtGui,QtCore
import os

class ProjectTreeItem(QtGui.QTreeWidgetItem):
    
    def __init__(self, filepath, text, *args):
        super (ProjectTreeItem, self).__init__(*args)
        self.filepath = filepath
        self.setText (0, text)

class ProjectTreeView(QtGui.QTreeWidget):
    
    def __init__(self, parent = None):
        
        super(ProjectTreeView, self).__init__(parent)
        self.itemDoubleClicked.connect(self.treeDoubleClicked)
        self.filelist = []
    
    def treeDoubleClicked(self, item, index):

        if os.path.isfile(item.filepath):
            self.emit(QtCore.SIGNAL('openFileTree(QString)'),
            	      QtCore.QString(item.filepath))
    
    def showFiles(self, filelist, projname):
        self.filelist = filelist
        item = ProjectTreeItem("", projname)
        self.addTopLevelItem(item)
        headeritem = ProjectTreeItem("", "Header Files", item)
        item.addChild(headeritem)
        sourceitem = ProjectTreeItem("", "Source Files", item)
        item.addChild(sourceitem)
        otheritem = ProjectTreeItem("", "Other Files", item)
        item.addChild(otheritem)

        for filepath in self.filelist:
            fileitem = None
            if filepath[filepath.rfind('.'):] == ".h":
                fileitem = ProjectTreeItem(filepath, os.path.basename(filepath), headeritem)
                headeritem.addChild (fileitem)
            elif filepath[filepath.rfind('.'):] == ".c" or filepath[filepath.rfind('.'):] == ".cpp":
                fileitem = ProjectTreeItem(filepath, os.path.basename(filepath), sourceitem)
                sourceitem.addChild (fileitem)
            else:
                fileitem = ProjectTreeItem(filepath, os.path.basename(filepath), otheritem)
                otheritem.addChild (fileitem)