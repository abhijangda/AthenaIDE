from PyQt4 import QtGui,QtCore
import os

class ProjectTreeItem(QtGui.QTreeWidgetItem):
    
    def __init__(self, filepath, text, *args):
        super (ProjectTreeItem, self).__init__(*args)
        self.filepath = filepath
        self.setText (0, text)
        self.setFlags (self.flags()|QtCore.Qt.ItemIsEditable)

class ProjectTreeView(QtGui.QTreeWidget):
    
    def __init__(self, parent = None, mainwin = None):
        
        super(ProjectTreeView, self).__init__(parent)
        self.itemDoubleClicked.connect(self.treeDoubleClicked)
        self.filelist = []
        self.setContextMenuPolicy (QtCore.Qt.DefaultContextMenu)
        self.popupMenu = QtGui.QMenu(self)

        addHeaderFile = QtGui.QAction("Add Header File", self)
        self.connect(addHeaderFile,QtCore.SIGNAL('triggered()'),self.addHeaderFileTriggered)

        addSourceFile = QtGui.QAction("Add Source File", self)
        self.connect(addSourceFile,QtCore.SIGNAL('triggered()'),self.addSourceFileTriggered)

        addOtherFile = QtGui.QAction("Add Other File", self)
        self.connect(addOtherFile,QtCore.SIGNAL('triggered()'),self.addOtherFileTriggered)

        self.removeFile = QtGui.QAction("Remove File", self)
        
        self.renameFile = QtGui.QAction("Rename File", self)
        self.connect(self.renameFile,QtCore.SIGNAL('triggered()'),self.renameFileTriggered)

        reloadProject = QtGui.QAction("Reload Project", self)
        findInProject = QtGui.QAction("Find in Project", self)

        closeProject = QtGui.QAction("Close Project", self)
        self.connect(closeProject,QtCore.SIGNAL('triggered()'),mainwin.close_project_triggered)

        EmptyProject = QtGui.QAction("Empty Project", self)
        self.connect(EmptyProject,QtCore.SIGNAL('triggered()'),mainwin.empty_project_triggered)

        renameProject = QtGui.QAction("Rename Project", self)

        projManager = QtGui.QAction("Open Project Manager", self)
        self.connect(projManager,QtCore.SIGNAL('triggered()'),mainwin.funcprojectmanager)

        saveProject = QtGui.QAction("Save Project", self)
        self.connect(saveProject,QtCore.SIGNAL('triggered()'),mainwin.save_project_triggered)

        saveProjectAs = QtGui.QAction("Save Project As", self)
        self.connect(saveProjectAs,QtCore.SIGNAL('triggered()'),mainwin.save_project_as_triggered)

        saveProjectCopyAs = QtGui.QAction("Save Project Copy As", self)
        self.connect(saveProjectCopyAs,QtCore.SIGNAL('triggered()'),mainwin.save_project_copy_as_triggered)

        self.popupMenu.addAction(addHeaderFile)
        self.popupMenu.addAction(addSourceFile)
        self.popupMenu.addAction(addOtherFile)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction(self.removeFile)
        self.popupMenu.addAction(self.renameFile)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction(saveProject)
        self.popupMenu.addAction(saveProjectAs)
        self.popupMenu.addAction(saveProjectCopyAs)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction(reloadProject)
        self.popupMenu.addAction(findInProject)
        self.popupMenu.addAction(closeProject)
        self.popupMenu.addAction(renameProject)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction(projManager)

    def renameFileTriggered(self):
        return
        item = self.currentItem()
        self.editItem(item, 0)

    def create_file(self, filter):
        addnewfilepath = str(QtGui.QFileDialog.getSaveFileName(self,'Save File',self.proj_path,(filter)))
        f = open (addnewfilepath, 'w')
        f.write("")
        f.close()

        return addnewfilepath

    def addHeaderFileTriggered(self):
        filepath = self.create_file ('Header Files(*.h)')
        item = ProjectTreeItem("", os.path.basename(filepath), self.headeritem)
        self.headeritem.addChild(item)
        self.emit(QtCore.SIGNAL('fileAdded(QString)'),QtCore.QString(filepath))
    
    def addSourceFileTriggered(self):
        filepath = self.create_file ('C Files(*.c);;C++ Files(*.cpp);;')
        item = ProjectTreeItem("", os.path.basename(filepath), self.sourceitem)
        self.sourceitem.addChild(item)
        self.emit(QtCore.SIGNAL('fileAdded(QString)'),QtCore.QString(filepath))
        
    def addOtherFileTriggered(self):
        filepath = self.create_file ('')
        item = ProjectTreeItem("", os.path.basename(filepath), self.otheritem)
        self.otheritem.addChild(item)
        self.emit(QtCore.SIGNAL('fileAdded(QString)'),QtCore.QString(filepath))
    
    def contextMenuEvent(self, event):
        item = self.itemAt (event.pos())
        if item.parent() != None and item.text(0) != "Header Files" and \
            item.text(0) != "Source Files" and item.text(0) != "Other Files":
            self.removeFile.setEnabled(True)
            self.renameFile.setEnabled(True)
        else:
            self.removeFile.setEnabled(False)
            self.renameFile.setEnabled(False)
            
        self.popupMenu.exec_(event.globalPos())

    def treeDoubleClicked(self, item, index):

        if os.path.isfile(item.filepath):
            self.emit(QtCore.SIGNAL('openFileTree(QString)'),
            	      QtCore.QString(item.filepath))
    
    def showFiles(self, filelist, projname, proj_path):
        self.proj_path = proj_path
        self.filelist = filelist
        item = ProjectTreeItem("", projname)
        self.addTopLevelItem(item)
        self.headeritem = ProjectTreeItem("", "Header Files", item)
        item.addChild(self.headeritem)
        self.sourceitem = ProjectTreeItem("", "Source Files", item)
        item.addChild(self.sourceitem)
        self.otheritem = ProjectTreeItem("", "Other Files", item)
        item.addChild(self.otheritem)

        for filepath in self.filelist:
            fileitem = None
            if filepath[filepath.rfind('.'):] == ".h":
                fileitem = ProjectTreeItem(filepath, os.path.basename(filepath), self.headeritem)
                self.headeritem.addChild (fileitem)
            elif filepath[filepath.rfind('.'):] == ".c" or filepath[filepath.rfind('.'):] == ".cpp":
                fileitem = ProjectTreeItem(filepath, os.path.basename(filepath), self.sourceitem)
                self.sourceitem.addChild (fileitem)
            else:
                fileitem = ProjectTreeItem(filepath, os.path.basename(filepath), self.otheritem)
                self.otheritem.addChild (fileitem)