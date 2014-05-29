from PyQt4 import QtGui,QtCore
import os

class FileTreeWidget(QtGui.QTreeWidget):
    
    def __init__(self, parent = None):
        
        super(FileTreeWidget, self).__init__(parent)
        self.rootDir = ""
        self.topLevelItem = None
        self.itemDoubleClicked.connect(self.treeDoubleClicked)
    
    def treeDoubleClicked(self, item, index):

        path = ""
        while item != self.topLevelItem:
            path = os.path.join (str(item.text (0)), path)
            item = item.parent ()
        
        path = os.path.join(self.rootDir, path [:-1])
        if path != "" and os.path.isfile(path):
            self.emit(QtCore.SIGNAL('openFileTree(QString)'),QtCore.QString(path))

    def showDirTree(self, directory):
        self.rootDir = directory
        self.filelist = []
        self._showDirTree(directory, None)
        self.filelist.sort()
        return self.filelist
    
    def addTopLevelItem(self, item):
        self.topLevelItem = item
        super(FileTreeWidget, self).addTopLevelItem(item)

    def clear(self):
        self.topLevelItem = None
        super(FileTreeWidget, self).clear()

    def _addItem(self, directory, parent = None):
        item = QtGui.QTreeWidgetItem(None)
        item.setText(0, directory)
        if parent is None:
            if self.topLevelItem is None:
                self.addTopLevelItem(item)
            else:
                self.topLevelItem.addChild(item)
        else:
            parent.addChild(item)

        return item
    
    def _showDirTree(self, directory, item = None):
        filelist = []
        if directory [-1] == os.sep:
            directory = directory [:-1]

        _item = self._addItem(os.path.basename(directory), item)
        listdir = os.listdir(directory)
        for _dir in listdir:
            dirpath = os.path.join (directory, _dir)
            if _dir [0] == '.' or _dir[-1] == "~":
                continue
            if os.path.isdir(dirpath):
                self._showDirTree(dirpath, _item)
            else:
                #self._addItem(os.path.basename(dirpath), _item)
                filelist.append(dirpath)
                self.filelist.append (dirpath)
        filelist.sort()
        for f in filelist:
            self._addItem(os.path.basename(f), _item)