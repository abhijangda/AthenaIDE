#2834 Lines
#7873 Total Lines
#!/usr/bin/python

import syntaxc,syntaxcpp
import txtinput,compiler,options,newproject,addnewwindow,projectmanager,classbrowser
import gdb_main,about_file
import sip
import sys,re
from PyQt4 import QtGui,QtCore
from PyQt4.Qt import QSyntaxHighlighter,QTextCursor,QPoint
from time import strftime
import os
import commands,threading

class Thread(threading.Thread):

    def __init__(self,command,call_back,args=[]):
        
        self._command = command
        self._call_back = call_back
        self.args = args
        super(Thread, self).__init__()
        
    def run(self):
        
        self._command(*self.args)
        self._call_back()

class athena(QtGui.QMainWindow):
    
    def __init__(self,parent = None):
        
        global filemenu,fname1,fname2,fname3,fname4,fname5        
                
        self.indent = ''
        self.gcccommand=''
        self.gppcommand=''
        self.defaultencoding=''
        self.indentwidth = ''
        self.inc_indent_syms = ''
        self.dec_indent_syms = ''
        self.autosavetimeout = ''
        self.autosavetabs = ''
        self.tabwidth = ''
        self.wordwrap = ''
        self.autosave = ''
        self.recentfiles = ''
        self.filestate =['new']
        self.f =''
        self.fpathnameindex = 0
        self.filepatharray = ['']
        self.compilefile = '' 
        self.settingschanged = False
        self.fileandext =[]
        self.encodingarray = []
        self.wordwrap = ''
        self.mode = ''
        
        self.object_classarray = []
        self.object_namearray = []
        self.save_copy = False
        self.datatypearray = ['char','double','float','int','long','void']
        self.linestrackarray = [[-1,-1,-1,-1,-1]]
        self.boollinetrack = True
        self.projCompiledTimes=[0]
        
        QtGui.QMainWindow.__init__(self,parent)
        
        self.showMaximized()
        self.setWindowTitle("AthenaIDE")
        self.setWindowIcon(QtGui.QIcon('texteditor.png'))
        
        self.projectdock = QtGui.QDockWidget(self)
        self.projectdock.setWindowTitle('')
        self.addDockWidget(0x1,self.projectdock) #Qt.LeftDockWidgetArea = 0x1
        self.projectdock.setFixedWidth(200)
        self.projectTree = QtGui.QTreeWidget(self.projectdock)
        self.projectdock.setWidget(self.projectTree)
        self.projectTree.itemDoubleClicked.connect(self.projectTreeClicked)
        self.projectTree.setHeaderLabel('Project')
        self.projectdock.hide()
        
        fileopen = QtGui.QAction(QtGui.QIcon('open.png'),'Open',self)
        self.connect(fileopen,QtCore.SIGNAL('triggered()'),self.opendialog)        
        
        filesave = QtGui.QAction(QtGui.QIcon('save.png'),'Save',self)
        self.connect(filesave,QtCore.SIGNAL('triggered()'),self.savedialog)
        filesave.setShortcut('CTRL+S')
        filesave.setStatusTip('Save the current file')
        
        filenew = QtGui.QAction(QtGui.QIcon('new.png'),'New',self)
                
        exitnt = QtGui.QAction('Exit',self)
        self.connect(exitnt,QtCore.SIGNAL('triggered()'),self.end)        

        copy = QtGui.QAction(QtGui.QIcon('copy.png'),'Copy',self)
        self.connect(copy,QtCore.SIGNAL('triggered()'),self.copy)
        copy.setShortcut('CTRL+C')
        copy.setStatusTip('Copies the currently selected text to clipboard')

        paste = QtGui.QAction(QtGui.QIcon('paste.png'),'Paste',self)
        self.connect(paste,QtCore.SIGNAL('triggered()'),self.paste)
        paste.setShortcut('CTRL+V')
        paste.setStatusTip('Paste the current text in clipboard')
        
        cut = QtGui.QAction(QtGui.QIcon('cut.png'),'Cut',self)
        self.connect(cut,QtCore.SIGNAL('triggered()'),self.cut)
        cut.setShortcut('CTRL+X')
        cut.setStatusTip('Cut the currently selected text to clipboard')
        
        undo = QtGui.QAction(QtGui.QIcon('undo.png'),'Undo',self)
        self.connect(undo,QtCore.SIGNAL('triggered()'),self.undo)
        undo.setShortcut('CTRL+Z')
        undo.setStatusTip('Undo the last operation')
        
        redo = QtGui.QAction(QtGui.QIcon('redo.png'),'Redo',self)
        self.connect(redo,QtCore.SIGNAL('triggered()'),self.redo)
        redo.setShortcut('CTRL+SHIFT+Z')
        redo.setStatusTip('Redo the last operation')
        
        selectall = QtGui.QAction(QtGui.QIcon('selectall.png'),'Select All',self)
        self.connect(selectall,QtCore.SIGNAL('triggered()'),self.selectal)
        selectall.setShortcut('CTRL+A')
        selectall.setStatusTip('Selects all the text')
        
        datentime = QtGui.QAction('Insert Date and Time',self)
        self.connect(datentime,QtCore.SIGNAL('triggered()'),self.dattime)

        find = QtGui.QAction(QtGui.QIcon('find.png'),'Find',self)
        self.connect(find,QtCore.SIGNAL('triggered()'),self.openfind)
        find.setShortcut('CTRL+F')
        find.setStatusTip('Find text in current file')

        findandreplace = QtGui.QAction(QtGui.QIcon('findandreplace.png'),'Find And Replace',self)
        self.connect(findandreplace,QtCore.SIGNAL('triggered()'),self.openfindandreplace)
        findandreplace.setShortcut('CTRL+R')
        findandreplace.setStatusTip('Find and Replace text in current file')
        
        findselectedtext = QtGui.QAction('Find Selected Text',self)
        self.connect(findselectedtext,QtCore.SIGNAL('triggered()'),self.funcfindselected)
        findselectedtext.setShortcut('CTRL+SHIFT+F')
        findselectedtext.setStatusTip('Find currently selected text in current file')
        
        findinfile = QtGui.QAction('Find in file',self)
        self.connect(findinfile,QtCore.SIGNAL('triggered()'),self.funcfindinfile)
        findinfile.setStatusTip('Find text in a file')
        
        regexpsearch = QtGui.QAction('Regular Expression Search',self)
        self.connect(regexpsearch,QtCore.SIGNAL('triggered()'),self.funcregexpsearch)
        regexpsearch.setShortcut('CTRL+SHIFT+R')
        regexpsearch.setStatusTip('Search regular expression in current file')
        
        changefont = QtGui.QAction('Font',self)
        self.connect(changefont,QtCore.SIGNAL('triggered()'),self.font)

        changecolor = QtGui.QAction('Text Color',self)
        self.connect(changecolor,QtCore.SIGNAL('triggered()'),self.color)

        mnuincindent = QtGui.QAction(QtGui.QIcon('indent.png'),'Increase Indent',self)
        self.connect(mnuincindent,QtCore.SIGNAL('triggered()'),self.incindent)
        mnuincindent.setShortcut('CTRL+]')
        mnuincindent.setStatusTip('Increase Indent of currently selected region')
        
        mnudecindent = QtGui.QAction(QtGui.QIcon('dedent.png'),'Decrease Indent',self)
        self.connect(mnudecindent,QtCore.SIGNAL('triggered()'),self.decindent)
        mnudecindent.setShortcut('CTRL+[')
        mnudecindent.setStatusTip('Decrease Indent of currently selected region')
        
        mnuaddcppcomment = QtGui.QAction('Add Comment',self)
        self.connect(mnuaddcppcomment,QtCore.SIGNAL('triggered()'),self.addcppcomment)
        mnuaddcppcomment.setStatusTip('Add a comment to current file')
        
        commentout_multiline = QtGui.QAction(QtGui.QIcon('commentout.png'),'Comment Out Region',self)
        self.connect(commentout_multiline,QtCore.SIGNAL('triggered()'),self.funccommentout)
        commentout_multiline.setShortcut('CTRL+SHIFT+C')
        commentout_multiline.setStatusTip('Comment out the currently selected text')
        
        uncommentout_multiline = QtGui.QAction(QtGui.QIcon('uncommentout.png'),'Uncomment Out Region',self)
        self.connect(uncommentout_multiline, QtCore.SIGNAL('triggered()'),self.funcuncommentout)
        uncommentout_multiline.setShortcut('CTRL+SHIFT+U')
        uncommentout_multiline.setStatusTip('Uncomment out the currently selected text')
        
        tabifyregion = QtGui.QAction('Tabify Region',self)
        self.connect(tabifyregion, QtCore.SIGNAL('triggered()'),self.functabifyregion)
        tabifyregion.setShortcut('CTRL+SHIFT+T')
        tabifyregion.setStatusTip('Replaces Spaces with Tabs according to Tab Width')
        
        untabifyregion = QtGui.QAction('Untabify Region',self)
        self.connect(untabifyregion, QtCore.SIGNAL('triggered()'),self.funcuntabifyregion)
        untabifyregion.setShortcut('CTRL+SHIFT+R')
        untabifyregion.setStatusTip('Replaces Tabs with Spaces according to Tab Width')
        
        uppercaseselection = QtGui.QAction('Uppercase Selection',self)
        self.connect(uppercaseselection, QtCore.SIGNAL('triggered()'),self.funcuppercaseselection)
        uppercaseselection.setShortcut('CTRL+SHIFT+O')
        uppercaseselection.setStatusTip('Uppercase each character in the selected text')
        
        lowercaseselection = QtGui.QAction('Lowercase Selection',self)
        self.connect(lowercaseselection, QtCore.SIGNAL('triggered()'),self.funclowercaseselection)
        lowercaseselection.setShortcut('CTRL+SHIFT+L')
        lowercaseselection.setStatusTip('Lowercase each character in the selected text')
        
        striptrailingspaces = QtGui.QAction('Strip Trailing Whitespaces',self)
        self.connect(striptrailingspaces,QtCore.SIGNAL('triggered()'),self.funcstriptrailingspaces)
        striptrailingspaces.setShortcut('CTRL+SHIFT+S')
        striptrailingspaces.setStatusTip('Strip Trailing spaces in the file')
        
        self.statusBar().showMessage('Char 0 Col 0 Line 0')
        
        txtInput0 = txtinput.codewidget("",self)
        self.connect(txtInput0.txtInput, QtCore.SIGNAL('textChanged()'),self.textchanged)
        self.connect(txtInput0.txtInput, QtCore.SIGNAL('cursorPositionChanged()'),self.OnMousePressed)
        
        filesaveas = QtGui.QAction(QtGui.QIcon('saveas.png'),'Save As',self)
        self.connect(filesaveas,QtCore.SIGNAL('triggered()'),self.saveas)
        filesaveas.setShortcut('CTRL+SHIFT+S')
        filesaveas.setStatusTip('SaveAs the current file')
        
        filesaveall = QtGui.QAction("Save All",self)
        self.connect(filesaveall,QtCore.SIGNAL('triggered()'),self.funcsaveall)
        
        filesaveallas = QtGui.QAction("Save All As",self)
        self.connect(filesaveall,QtCore.SIGNAL('triggered()'),self.funcsaveallas)
        
        filesavecopyas = QtGui.QAction("Save Copy As",self)
        self.connect(filesaveall,QtCore.SIGNAL('triggered()'),self.funcsavecopyas)
        
        eXit = QtGui.QAction(QtGui.QIcon('exit.png'),'Exit',self) 
        self.connect(eXit,QtCore.SIGNAL('triggered()'),self.end)
        eXit.setShortcut('CTRL+Q')
        eXit.setStatusTip('Exits Athena')
        
        fileprint = QtGui.QAction(QtGui.QIcon('print.png'),'Print',self)
        self.connect(fileprint,QtCore.SIGNAL('triggered()'),self.funcprint)
        fileprint.setShortcut('CTRL+P')
        fileprint.setStatusTip('Print the current file')
        
        newtab = QtGui.QAction('New Tab',self)
        self.connect(newtab,QtCore.SIGNAL('triggered()'),self.funcnewtab)

        removetab = QtGui.QAction('Remove Current Tab',self)
        self.connect(removetab,QtCore.SIGNAL('triggered()'),self.funcremovetab)

        removealltab = QtGui.QAction('Remove All Tabs',self)
        self.connect(removealltab,QtCore.SIGNAL('triggered()'),self.funcremovealltab)

        fname1 =  QtGui.QAction('',self)
        self.connect(fname1,QtCore.SIGNAL('triggered()'),self.funcfname1)

        fname2 = QtGui.QAction('',self)
        self.connect(fname2,QtCore.SIGNAL('triggered()'),self.funcfname2)

        fname3 = QtGui.QAction('',self)
        self.connect(fname3,QtCore.SIGNAL('triggered()'),self.funcfname3)

        fname4 = QtGui.QAction('',self)
        self.connect(fname4,QtCore.SIGNAL('triggered()'),self.funcfname4)
        
        fname5 = QtGui.QAction('',self)
        self.connect(fname5,QtCore.SIGNAL('triggered()'),self.funcfname5)

        showoptions = QtGui.QAction(QtGui.QIcon('options.png'),'Options',self)
        self.connect(showoptions,QtCore.SIGNAL('triggered()'),self.funcoptions)
        
        toolbarrun = QtGui.QAction(QtGui.QIcon('run.png'),'Run',self)
        self.connect(toolbarrun,QtCore.SIGNAL('triggered()'),self.toolbarrun)
        toolbarrun.setShortcut('F5')
        toolbarrun.setStatusTip('Run')
        
        toolbarcompile = QtGui.QAction(QtGui.QIcon('compile.png'),'Compile And Run', self)
        self.connect(toolbarcompile,QtCore.SIGNAL('triggered()'),self.toolbarcompile)
        toolbarcompile.setShortcut('SHIFT+F5')
        toolbarcompile.setStatusTip('Compile')
        
        self.arrfname = [fname1,fname2,fname3,fname4,fname5]
        
        self.arrfpathname = []
        
        cmdgcccompile = QtGui.QAction('Compile with GCC',self)
        self.connect(cmdgcccompile,QtCore.SIGNAL('triggered()'),self.rungcccompiler) 

        cmdgppcompile = QtGui.QAction('Compile with G++',self)
        self.connect(cmdgppcompile,QtCore.SIGNAL('triggered()'),self.rungppcompiler)

        menubar = self.menuBar()

        self.cmbencoding = QtGui.QComboBox(self.statusBar())
        self.cmbencoding.addItems(['Plain Text','C','C++'])
        self.connect(self.cmbencoding,QtCore.SIGNAL('currentIndexChanged(QString)'),self.changeencoding)
        
        newprojectaction = QtGui.QAction('New Project',self)
        newprojectaction.setShortcut('CTRL+SHIFT+N')
        newprojectaction.setStatusTip('Create a New Project')
        
        newfileaction = QtGui.QAction('New File',self)
        newfileaction.setShortcut('CTRL+N')
        newfileaction.setStatusTip('Create a New File')
        
        self.addnew = QtGui.QAction('Add New File',self)
        self.addexisting = QtGui.QAction('Add Existing File',self)
        self.addnew.setEnabled(False)
        self.addexisting.setEnabled(False)
        openproj = QtGui.QAction('Open Project',self)
        openproj.setShortcut('Ctrl+SHIFT+O')
        openproj.setStatusTip('Open a Project')
        openfile = QtGui.QAction('Open File',self)
        openfile.setShortcut('Ctrl+O')
        openfile.setStatusTip('Open a File')
        
        autoindent = QtGui.QAction('Auto Indent',self)
        runterminal = QtGui.QAction('Run Terminal',self)
        runterminal.setStatusTip('Run GNOME Terminal')
        rungdb = QtGui.QAction('Debug using GNU Project Debugger(gdb)',self)
        rungdb.setShortcut('SHIFT+F9')
        rungdb.setStatusTip('Debug with a gdb command line')
        
        classbrowser = QtGui.QAction('Class Browser',self)
        gotoline = QtGui.QAction('Go To Line',self)
        gotoline.setShortcut('Alt+G')
        gotoline.setStatusTip('GoTo a specified line in the current file')
        projectmanager = QtGui.QAction('Project Manager',self)
        projectmanager.setStatusTip('Edit Project Name, Type and Files')
        
        self.connect(newprojectaction,QtCore.SIGNAL('triggered()'),self.funcnewproject)
        self.connect(newfileaction,QtCore.SIGNAL('triggered()'),self.new)
        self.connect(self.addnew,QtCore.SIGNAL('triggered()'),self.funcaddnew)
        self.connect(self.addexisting, QtCore.SIGNAL('triggered()'),self.funcaddexisting)
        self.connect(openfile,QtCore.SIGNAL('triggered()'),self.opendialog)
        self.connect(openproj,QtCore.SIGNAL('triggered()'),self.funcopenproj)
        self.connect(autoindent,QtCore.SIGNAL('triggered()'),self.funcautoindent)
        self.connect(runterminal,QtCore.SIGNAL('triggered()'),self.funcrunterminal)
        self.connect(rungdb,QtCore.SIGNAL('triggered()'),self.funcrungdb)
        self.connect(gotoline,QtCore.SIGNAL('triggered()'),self.funcgotoline)        
        self.connect(classbrowser,QtCore.SIGNAL('triggered()'),self.funcclassbrowser)
        self.connect(projectmanager,QtCore.SIGNAL('triggered()'),self.funcprojectmanager)
        
        newmenu = QtGui.QMenu('New',self)
        newmenu.addAction(newfileaction)
        newmenu.addAction(newprojectaction)
        addmenu = QtGui.QMenu('Add',self)
        addmenu.addAction(self.addnew)
        addmenu.addAction(self.addexisting)
        openmenu = QtGui.QMenu('Open',self)
        openmenu.addAction(openproj)
        openmenu.addAction(openfile)
        fileopen.setMenu(openmenu)
        
        filemenu = menubar.addMenu('&File')
        filemenu.addMenu(newmenu)
        filemenu.addAction(newtab)
        filemenu.addMenu(addmenu)
        filemenu.addMenu(openmenu)
        filemenu.addSeparator()
        filemenu.addAction(filesave)
        filemenu.addAction(filesaveas)
        filemenu.addAction(filesaveall)
        filemenu.addAction(filesaveallas)
        filemenu.addAction(filesavecopyas)
        filemenu.addSeparator()
        filemenu.addAction(fileprint)
        filemenu.addAction(removetab)
        filemenu.addAction(removealltab)
        filemenu.addAction(eXit)
        filemenu.addSeparator()
                
        editmenu = menubar.addMenu('&Edit')
        editmenu.addAction(undo)
        editmenu.addAction(redo)
        editmenu.addSeparator()
        editmenu.addAction(cut)
        editmenu.addAction(copy)
        editmenu.addAction(paste)
        editmenu.addAction(selectall)
        editmenu.addSeparator()
        editmenu.addAction(find)
        editmenu.addAction(findandreplace)
        editmenu.addAction(findinfile)
        editmenu.addAction(findselectedtext)
        editmenu.addAction(regexpsearch)
        editmenu.addSeparator()
        editmenu.addAction(datentime)
        
        formatmenu = menubar.addMenu('F&ormat')
        formatmenu.addAction(changefont)
        formatmenu.addAction(changecolor)
        formatmenu.addSeparator() 
        formatmenu.addAction(mnuincindent)
        formatmenu.addAction(mnudecindent)
        formatmenu.addSeparator()
        formatmenu.addAction(mnuaddcppcomment)       
        formatmenu.addAction(commentout_multiline)
        formatmenu.addAction(uncommentout_multiline)
        formatmenu.addSeparator()
        formatmenu.addAction(tabifyregion)
        formatmenu.addAction(untabifyregion)
        formatmenu.addSeparator()
        formatmenu.addAction(uppercaseselection)
        formatmenu.addAction(lowercaseselection)
        formatmenu.addSeparator()
        formatmenu.addAction(striptrailingspaces)
        
        self.navigationmenu = menubar.addMenu('Navi&gaton')
        back_line = QtGui.QAction(QtGui.QIcon('backline'),'Back',self)
        back_line.setShortcut(QtCore.Qt.ALT+QtCore.Qt.Key_Left)
        back_line.setStatusTip('Go to previous line in line history')
        forward_line = QtGui.QAction(QtGui.QIcon('nextline'),'Forward',self)
        forward_line.setShortcut(QtCore.Qt.ALT+QtCore.Qt.Key_Right)
        forward_line.setStatusTip('Go to next line in line history')
        last_line = QtGui.QAction(QtGui.QIcon('lastline'),'End of file',self)
        last_line.setShortcut(QtCore.Qt.ALT+QtCore.Qt.Key_Down)
        last_line.setStatusTip('Go to last line in the file')
        first_line = QtGui.QAction(QtGui.QIcon('firstline'),'Start of file',self)
        first_line.setShortcut(QtCore.Qt.ALT+QtCore.Qt.Key_Up)
        first_line.setStatusTip('Go to first line')
        add_bookmark = QtGui.QAction(QtGui.QIcon('bookmarksadd.png'),'Add Bookmark',self)
        add_bookmark.setShortcut(QtCore.Qt.CTRL+QtCore.Qt.Key_B)
        add_bookmark.setStatusTip('Add current line to bookmark')
        next_bookmark = QtGui.QAction(QtGui.QIcon('bookmarksnext.png'),'Next Bookmark',self)
        next_bookmark.setShortcut(QtCore.Qt.CTRL+QtCore.Qt.Key_Right)
        next_bookmark.setStatusTip('Go to next line in bookmarks')
        prev_bookmark = QtGui.QAction(QtGui.QIcon('bookmarksprev.png'),'Previous Bookmark',self)
        prev_bookmark.setShortcut(QtCore.Qt.CTRL+QtCore.Qt.Key_Left)
        prev_bookmark.setStatusTip('Go to previous line in bookmarks')
        clear_bookmark = QtGui.QAction(QtGui.QIcon('bookmarksclear.png'),'Clear Bookmarks',self)
        clear_bookmark.setShortcut(QtCore.Qt.CTRL+QtCore.Qt.Key_Delete)
        clear_bookmark.setStatusTip('Clear all bookmarks')
        self.bookmark_actiongroup = QtGui.QActionGroup(self)
        
        self.bookmark_menu_item_array = []
        self.bookmark_line_array = []
        self.bookmark_tabsindex_array = []
        self.bookmark_index = -1
        
        self.navigationmenu.addAction(back_line)
        self.navigationmenu.addAction(forward_line)
        self.navigationmenu.addSeparator()
        self.navigationmenu.addAction(first_line)
        self.navigationmenu.addAction(last_line)
        self.navigationmenu.addSeparator()
        self.navigationmenu.addAction(gotoline)
        self.navigationmenu.addSeparator()
        self.navigationmenu.addAction(add_bookmark)
        self.navigationmenu.addAction(next_bookmark)
        self.navigationmenu.addAction(prev_bookmark)
        self.navigationmenu.addAction(clear_bookmark)
        self.navigationmenu.addSeparator()
        
        self.connect(back_line,QtCore.SIGNAL('triggered()'),self.funcbackline)
        self.connect(forward_line,QtCore.SIGNAL('triggered()'),self.funcforwardline)
        self.connect(last_line,QtCore.SIGNAL('triggered()'),self.funclastline)
        self.connect(first_line,QtCore.SIGNAL('triggered()'),self.funcfirstline)
        self.connect(add_bookmark,QtCore.SIGNAL('triggered()'),self.funcaddbookmark)
        self.connect(prev_bookmark,QtCore.SIGNAL('triggered()'),self.funcprevbookmark)
        self.connect(next_bookmark,QtCore.SIGNAL('triggered()'),self.funcnextbookmark)
        self.connect(clear_bookmark,QtCore.SIGNAL('triggered()'),self.funcclearbookmark)
        
        compilemenu = menubar.addMenu('&Compile')
        compilemenu.addAction(cmdgcccompile)
        compilemenu.addSeparator()
        compilemenu.addAction(cmdgppcompile)
        toolbarcompile.setMenu(compilemenu)
        filenew.setMenu(newmenu)

        gui_gdb = QtGui.QAction('Debug with AthenaDB',self)
        gui_gdb.setShortcut('F9')
        gui_gdb.setStatusTip('Debug with AthenaDB, a gdb GUI Front End')
        self.connect(gui_gdb,QtCore.SIGNAL('triggered()'),self.func_gui_gdb)
        debugmenu = menubar.addMenu('Debug')
        debugmenu.addAction(gui_gdb)
        debugmenu.addAction(rungdb)

        toolsmenu = menubar.addMenu('&Tools')
        toolsmenu.addAction(showoptions)
        toolsmenu.addAction(autoindent)
        toolsmenu.addAction(runterminal)        
        toolsmenu.addAction(projectmanager)
        toolsmenu.addAction(classbrowser)

        helpmenu = menubar.addMenu('&Help')
        aboutide = QtGui.QAction('About AthenaIDE',self)
        self.connect(aboutide,QtCore.SIGNAL('triggered()'),self.func_aboutide)
        helpmenu.addAction(aboutide)        
        aboutdb = QtGui.QAction('About AthenaDB',self)
        self.connect(aboutdb,QtCore.SIGNAL('triggered()'),self.func_aboutdb)
        helpmenu.addAction(aboutdb)
        toolbar = self.addToolBar('CToolbar')
        toolbar.addAction(filenew)
        toolbar.addAction(fileopen)
        toolbar.addAction(filesave)
        toolbar.addAction(filesaveas)
        toolbar.addAction(fileprint)
        toolbar.addSeparator()
        toolbar.addAction(undo)
        toolbar.addAction(redo)
        toolbar.addAction(cut)
        toolbar.addAction(copy)
        toolbar.addAction(paste)
        toolbar.addAction(selectall)
        toolbar.addAction(find)
        toolbar.addAction(findandreplace)
        toolbar.addSeparator()
        toolbar.addAction(mnuincindent)        
        toolbar.addAction(mnudecindent)
        toolbar.addAction(commentout_multiline)
        toolbar.addAction(uncommentout_multiline)
        toolbar.addSeparator()
        toolbar.addAction(toolbarcompile)
        toolbar.addAction(toolbarrun)
        toolbar.addSeparator()
        toolbar.addAction(back_line)
        toolbar.addAction(forward_line)
        toolbar.addAction(last_line)
        toolbar.addAction(first_line)
        toolbar.addSeparator()        
        toolbar.addAction(add_bookmark)
        toolbar.addAction(next_bookmark)
        toolbar.addAction(prev_bookmark)
        toolbar.addAction(clear_bookmark)
        toolbar.addSeparator()
        toolbar.addAction(showoptions)
        toolbar.addAction(eXit)
        
        self.statusBar().addPermanentWidget(self.cmbencoding)
        self.cmbencoding.show()
        self.winfind = QtGui.QDialog(self)
        self.winfindandreplace = QtGui.QMainWindow(self)
        self.winfindinfile = QtGui.QDialog(self)
        self.winaddcppcomment = QtGui.QMainWindow(self)
        self.winaddccomment = QtGui.QMainWindow(self)
        
        page1 = QtGui.QWidget()
        self.tabs = QtGui.QTabWidget()
        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(txtInput0)
        page1.setLayout(vbox1)
        self.txtarray = [txtInput0]
        self.mode='File'
        
        self.tabs.addTab(page1,'')
        self.setCentralWidget(self.tabs)
        self.tabs.setTabText(self.tabs.currentIndex(),'New File')
        self.tabs.hide()
        
        self.runcompiler = compiler.compilerclass(self)
        self.autosaveTimer = QtCore.QTimer(self)
        try:
            settings = ''
            settingsfile = open('./settings.ini','r')
            for line in settingsfile:
                settings = settings + line
            
            settingsfile.close()

            for i in range(settings.index('<indentwidth>')+len('<indentwidth>'),settings.index('</indentwidth>')):
                self.indentwidth = self.indentwidth + settings[i]
                
            for i in range(settings.index('<incindentsymbols>')+len('<incindentsymbols>'),settings.index('</incindentsymbols>')):
                self.inc_indent_syms = self.inc_indent_syms + settings[i]
                
            for i in range(settings.index('<decindentsymbols>')+len('<decindentsymbols>'),settings.index('</decindentsymbols>')):
                self.dec_indent_syms = self.dec_indent_syms + settings[i]

            for i in range(settings.index('<autosave>')+len('<autosave>'),settings.index('</autosave>')):
                self.autosave = self.autosave + settings[i]
                
            for i in range(settings.index('<autosavetimeout>')+len('<autosavetimeout>'),settings.index('</autosavetimeout>')):
                self.autosavetimeout = self.autosavetimeout + settings[i]
                
            for i in range(settings.index('<autosavetabs>')+len('<autosavetabs>'),settings.index('</autosavetabs>')):
                self.autosavetabs = self.autosavetabs + settings[i]

            if self.autosave=='True':
                self.funcstartautosave()
                
            for i in range(settings.index('<wordwrap>')+len('<wordwrap>'),settings.index('</wordwrap>')):
                self.wordwrap = self.wordwrap + settings[i]

            for i in range(settings.index('<tabwidth>')+len('<tabwidth>'),settings.index('</tabwidth>')):
                self.tabwidth = self.tabwidth + settings[i]

            for i in range(settings.index('<encoding>')+len('<encoding>'),settings.index('</encoding>')):
                self.defaultencoding = self.defaultencoding + settings[i]
                
            for i in range(settings.index('<indentation>')+len('<indentation>'),settings.index('</indentation>')):
                self.indent = self.indent + settings[i]
                
            for i in range(settings.index('<recent files>')+len('<recent files>'),settings.index('</recent files>')):
                self.recentfiles = self.recentfiles + settings[i]
                
            for i in range(settings.index('<gcc>') + len('<gcc>'),settings.index('</gcc>')):
                self.gcccommand = self.gcccommand + settings[i]

            for i in range(settings.index('<g++>') + len('<g++>'),settings.index('</g++>')):
                self.gppcommand = self.gppcommand + settings[i]

            if self.defaultencoding == 'C':
                highlight = syntaxc.CHighlighter(self.txtarray[0].txtInput.document())
                
            if self.defaultencoding == 'C++':
                highlight = syntaxcpp.CPPHighlighter(self.txtarray[0].txtInput.document())

        except:
            pass
        
        self.addtoencodingarray(0,self.defaultencoding)

        if self.defaultencoding == 'PlainText':
            self.cmbencoding.setCurrentIndex(0)   
        if self.defaultencoding == 'C':
            self.cmbencoding.setCurrentIndex(1)                
        if self.defaultencoding == 'C++':
            self.cmbencoding.setCurrentIndex(2)
           
        self.Timer = QtCore.QTimer(self)
        self.Timer.setInterval(100)
        self.connect(self.autosaveTimer,QtCore.SIGNAL('timeout()'),self.funcautosave)
        self.connect(self.Timer,QtCore.SIGNAL('timeout()'),self.functimer)
        self.projtreeitemarray = []
        self.tracktabsarray = []
        self.funcnewprojcalled = False
        self.funcaddnewcalled = False
        self.projname = ''
        self.projfilepatharray = []
        self.createTreeItem = True
        self.projtype = ''
        if self.wordwrap=='True':
            self.txtarray[self.tabs.currentIndex()].txtInput.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)

        if self.recentfiles == 'True':
            try:
                f = open('./recentfiles.ini','r')
                text = ''
                for d in f:
                    text = text + d
                f.close()
                self.canwrite_recentfiles = False
                index = -1
                for i in range(text.count('<file')):
                    filepath = ''
                    index = text.index('<file>',index+1)
                    for j in range(index+len('<file>'),text.index('</file>',index)):
                        filepath = filepath + text[j]
                    self.updatefilemenu(filepath)
                self.canwrite_recentfiles = True
            except:
                pass
        self.filedialogdir = ''

    def func_aboutide(self):

        self.about_ide = about_file.aboutide_dialog(self)
        self.about_ide.show()

    def func_aboutdb(self):

        self.about_db = about_file.aboutdb_dialog(self)
        self.about_db.show()
    
    def bookmark_menu_item_clicked(self):

        sender = self.sender()
        for i in range(len(self.bookmark_menu_item_array)):
            if sender == self.bookmark_menu_item_array[i]:
                self.bookmark_index = i
                break
        self.tabs.setCurrentIndex(self.bookmark_tabsindex_array[self.bookmark_index])
        cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
        cc.setPosition(0,cc.MoveAnchor)
        cc.movePosition(cc.Down,cc.MoveAnchor,self.bookmark_line_array[self.bookmark_index]-1)
        self.txtarray[self.tabs.currentIndex()].txtInput.setTextCursor(cc)
        self.txtarray[self.tabs.currentIndex()].txtInput.highlightcurrentline()
        
    def funcaddbookmark(self):

        cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
        self.bookmark_line_array.append(cc.blockNumber()+1)
        self.bookmark_tabsindex_array.append(self.tabs.currentIndex())
        self.bookmark_menu_item_array.append(QtGui.QAction(str(self.tabs.tabText(self.tabs.currentIndex()))+'    Line: '+str(cc.blockNumber()+1),self))
        self.navigationmenu.addAction(self.bookmark_menu_item_array[len(self.bookmark_menu_item_array)-1])
        self.bookmark_menu_item_array[len(self.bookmark_menu_item_array)-1].setCheckable(True)
        self.bookmark_actiongroup.addAction(self.bookmark_menu_item_array[len(self.bookmark_menu_item_array)-1])
        self.connect(self.bookmark_menu_item_array[len(self.bookmark_menu_item_array)-1],QtCore.SIGNAL('triggered()'),self.bookmark_menu_item_clicked)
        
    def funcnextbookmark(self):

        if self.bookmark_index == len(self.bookmark_line_array)-1:
            self.bookmark_index = -1
        self.bookmark_index +=1
        self.tabs.setCurrentIndex(self.bookmark_tabsindex_array[self.bookmark_index])
        cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
        cc.setPosition(0,cc.MoveAnchor)
        cc.movePosition(cc.Down,cc.MoveAnchor,self.bookmark_line_array[self.bookmark_index]-1)
        self.txtarray[self.tabs.currentIndex()].txtInput.setTextCursor(cc)
        self.bookmark_menu_item_array[self.bookmark_index].setChecked(True)
        self.txtarray[self.tabs.currentIndex()].txtInput.highlightcurrentline()

    def funcprevbookmark(self):

        if self.bookmark_index == 0:
            self.bookmark_index = len(self.bookmark_line_array)-1
        self.bookmark_index -=1
        self.tabs.setCurrentIndex(self.bookmark_tabsindex_array[self.bookmark_index])
        cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
        cc.setPosition(0,cc.MoveAnchor)
        cc.movePosition(cc.Down,cc.MoveAnchor,self.bookmark_line_array[self.bookmark_index]-1)
        self.txtarray[self.tabs.currentIndex()].txtInput.setTextCursor(cc)
        self.bookmark_menu_item_array[self.bookmark_index].setChecked(True)
        self.txtarray[self.tabs.currentIndex()].txtInput.highlightcurrentline()

    def funcclearbookmark(self):

        for i in range(len(self.bookmark_tabsindex_array)):
            self.navigationmenu.removeAction(self.bookmark_menu_item_array[i])
        self.bookmark_menu_item_array = []
        self.bookmark_tabsindex_array = []
        self.bookmark_line_array = []
        self.bookmark_actiongroup = QtGui.QActionGroup(self)
        
    def funcstartautosave(self):
        
        self.autosaveTimer.stop()
        self.autosaveTimer.setInterval(float(self.autosavetimeout)*1000*60)
        self.autosaveTimer.start()        

    def funcautosave(self):

        if self.autosavetabs == 'all':
            self.funcsaveall()
        else:
            if self.autosavetabs == 'current':
                self.savedialog()

    def funcstriptrailingspaces(self):

        cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
        cc.setPosition(0,cc.MoveAnchor)
        cc.movePosition(cc.End,cc.MoveAnchor)
        end_line = cc.blockNumber()
        cc.setPosition(0,cc.MoveAnchor)
        for i in range(end_line+1):
            cc.movePosition(cc.EndOfLine,cc.KeepAnchor)
            line = unicode(cc.selectedText(),'utf-8')
            space_count = 0
            for j in range(len(line)-1,0,-1):
                if line[j] == ' ':
                    space_count +=1
                else:
                    break
            cc.movePosition(cc.EndOfLine,cc.MoveAnchor)
            cc.setPosition(cc.position()-space_count,cc.KeepAnchor)
            cc.removeSelectedText()
            cc.movePosition(cc.Down,cc.MoveAnchor)
            cc.movePosition(cc.StartOfLine,cc.MoveAnchor)
            
    def funcuppercaseselection(self):

        cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
        text = str(cc.selectedText())
        cc.removeSelectedText()
        cc.insertText(text.upper())
    
    def funclowercaseselection(self):

        cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
        text = str(cc.selectedText())
        cc.removeSelectedText()
        cc.insertText(text.lower())
        
    def funcbackline(self):

        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        cc = txtInput.textCursor()
        line = cc.blockNumber() +1
        txtInput.boollinetrack = False
        i=0
        while i<5 and txtInput.linestrackarray[i]!=line:
            i +=1
       
        if i<5 and i>0:
            if line>=txtInput.linestrackarray[i-1]:
                cc.movePosition(cc.Up,cc.MoveAnchor,line-txtInput.linestrackarray[i-1])
            if line<txtInput.linestrackarray[i-1]:
                cc.movePosition(cc.Down,cc.MoveAnchor,txtInput.linestrackarray[i-1]-line)
            txtInput.setTextCursor(cc)
            txtInput.highlightcurrentline()
        txtInput.boollinetrack = True
        
    def funcforwardline(self):

        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        cc = txtInput.textCursor()
        line = cc.blockNumber() +1
        txtInput.boollinetrack = False
        i=0
        while i<5 and txtInput.linestrackarray[i]!=line:
            i +=1
       
        if i<4:
            if line>=txtInput.linestrackarray[i+1]:
                cc.movePosition(cc.Up,cc.MoveAnchor,line-txtInput.linestrackarray[i+1])
            if line<txtInput.linestrackarray[i+1]:
                cc.movePosition(cc.Down,cc.MoveAnchor,txtInput.linestrackarray[i+1]-line)
            txtInput.setTextCursor(cc)        
            txtInput.highlightcurrentline()
        txtInput.boollinetrack = True
        
    def funclastline(self):

        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput            
        doc = txtInput.document()
        chars = doc.characterCount()
        cc = txtInput.textCursor()
        cc.setPosition(chars-1,cc.MoveAnchor)
        cc.movePosition(cc.StartOfLine,cc.MoveAnchor)
        txtInput.setTextCursor(cc)
        txtInput.boollinetrack = False
        txtInput.highlightcurrentline()
        
    def funcfirstline(self):

        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        cc = txtInput.textCursor()
        cc.setPosition(0,cc.MoveAnchor)
        txtInput.setTextCursor(cc)
        txtInput.boollinetrack = False
        txtInput.highlightcurrentline()
        
    def funcprojectmanager(self):
        
        def projmanager_close_event():
            
            newprojname = self.winprojmanager.txtname.text()
            newprojtype = self.winprojmanager.txttype.text()
            newprojfilepatharray = []
            for i in range(self.winprojmanager.lstfiles.count()):
                newprojfilepatharray.append(str(self.winprojmanager.lstfiles.item(i).text()))
            
            if newprojname != self.projname:
                self.projectTreeItem.setText(0,self.newprojname)
                self.projname = newprojname
            
            self.projtype = newprojtype
            
            if newprojfilepatharray != self.projfilepatharray:
                if len(newprojfilepatharray) == len(self.projfilepatharray):
                    for i in range(len(self.newprojfilepatharray)):
                        self.projtreeitemarray[i].setText(0,self.getprojfilename(self.newprojfilepatharray[i]))
                        
                if len(newprojfilepatharray) < len(self.projfilepatharray):
                    self.projectTree.clear()
                    self.projectTreeItem = QtGui.QTreeWidgetItem(self.projectTree)
                    self.projectTreeItem.setText(0,self.projname)
                    self.projtreeitemarray=[]
                    for i in range(len(newprojfilepatharray)):
                        self.projtreeitemarray.append(QtGui.QTreeWidgetItem(self.projectTreeItem))
                        self.projtreeitemarray[len(self.projtreeitemarray)-1].setText(0,self.getprojfilename(newprojfilepatharray[len(self.projtreeitemarray)-1]))                
                        
                if len(newprojfilepatharray) > len(self.projfilepatharray):
                    for i in range(len(self.projfilepatharray)):
                        self.projtreeitemarray[i].setText(0,self.getprojfilename(newprojfilepatharray[i]))
                    for i in range(len(newprojfilepatharray)-len(self.projfilepatharray)):
                        self.projtreeitemarray.append(QtGui.QTreeWidgetItem(self.projectTreeItem))
                        self.projtreeitemarray[len(self.projtreeitemarray)-1].setText(0,self.getprojfilename(newprojfilepatharray[len(self.projtreeitemarray)-1]))
                self.projfilepatharray = newprojfilepatharray   
        self.winprojmanager = projectmanager.ProjectManager(self.projpath,self)
        self.connect(self.winprojmanager,QtCore.SIGNAL('destroy()'),projmanager_close_event)
        self.winprojmanager.show()
       
    def funcclassbrowser(self):

        if self.mode == 'Project' and self.projtype == 'C++ Project':      
            class_list = []
            members_list = []
            for txt in self.txtarray:
                if '.h' not in txt.filename:
                    continue
                for j in range(txt.combo_class.count()):
                    class_list.append(txt.combo_class.itemText(j))            
                    members_list.append(txt.func_array[j])
            
            self._class_browser = classbrowser.ClassBrowser(class_list,members_list,self)
            self._class_browser.show()
            
    def funcuncommentout(self):

        cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
        
        if cc.hasSelection() == True:
            selectionstart = cc.selectionStart()
            selectionend = cc.selectionEnd()
            cc.clearSelection()
            cc.setPosition(selectionstart,QTextCursor.MoveAnchor)
            cc.setPosition(selectionstart+2,QTextCursor.KeepAnchor)
            if cc.selectedText() == '/*':
                cc.removeSelectedText()
            cc.setPosition(selectionend-4,QTextCursor.MoveAnchor)
            cc.setPosition(selectionend-2,QTextCursor.KeepAnchor)
            if cc.selectedText() == '*/':
                cc.removeSelectedText()
            self.txtarray[self.tabs.currentIndex()].txtInput.setTextColor(QtGui.QColor('black'))
            self.txtarray[self.tabs.currentIndex()].txtInput.setFontItalic(False)
            self.txtarray[self.tabs.currentIndex()].txtInput.setTextCursor(cc)
            
            
    def funccommentout(self):

        cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
        
        if cc.hasSelection() == True:
            selectionstart = cc.selectionStart()
            selectionend = cc.selectionEnd()
            cc.clearSelection()
            cc.setPosition(selectionstart,QTextCursor.MoveAnchor)
            cc.insertText('/*')
            cc.setPosition(selectionend+2,QTextCursor.MoveAnchor)
            cc.insertText('*/')
            cc.setPosition(selectionstart,QTextCursor.MoveAnchor)
            cc.setPosition(selectionend+2,QTextCursor.KeepAnchor)
            self.txtarray[self.tabs.currentIndex()].txtInput.setTextColor(QtGui.QColor('darkGreen'))
            self.txtarray[self.tabs.currentIndex()].txtInput.setFontItalic(True)
            cc.clearSelection()
            self.txtarray[self.tabs.currentIndex()].txtInput.setTextCursor(cc)
            
    def closeEvent(self,event):

        self.exitdialog = QtGui.QDialog(self)
        self.notsavedarray = []
        self.checkboxarray = []

        def closewithoutsave():
            
            sys.exit()
            
        def cancel():

            self.exitdialog.close()

        def save():

            for i in range(len(self.checkboxarray)):
                
                if self.mode == 'File':
                    if self.checkboxarray[i].isChecked() == True:

                        if self.filepatharray[self.notsavedarray[i]] != '':

                            os.remove(self.filepatharray[self.notsavedarray[i]])
                            f = open(self.filepatharray[self.notsavedarray[i]],'w')
                            f.write(str(self.txtarray[self.notsavedarray[i]].toPlainText()))
                            f.close()
                        else:
                            self.tabs.setCurrentIndex(self.notsavedarray[i])
                            self.savedialog()
                if self.mode == 'Project':
                    if self.checkboxarray[i].isChecked() == True:
                        
                        if self.projfilepatharray[self.tracktabsarray[self.notsavedarray[i]]] != '':

                            os.remove(self.projfilepatharray[self.tracktabsarray[self.notsavedarray[i]]])
                            f = open(self.projfilepatharray[self.tracktabsarray[self.notsavedarray[i]]],'w')
                            f.write(str(self.txtarray[self.notsavedarray[i]].txtInput.toPlainText()))
                            f.close()
                        else:
                            self.tabs.setCurrentIndex(self.notsavedarray[i])
                            self.savedialog()
            sys.exit()
        
        if self.mode == 'File':
            self.notsavedarray = []            
            for i in range(len(self.filepatharray)):
                if self.filepatharray[i] != '':
                    f = open(self.filepatharray[i],'r')
                    s = ''
                    for d in f:
                        s +=d
                    f.close()
                    if self.strequal(s,str(self.txtarray[i].txtInput.toPlainText())) == False:
                        self.notsavedarray.append(i)
                else:
                    if str(self.txtarray[i].txtInput.toPlainText()) !='':
                        self.notsavedarray.append(i)
                        
        if self.mode == 'Project':
            self.notsavedarray = []
            for i in range(self.tabs.count()):
                self.projfilepatharray
                projfilepath = self.projfilepatharray[self.tracktabsarray[i]]                
                if projfilepath !="":
                    f = open(projfilepath,'r')
                    s = ''
                    for d in f:
                        s +=d
                    f.close()
                    
                    if self.strequal(s,str(self.txtarray[i].txtInput.toPlainText())) == False:
                       self.notsavedarray.append(i)
                else:
                    if str(self.txtarray[i].txtInput.toPlainText()) !='':
                            self.notsavedarray.append(i)
                               
        if self.notsavedarray == []:

            event.accept()
            sys.exit()

        else:
            event.ignore()
            
            self.exitdialog.setWindowTitle('Athena')
            self.exitdialog_vbox_frame = QtGui.QFrame(self.exitdialog)
            self.exitdialog.vbox = QtGui.QVBoxLayout(self.exitdialog_vbox_frame)
            label = QtGui.QLabel("Following files are not saved. Please select files you want to save.")
            self.exitdialog.vbox.addWidget(label)
            self.exitdialog_hbox_frame = QtGui.QFrame(self.exitdialog)
            self.exitdialog.hbox = QtGui.QHBoxLayout(self.exitdialog_hbox_frame)
            self.exitdialog.cmdclosewithoutsave = QtGui.QPushButton("Close without saving",self.exitdialog)
            self.exitdialog.cmdcancel = QtGui.QPushButton("Cancel",self.exitdialog)
            self.exitdialog.cmdsave = QtGui.QPushButton("Save",self.exitdialog)

            self.connect(self.exitdialog.cmdsave,QtCore.SIGNAL("clicked()"),save)
            self.connect(self.exitdialog.cmdcancel,QtCore.SIGNAL("clicked()"),cancel)
            self.connect(self.exitdialog.cmdclosewithoutsave,QtCore.SIGNAL("clicked()"),closewithoutsave)

            if self.mode == 'File':
                for i in self.notsavedarray:
                    self.checkboxarray.append(QtGui.QCheckBox(self.tabs.tabText(i),self.exitdialog))                    
                    self.exitdialog.vbox.addWidget(self.checkboxarray[len(self.checkboxarray)-1])
                    self.checkboxarray[len(self.checkboxarray)-1].setCheckable(True)
                    
            if self.mode == 'Project':
                for i in self.notsavedarray:
                    self.checkboxarray.append(QtGui.QCheckBox(self.tabs.tabText(i),self.exitdialog))                    
                    self.exitdialog.vbox.addWidget(self.checkboxarray[len(self.checkboxarray)-1])
                    self.checkboxarray[len(self.checkboxarray)-1].setCheckable(True)
                
            self.exitdialog.hbox.addWidget(self.exitdialog.cmdclosewithoutsave)
            self.exitdialog.hbox.addWidget(self.exitdialog.cmdcancel)
            self.exitdialog.hbox.addWidget(self.exitdialog.cmdsave)
            self.exitdialog_vbox_frame.setLayout(self.exitdialog.vbox)
            self.exitdialog_hbox_frame.setLayout(self.exitdialog.hbox)
            self.exitdialog.main_vbox = QtGui.QVBoxLayout(self.exitdialog)
            self.exitdialog.main_vbox.addWidget(self.exitdialog_vbox_frame)
            self.exitdialog.main_vbox.addWidget(self.exitdialog_hbox_frame)
            self.exitdialog.setLayout(self.exitdialog.main_vbox)
            self.exitdialog.show()
            
            
    def funcgotoline(self):

        self.wingotoline = QtGui.QMainWindow(self)
 
        def funccancel():
            self.wingotoline.close()

        def funcline():

            linenumber = int(self.wingotoline.txtgotoline.text())
            cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
            if linenumber > cc.blockNumber():
                cc.movePosition(QTextCursor.Down,QTextCursor.MoveAnchor,linenumber-cc.blockNumber()-1)
            if linenumber < cc.blockNumber():
                cc.movePosition(QTextCursor.Up,QTextCursor.MoveAnchor,cc.blockNumber()-linenumber-1)
            self.txtarray[self.tabs.currentIndex()].txtInput.setTextCursor(cc)
            self.txtarray[self.tabs.currentIndex()].txtInput.highlightcurrentline()
        
        self.wingotoline.setGeometry(100,100,259,143)
        self.wingotoline.setWindowTitle('Go To Line')
        self.wingotoline.show()
        self.wingotoline.txtgotoline = QtGui.QLineEdit('',self.wingotoline)
        self.wingotoline.txtgotoline.setGeometry(10,50,241,31)
        self.wingotoline.txtgotoline.show()
        self.wingotoline.cmdgotoline = QtGui.QPushButton('Go',self.wingotoline)
        self.wingotoline.cmdgotoline.setGeometry(30,100,97,31)
        self.wingotoline.cmdgotoline.show()
        self.wingotoline.label = QtGui.QLabel("Go to line:",self.wingotoline)
        self.wingotoline.label.setGeometry(10,10,211,21)
        self.wingotoline.label.show()
        self.wingotoline.cmdcancel = QtGui.QPushButton("Cancel",self.wingotoline)
        self.wingotoline.cmdcancel.setGeometry(140,100,97,31)
        self.wingotoline.cmdcancel.show()
        
        self.wingotoline.connect(self.wingotoline.cmdcancel,QtCore.SIGNAL('clicked()'),funccancel)
        self.wingotoline.connect(self.wingotoline.cmdgotoline, QtCore.SIGNAL('clicked()'),funcline)

    def funcrunterminal(self):

        self.threadterminal = Thread(self.runterminal,self.callback)
        self.threadterminal.start()
        
    def callback(self):
        
        pass
        
    def runterminal(self):

        os.system("gnome-terminal")

    def func_gui_gdb(self):
        
        if self.compilefile == '':
            msgbox = QtGui.QMessageBox.information(self,"Athena","File is not compiled, do you still want to run AthenaDB",QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
            if msgbox == QtGui.QMessageBox.Yes:
                self.gdb_main_win = gdb_main.main_window(self)                
                self.gdb_main_win.run_gdb_gui("","","")
                self.gdb_main_win.show()
        else:            
            self.gdb_main_win = gdb_main.main_window(self)
            directory = self.compilefile[:self.compilefile.rfind("/")]        
            self.gdb_main_win.run_gdb_gui(str(self.compilefile),"",directory)
            self.gdb_main_win.show()
            
    def funcrungdb(self):

        if self.compilefile != "":
            self.th = Thread(os.system,self.callback,["gnome-terminal -e " + "\"/bin/bash -c '" + "gdb " + str(self.compilefile) + "; exec /bin/bash -i'\""])
            self.th.start()            
        else:
            msg = QtGui.QMessageBox.information(self,"Athena","Please compile the file before running GNU Project Debugger",QtGui.QMessageBox.Ok)           
    
    def funcautoindent(self):
      
        def insert(times):
            r = ''
            indent_width = self.txtarray[self.tabs.currentIndex()].txtInput.indentwidth
            for i in range(0,times):
                r = indent_width + r
        
            return r
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        text = str(txtInput.toPlainText())
        cc = txtInput.textCursor()
        cc.movePosition(cc.Start,cc.MoveAnchor)
        index=0
        indent_level  = 0
        if text.count('{') == text.count('}'):            
            while(cc.movePosition(cc.NextCharacter,cc.KeepAnchor)==True):            
                word = unicode(cc.selectedText(),'utf-8')            
                cc.clearSelection()
                if word == '{':
                    indent_level +=1
                    if text[index+1] != '\n':
                        cc.insertText('\n')
                    if index != 0 and text[index-1] != '\n':
                        pos = cc.position()
                        if pos !=0:
                            cc.setPosition(pos-2,cc.MoveAnchor)
                            cc.insertText('\n')
                            cc.setPosition(pos+1,cc.MoveAnchor)
                    cc.insertText(insert(indent_level))
                else:                
                    if word == '}':
                        indent_level -=1
                        if text[index+1] != '\n':
                            cc.insertText('\n')
                        cc.insertText(insert(indent_level))
                    else:
                        if text[index] == '\n':
                            cc.insertText(insert(indent_level))
                index +=1
        else:
            msgbox = QtGui.QMessageBox.information(self,"Auto Indent","There is some error related to '{' and '}' in your code!",QtGui.QMessageBox.Ok)

    def getdir(self,filename):

        a = filename.split('/')
        s = ''
        for i in range(0,len(a)-1):
            s = "%s%s%s" % (s ,a[i],'/')
        return s
    
    def funcopenproj(self):

        self.projpath = ''
        
        self.projpath = str(QtGui.QFileDialog.getOpenFileName(self,'Open Project',self.filedialogdir,('C Project Files(*.cproj);;C++ Project Files(*.cppproj);;All Files(*.*)')))
            
        
        if self.projpath != '':
            self.projCompiledTimes=[0]
            self.filedialogdir = self.getdir(str(self.projpath))
            self.mode = 'Project'
            self.tabs.clear()
            self.txtarray=[]
            self.filepatharray=[]
            self.filestate=[]
            self.encodingarray=[]
            self.linestrackarray=[]
            self.openprojfile = open(str(self.projpath),'r+')
            self.openprojstring = ''
            self.projectdock.show()
            for d in self.openprojfile:
                self.openprojstring = self.openprojstring + d
            self.projtype = ''
            if self.projname == '':
                self.createTreeItem = True
            else:
                self.createTreeItem = False
            self.projname = ''
            for i in range(self.openprojstring.index('<name>')+6, self.openprojstring.index('</name>')):
                self.projname = self.projname + self.openprojstring[i]

            if self.createTreeItem == True:
                self.projectTree.setColumnCount(1)
                self.projectTreeItem = QtGui.QTreeWidgetItem(self.projectTree)
                self.projectTreeItem.setText(0,self.projname)
            else:
                try:
                    while(True):
                        del self.projecttreeitemarray[0]
                        del self.projfilepatharray[0]
                except:
                    pass
                    
                self.projectTree.clear()
                self.projectTree.setColumnCount(1)
                self.projectTreeItem = QtGui.QTreeWidgetItem(self.projectTree)
                self.projectTreeItem.setText(0,self.projname)
                
            for i in range(self.openprojstring.index('<type>')+6, self.openprojstring.index('</type>')):
                self.projtype = self.projtype + self.openprojstring[i]

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
            self.projtreeitemarray = []
            
            for i in range(0,len(self.projfilesendarray)):
                s = '' 
                for j in range(int(self.projfilesstartarray[i])+6,int(self.projfilesendarray[i])):
                    s = s + self.openprojstring[j]
                self.projfilepatharray.append(s)
                
#                if '.h' in s:
#                    self.includefileslist.append(s)                               
            #self.addcreatedobjects()
            for i in range(0,len(self.projfilepatharray)):
                self.projtreeitemarray.append(QtGui.QTreeWidgetItem(self.projectTreeItem))
                self.projtreeitemarray[i].setText(0,self.getprojfilename(self.projfilepatharray[i]))
            
            self.addnew.setEnabled(True)
            self.addexisting.setEnabled(True)
            
    def getprojfilename(self,path):
        
        array = []
        array = path.split('/')
        return str(array[len(array)-1])
            
    def projectTreeClicked(self,item,index):

        global docstr
        ##Remember to correct this code of fucking function written by me, at that time I was just a kid :P
        index = self.projtreeitemarray.index(item)
        self.fileandext = self.projfilepatharray[index].split('/')[len(self.projfilepatharray[index].split('/'))-1],self.projfilepatharray[index].split('.')[len(self.projfilepatharray[index].split('.'))-1]
        s,ext = self.fileandext
        self.index = index
        
        def createnewtab():
            global docstr
            page = QtGui.QWidget()
            vbox = QtGui.QVBoxLayout()
            self.txtarray.append(txtinput.codewidget(self.projtype,self))
            vbox.addWidget(self.txtarray[self.tabs.count()])
            page.setLayout(vbox)
            self.tabs.addTab(page, s)
            ff = open(self.projfilepatharray[self.index],'r+')
            docstr = ''
            self.txtarray[self.tabs.count()-1].filename = self.projfilepatharray[self.index]
            self.txtarray[self.tabs.count()-1].txtInput.setPlainText('')
            txtInput = self.txtarray[self.tabs.count()-1].txtInput
            self.txtarray[self.tabs.count() - 1].indentwidth = self.indentwidth
            self.txtarray[self.tabs.count() - 1].indentTF = self.indent
            self.txtarray[self.tabs.count() - 1].inc_indent_syms = self.inc_indent_syms
            self.txtarray[self.tabs.count() - 1].dec_indent_syms = self.dec_indent_syms
            
            for line in ff:
                docstr = docstr+line
            txtInput.setPlainText(docstr)
            self.txtarray[self.tabs.count() - 1].show_combo_boxes(self.projtype)            
            self.tracktabsarray.append(self.index)#Here self.tracktabsarray stores the index of file and self.tracktabsindex[self.tabs.currentIndex()] will give the index of tabs which displays the file.
            #or you can say index of file in projfilepatharray = self.tracktabsarray[self.tabs.currentIndex()}
            
            if ext == 'c' or ext=='C' or self.projtype == 'C Project':
                highlight = syntaxc.CHighlighter(self.txtarray[self.tabs.count()-1].txtInput.document())
                txtInput.fill_c_code_completion()
                self.addtoencodingarray(self.tabs.count()-1,'C') 
            else:
                if ext == 'cpp' or ext =='CPP' or self.projtype == 'C++ Project':
                    
                    highlight = syntaxcpp.CPPHighlighter(self.txtarray[self.tabs.count()-1].txtInput.document())
                    txtInput.fill_cpp_code_completion()                    
                    self.addtoencodingarray(self.tabs.count()-1,'C++') 
                else:
                    self.addtoencodingarray(self.tabs.count()-1,'PlainText') 
            self.filestate.append('opened')
                
            if self.wordwrap == 'False':
                self.txtarray[self.tabs.count()-1].txtInput.setLineWrapMode(QtGui.QTextEdit.NoWrap)
            else:
                self.txtarray[self.tabs.count()-1].txtInput.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)
            self.linestrackarray.append([-1,-1,-1,-1,-1])
        cancreate = False
        
        if int(self.tabs.count()) == 0:
            createnewtab()
            self.tabs.show()
            #if self.projtype == 'C++ Project':                
            #    self.txtarray[self.tabs.count()-1].txtInput.object_classarray = self.object_classarray
            #    self.txtarray[self.tabs.count()-1].txtInput.object_namearray = self.object_namearray
            self.connect(self.txtarray[self.tabs.count()-1].txtInput, QtCore.SIGNAL('textChanged()'),self.textchanged)
            self.connect(self.txtarray[self.tabs.count()-1].txtInput, QtCore.SIGNAL('cursorPositionChanged()'),self.OnMousePressed)
                                
        for i in range(0,int(self.tabs.count())):
            if s == str(self.tabs.tabText(i)):
                cancreate = False
                break
            else:
                cancreate = True
                
        if cancreate == True:
            createnewtab()
            self.tabs.show()
            #if self.projtype == 'C++ Project':
                #self.txtarray[self.tabs.count()-1].txtInput.object_classarray = self.object_classarray
                #self.txtarray[self.tabs.count()-1].txtInput.object_namearray = self.object_namearray
            self.connect(self.txtarray[self.tabs.count()-1].txtInput, QtCore.SIGNAL('textChanged()'),self.textchanged)
            self.connect(self.txtarray[self.tabs.count()-1].txtInput, QtCore.SIGNAL('cursorPositionChanged()'),self.OnMousePressed)
        
    def funcaddexisting(self):
        
        self.addexistingfilepath = QtGui.QFileDialog.getOpenFileName(self,'Open File',self.filedialogdir,('C Files(*.c);;C++ Files(*.cpp);;All Files(*.*)'))
        if self.addexistingfilepath!="":            
            self.filedialogdir = self.getdir(self.addexistingfilepath)
            d = self.addexistingfilepath.split('/')
            self.addexistingfilename = ''
            self.addexistingfilename = str(d[len(d)-1])
            self.projtreeitemarray.append(QtGui.QTreeWidgetItem(self.projectTreeItem))
            self.projtreeitemarray[len(self.projtreeitemarray)-1].setText(0,self.addexistingfilename)
            self.projfilepatharray.append(str(self.addexistingfilepath))
            self.projfile = open(self.projpath,'a')
            self.projfile.write('<file>' + self.addexistingfilepath + '</file>')
            self.projfile.close()
            if '.h' in self.addexistingfilepath:
                self.includefileslist.append(s)            
        
    def funcaddnew(self):
        try:
            self.addwin = addnewwindow.addnewwin(self)
            self.addwin.openaddwin(self.projpath,self.projtype)
            self.Timer.start()
            self.funcaddnewcalled = True
        except:
            pass
        
    def functimer(self):

        self.passprojname = False
        self.passfileinf = False
        
        if self.funcnewprojcalled == True:
            self.projCompiledTimes=[0]
            self.passprojname = self.newproj.passprojname()
            if self.passprojname == True:
                self.projfilepatharray = []
                self.projectdock.show()
                self.projname = self.newproj.txtname.text()
                self.projpath = self.newproj.txtsavepath.text()
                self.projtype = self.newproj.returnprojtype()
                self.mode = 'Project'
                if self.projname == '':
                    self.createTreeItem = True
                else:
                    self.createTreeItem = False
                    
                if self.createTreeItem == True:
                    self.projectTree.setColumnCount(1)
                    self.projectTreeItem = QtGui.QTreeWidgetItem(self.projectTree)
                    self.projectTreeItem.setText(0,self.projname)
                else:
                    try:
                        while(True):
                            del self.projecttreeitemarray[0]
                            del self.projfilepatharray[0]
                            self.projectTreeItem.clear()
                    except:
                        pass                  
                    
                    self.projectTree.setColumnCount(1)
                    self.projectTreeItem = QtGui.QTreeWidgetItem(self.projectTree)
                    self.projectTreeItem.setText(0,self.projname)
                    
                self.passprojname = False
                self.funcnewprojcalled = False
                self.Timer.stop()
                self.tabs.clear()
                
                for i in range(len(self.txtarray)):
                    del self.txtarray[i]
                    del self.filepatharray[i]
                    del self.filestate[i]
                    del self.encodingarray[i]
                    
        if self.funcaddnewcalled == True:
            self.passfileinf = self.addwin.allowpassfileinf()
            if self.passfileinf == True:
                self.projfilename = self.addwin.passfileinf()
                self.projtreeitemarray.append(QtGui.QTreeWidgetItem(self.projectTreeItem))
                self.projtreeitemarray[len(self.projtreeitemarray)-1].setText(0,self.projfilename)
                self.projfilepatharray.append(str(self.addwin.passfilepath()))
                self.passfileinf = False
                self.funcaddnewcalled == False
                self.Timer.stop()
            
    def funcnewproject(self):

        self.newproj = newproject.newprojectwin(self)
        self.newproj.show()
        self.Timer.start()        
        self.funcnewprojcalled = True
        self.addnew.setEnabled(True)
        self.addexisting.setEnabled(True)
        
    def changeencoding(self,encoding):

        self.addtoencodingarray(self.tabs.currentIndex(),encoding) 
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        doc = QtGui.QTextDocument(self)
        doc.setPlainText(txtInput.toPlainText())
        doc.setDefaultFont(txtInput.currentFont())
        txtInput.setDocument(doc)
        
        if encoding == 'C':
            highlight = syntaxc.CHighlighter(txtInput.document())
        else:
            if encoding=='C++':
                highlight = syntaxcpp.CPPHighlighter(txtInput.document())
            else:
                encoding = 'PlainText'      
            
    def toolbarcompile(self):
        
        try:
            s,ext = self.fileandext
        
            if s != '':
                if ext == 'C' or ext == 'c':
                    self.rungcccompiler()                        
                if ext == 'CPP' or ext == 'cpp':
                    self.rungppcompiler()
                                
        except:
            pass
                
    def addcppcomment(self):
        
        def addcomment():
            
            txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
            
            if self.winaddcppcomment.radiomulti.isChecked():
                txtInput.textCursor().insertText('/*' + str(self.winaddcppcomment.txtcomment.toPlainText()) + '*/')
                
            if self.winaddcppcomment.radiosingle.isChecked():
                txtInput.textCursor().insertText('//' + str(self.winaddcppcomment.txtcomment.toPlainText()))
                
        def cancel():
            
            self.winaddcppcomment.close()
            
        self.winaddcppcomment.setGeometry(100,100,363,214)
        self.winaddcppcomment.setWindowTitle('Add C++ Comment')
        self.winaddcppcomment.show()
        self.winaddcppcomment.lblcomment = QtGui.QLabel('Comment',self.winaddcppcomment)
        self.winaddcppcomment.lblcomment.setGeometry(10,30,71,21)
        self.winaddcppcomment.txtcomment = QtGui.QTextEdit('',self.winaddcppcomment)
        self.winaddcppcomment.txtcomment.setGeometry(100,20,221,41)
        self.winaddcppcomment.radiosingle = QtGui.QRadioButton('Single Line Comment',self.winaddcppcomment)
        self.winaddcppcomment.radiosingle.setGeometry(0,100,171,22)
        self.winaddcppcomment.radiomulti = QtGui.QRadioButton('Multi Line Comment',self.winaddcppcomment)
        self.winaddcppcomment.radiomulti.setGeometry(180,100,161,22)
        self.winaddcppcomment.cmdcancel = QtGui.QPushButton('Cancel',self.winaddcppcomment)
        self.winaddcppcomment.cmdcancel.setGeometry(60,160,111,27)
        self.winaddcppcomment.cmdadd = QtGui.QPushButton('Add Comment',self.winaddcppcomment)
        self.winaddcppcomment.cmdadd.setGeometry(220,160,111,27)
        self.winaddcppcomment.connect(self.winaddcppcomment.cmdadd,QtCore.SIGNAL('clicked()'),addcomment)
        self.winaddcppcomment.connect(self.winaddcppcomment.cmdcancel,QtCore.SIGNAL('clicked()'),cancel)            
        self.winaddcppcomment.lblcomment.show()
        self.winaddcppcomment.txtcomment.show()
        self.winaddcppcomment.radiosingle.show()
        self.winaddcppcomment.radiomulti.show()
        self.winaddcppcomment.cmdcancel.show()
        self.winaddcppcomment.cmdadd.show()

    def addccomment(self):
        
        def addcomment():
            
            txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
            txtInput.textCursor().insertText('/*' + str(self.winaddccomment.txtcomment.toPlainText()) + '*/')
                            
        def cancel():
            self.winaddccomment.close()
            
        self.winaddccomment.setGeometry(100,100,363,214)
        self.winaddccomment.setWindowTitle('Add C++ Comment')
        self.winaddccomment.show()
        self.winaddccomment.lblcomment = QtGui.QLabel('Comment',self.winaddccomment)
        self.winaddccomment.lblcomment.setGeometry(10,30,71,21)
        self.winaddccomment.txtcomment = QtGui.QTextEdit('',self.winaddccomment)
        self.winaddccomment.txtcomment.setGeometry(100,20,221,41)
        self.winaddccomment.cmdcancel = QtGui.QPushButton('Cancel',self.winaddccomment)
        self.winaddccomment.cmdcancel.setGeometry(60,160,111,27)
        self.winaddccomment.cmdadd = QtGui.QPushButton('Add Comment',self.winaddccomment)
        self.winaddccomment.cmdadd.setGeometry(220,160,111,27)
        self.winaddccomment.connect(self.winaddccomment.cmdadd,QtCore.SIGNAL('clicked()'),addcomment)
        self.winaddccomment.connect(self.winaddccomment.cmdcancel,QtCore.SIGNAL('clicked()'),cancel)            
        self.winaddccomment.lblcomment.show()
        self.winaddccomment.txtcomment.show()
        self.winaddccomment.cmdcancel.show()
        self.winaddccomment.cmdadd.show()
    
    def functabifyregion(self):

        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        cc = txtInput.textCursor()
        
        if cc.hasSelection() == True:
            selection_start_char = cc.selectionStart()
            selection_end_char = cc.selectionEnd()
            cc.setPosition(selection_end_char,cc.MoveAnchor)
            selection_end_line = cc.blockNumber()
            cc.setPosition(selection_start_char,cc.MoveAnchor)
            selection_start_line = cc.blockNumber()
            cc.movePosition(cc.StartOfLine,cc.MoveAnchor)            
            
            for i in range(selection_start_line,selection_end_line+2):
                
                cc.movePosition(cc.EndOfLine,cc.KeepAnchor)
                line = cc.selectedText()
                spaces = 0
                for j in range(0,len(line)):
                    if line[j] == ' ':
                        spaces +=1
                    else:
                        break

                cc.movePosition(cc.StartOfLine,cc.MoveAnchor)
                for j in range(spaces):
                    cc.deleteChar()
                for j in range(spaces/len(self.tabwidth)):
                    cc.insertText('\t')
                    
                cc.movePosition(cc.NextBlock,cc.MoveAnchor)
                
    def funcuntabifyregion(self):

        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        cc = txtInput.textCursor()
        if cc.hasSelection() == True:
            selection_start_char = cc.selectionStart()
            selection_end_char = cc.selectionEnd()
            cc.setPosition(selection_end_char,cc.MoveAnchor)
            selection_end_line = cc.blockNumber()
            cc.setPosition(selection_start_char,cc.MoveAnchor)
            selection_start_line = cc.blockNumber()
            cc.movePosition(cc.StartOfLine,cc.MoveAnchor)
            for i in range(selection_start_line+1,selection_end_line+2):
                cc.movePosition(cc.EndOfLine,cc.KeepAnchor)
                line = cc.selectedText()
                cc.movePosition(cc.StartOfLine,cc.MoveAnchor)
                tabs = 0
                for j in range(len(line)):
                    if line[j] == '\t':
                        tabs +=1
                    else:
                        break
                    
                for j in range(tabs):
                    cc.deleteChar()
                    
                for j in range(tabs*len(self.tabwidth)):
                    cc.insertText(' ')
                    
                cc.movePosition(cc.NextBlock,cc.MoveAnchor)
                
    
    def incindent(self):
        
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        cc = txtInput.textCursor()
        if cc.hasSelection() == True:
            selection_start_char = cc.selectionStart()
            selection_end_char = cc.selectionEnd()
            cc.setPosition(selection_end_char,cc.MoveAnchor)
            selection_end_line = cc.blockNumber()
            cc.setPosition(selection_start_char,cc.MoveAnchor)
            selection_start_line = cc.blockNumber()
            cc.movePosition(cc.StartOfLine,cc.MoveAnchor)
            cc.insertText(self.indentwidth)
            for i in range(selection_start_line+1,selection_end_line+1):
                cc.movePosition(cc.NextBlock,cc.MoveAnchor)
                cc.insertText(self.indentwidth)
               
    def decindent(self):
        
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        cc = txtInput.textCursor()
        if cc.hasSelection() == True:
            selection_start_char = cc.selectionStart()
            selection_end_char = cc.selectionEnd()
            cc.setPosition(selection_end_char,cc.MoveAnchor)
            selection_end_line = cc.blockNumber()
            cc.setPosition(selection_start_char,cc.MoveAnchor)
            selection_start_line = cc.blockNumber()
            cc.movePosition(cc.StartOfLine,cc.MoveAnchor)
            for i in range(len(self.indentwidth)):
                    cc.deleteChar()
            for i in range(selection_start_line+1,selection_end_line+1):
                cc.movePosition(cc.NextBlock,cc.MoveAnchor)
                for i in range(len(self.indentwidth)):
                    cc.deleteChar()

    def toolbarrun(self):        
            
        if self.filestate[self.tabs.currentIndex()] == 'opened':
            
                try:
                    f1 = self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.projfilepatharray[self.tabs.currentIndex()])
                    
                
        if self.filestate[self.tabs.currentIndex()] == 'saved':
            
                try:
                    f1 = self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.projfilepatharray[self.tabs.currentIndex()])
                
        if self.filestate[self.tabs.currentIndex()] == 'new':
            ask = QtGui.QMessageBox.question(self,'Compile','Your File is not saved, file should be saved before compilation! ',QtGui.QMessageBox.Ok,QtGui.QMessageBox.Cancel)
            if ask == QtGui.QMessageBox.Ok:
                self.funcsaveasfile()
                
                try:
                    f1= self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.projfilepatharray[self.tabs.currentIndex()])
        
        s,ext = self.fileandext
        if self.mode == 'Project':
            f1 = []
            
            for d in self.projfilepatharray:
                f1.append(self.correctfilename(d))
            a = f1[0].split('/')
            s = ''
            for i in range(1,len(a)-1):
                    s = s + '/' + a[i]
            ext = f1[0].split('.')[1]            
        if self.mode == 'File':
                
            a = f1.split('/')
            
            s = ''
            for i in range(1,len(a)-1):
                s = s + '/' + a[i]
            ext = f1.split('.')[1]
        self.compilefile = s +'/'+ 'tempfile'
        f2 = self.compilefile
        
        if s != '':
                if ext == 'C' or ext == 'c' or self.projtype == "C Project":
                        if f2 != '':
                            
                            if self.mode == "File":
                                self.runcompiler.gcccompiler(f1,f2,self.mode,self.txtarray,self.tabs,self.filepatharray,self.tracktabsarray)
                            if self.mode == "Project":                                
                                self.runcompiler.gcccompiler(f1,f2,self.mode,self.txtarray,self.tabs,self.projfilepatharray,self.tracktabsarray)
                            self.runcompiler.show()
                                                                      
                if ext == 'CPP' or ext == 'cpp' or self.projtype == "C++ Project":
                    if f2 != '':
                        if self.mode == "File":
                                self.runcompiler.gppcompiler(f1,f2,self.mode,self.txtarray,self.tabs,self.filepatharray,self.tracktabsarray)
                        if self.mode == "Project":                            
                            self.runcompiler.gppcompiler(f1,f2,self.mode,self.txtarray,self.tabs,self.projfilepatharray,self.tracktabsarray,self.projCompiledTimes)
                            self.projCompiledTimes[0]+=1
                        self.runcompiler.show()
                                               
    def rungcccompiler(self):
        
        f2 = ''
        
        if self.filestate[self.tabs.currentIndex()] == 'opened':
            
                try:
                    f1 = self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.projfilepatharray[self.tabs.currentIndex()])
                    
                self.compilefile = QtGui.QFileDialog.getSaveFileName(self,'Save File','')
        if self.filestate[self.tabs.currentIndex()] == 'saved':
            
                try:
                    f1 = self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.projfilepatharray[self.tabs.currentIndex()])
                self.compilefile = QtGui.QFileDialog.getSaveFileName(self,'Save File','')
        if self.filestate[self.tabs.currentIndex()] == 'new':
            ask = QtGui.QMessageBox.question(self,'Compile','Your File is not saved, file should be saved before compilation! ',QtGui.QMessageBox.Ok,QtGui.QMessageBox.Cancel)
            if ask == QtGui.QMessageBox.Ok:
                self.funcsaveasfile()
                self.compilefile = QtGui.QFileDialog.getSaveFileName(self,'Save File','')
                try:
                    f1= self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.projfilepatharray[self.tabs.currentIndex()])
                
        if self.mode == 'Project':
                f1 = []
                for d in self.projfilepatharray:
                    f1.append(self.correctfilename(d))
                self.compilefile = QtGui.QFileDialog.getSaveFileName(self,'Save File',self.filedialogdir)
                self.filedialogdir = self.getdir(self.compilefile)
                
        f2 = self.correctfilename(self.compilefile)
        if f2 != '':                
                if self.mode == "File":                    
                    self.runcompiler.gcccompiler(f1,f2,self.mode,self.txtarray,self.tabs,self.filepatharray,self.tracktabsarray)
                if self.mode == "Project":
                    self.runcompiler.gcccompiler(f1,f2,self.mode,self.txtarray,self.tabs,self.projfilepatharray,self.tracktabsarray)
                self.runcompiler.show()
               
    def rungppcompiler(self):
        
        f2 = ''
        if self.mode == 'File':            
            if self.filestate[self.tabs.currentIndex()] == 'opened':                                    
                try:
                    f1 = self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.projfilepatharray[self.tabs.currentIndex()])
                
                self.compilefile = QtGui.QFileDialog.getSaveFileName(self,'Save File','')
            if self.filestate[self.tabs.currentIndex()] == 'saved':                   
                try:
                    f1 = self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.projfilepatharray[self.tabs.currentIndex()])
                
                self.compilefile = QtGui.QFileDialog.getSaveFileName(self,'Save File','')
            if self.filestate[self.tabs.currentIndex()] == 'new':
                ask = QtGui.QMessageBox.question(self,'Compile','Your File is not saved, file should be saved before compilation! ',QtGui.QMessageBox.Ok,QtGui.QMessageBox.Cancel)
                if ask == QtGui.QMessageBox.Ok:
                    self.funcsaveasfile()
                    self.compilefile = QtGui.QFileDialog.getSaveFileName(self,'Save File',self.filedialogdir)
                    self.filedialogdir = self.getdir(self.compilefile)
                    f1 = self.correctfilename(self.filepatharray[self.tabs.currentIndex()])
               
        if self.mode == 'Project':
                f1 = []
                for d in self.projfilepatharray:
                    f1.append(self.correctfilename(d))
                self.compilefile = QtGui.QFileDialog.getSaveFileName(self,'Save File',self.filedialogdir)
                self.filedialogdir = self.getdir(self.compilefile)
        f2 = self.correctfilename(self.compilefile)
        
        if f2 != '':
            if self.mode == "File":
                self.runcompiler.gppcompiler(f1,f2,self.mode,self.txtarray,self.tabs,self.filepatharray,self.tracktabsarray)
                
            if self.mode == "Project":
                
                self.runcompiler.gppcompiler(f1,f2,self.mode,self.txtarray,self.tabs,self.projfilepatharray,self.tracktabsarray,self.projCompiledTimes)
                
            self.runcompiler.show()
           
    def correctfilename(self,fname):
        
        d = str(fname)
        a = '' 
        for s in d:
            if s == ' ':
                a = a + '\ '
            else:
                a = a + s
        return a

    def winopt_closed(self):

        try:
            settings = ''
            settingsfile = open('./settings.ini','r')
            for line in settingsfile:
                settings = settings + line
            
            settingsfile.close()

            self.indentwidth = ''
            for i in range(settings.index('<indentwidth>')+len('<indentwidth>'),settings.index('</indentwidth>')):
                self.indentwidth = self.indentwidth + settings[i]
                
            self.inc_indent_syms = ''
            for i in range(settings.index('<incindentsymbols>')+len('<incindentsymbols>'),settings.index('</incindentsymbols>')):
                self.inc_indent_syms = self.inc_indent_syms + settings[i]
                
            self.dec_indent_syms  = ''
            for i in range(settings.index('<decindentsymbols>')+len('<decindentsymbols>'),settings.index('</decindentsymbols>')):
                self.dec_indent_syms = self.dec_indent_syms + settings[i]

            self.autosave = ''
            for i in range(settings.index('<autosave>')+len('<autosave>'),settings.index('</autosave>')):
                self.autosave = self.autosave + settings[i]

            self.autosavetimeout = ''
            for i in range(settings.index('<autosavetimeout>')+len('<autosavetimeout>'),settings.index('</autosavetimeout>')):
                self.autosavetimeout = self.autosavetimeout + settings[i]
                
            self.autosavetabs = ''
            for i in range(settings.index('<autosavetabs>')+len('<autosavetabs>'),settings.index('</autosavetabs>')):
                self.autosavetabs = self.autosavetabs + settings[i]
                
            self.wordwrap = '' 
            for i in range(settings.index('<wordwrap>')+len('<wordwrap>'),settings.index('</wordwrap>')):
                self.wordwrap = self.wordwrap + settings[i]

            self.tabwidth = ''
            for i in range(settings.index('<tabwidth>')+len('<tabwidth>'),settings.index('</tabwidth>')):
                self.tabwidth = self.tabwidth + settings[i]

            self.defaultencoding = ''
            for i in range(settings.index('<encoding>')+len('<encoding>'),settings.index('</encoding>')):
                self.defaultencoding = self.defaultencoding + settings[i]

            self.indent = ''
            for i in range(settings.index('<indentation>')+len('<indentation>'),settings.index('</indentation>')):
                self.indent = self.indent + settings[i]
                
            self.gcccommand = ''
            for i in range(settings.index('<gcc>') + len('<gcc>'),settings.index('</gcc>')):
                self.gcccommand = self.gcccommand + settings[i]

            self.gppcommand = ''
            for i in range(settings.index('<g++>') + len('<g++>'),settings.index('</g++>')):
                self.gppcommand = self.gppcommand + settings[i]

            for i in range(len(self.txtarray)):
                self.txtarray[i].txtInput.indentwidth = self.indentwidth
                self.txtarray[i].txtInput.indentTF = self.indent
                self.txtarray[i].txtInput.inc_indent_syms = self.inc_indent_syms
                self.txtarray[i].txtInput.dec_indent_syms = self.dec_indent_syms
                if self.wordwrap == 'False':
                    self.txtarray[i].txtInput.setLineWrapMode(QtGui.QTextEdit.NoWrap)
                else:
                    self.txtarray[i].txtInput.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)        
                
                if self.defaultencoding == 'C':
                    highlight = syntaxc.CHighlighter(self.txtarray[i].txtInput.document())
                
                if self.defaultencoding == 'C++':
                    highlight = syntaxcpp.CPPHighlighter(self.txtarray[i].txtInput.document())
        except:
            print 'Error'
        
        if self.autosave=='True':            
            self.funcstartautosave()
            
    def funcoptions(self):
                
        self.settingschanged=True
        _winopt = options.winoptions(self)        
        self.connect(_winopt,QtCore.SIGNAL('closed()'),self.winopt_closed)
        _winopt.document(self.txtarray[self.tabs.currentIndex()].txtInput)
        _winopt.show()
      
    def OnMousePressed(self):       
                
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        cc = txtInput.textCursor()
            
        if self.mode == 'File':
            if self.filestate[self.tabs.currentIndex()] == 'opened' or  self.filestate[self.tabs.currentIndex()] == 'saved':
                pass      

        ##highlight current line
        
        if txtInput.remove_prev_highlight == True:
                
            pos = cc.position()            
            cc.setPosition(txtInput.prev_pos,cc.MoveAnchor)
            cc.select(cc.LineUnderCursor)
            txtInput.setTextCursor(cc)
            txtInput.setTextBackgroundColor(QtGui.QColor(255,255,255,255))
            cc.setPosition(pos,cc.MoveAnchor)
            txtInput.setTextCursor(cc)
            txtInput.remove_prev_highlight = False
            
        ######################
        self.statusBar().showMessage('Char '+ str(cc.position()+1) + ' Col ' + str(cc.columnNumber()+1) + ' Line ' + str(cc.blockNumber()+1) + ' Encoding ' + self.encodingarray[self.tabs.currentIndex()] + ' Indentation ' + self.indent)
       
    def funcfname1(self):
        
        i = self.arrfname.index(fname1)
        strfname,strfpath = self.arrfpathname[i]
        self.filepatharray[self.tabs.currentIndex()] = strfpath
        self.funcopen(strfpath)
                        
    def funcfname2(self):
        
        i = self.arrfname.index(fname2)
        strfname,strfpath = self.arrfpathname[i]
        self.filepatharray[self.tabs.currentIndex()] = strfpath
        self.funcopen(strfpath)
         
    def funcfname3(self):
        
        i = self.arrfname.index(fname3)
        strfname,strfpath = self.arrfpathname[i]
        self.filepatharray[self.tabs.currentIndex()] = strfpath
        self.funcopen(strfpath)
         
    def funcfname4(self):
        
        i = self.arrfname.index(fname4)
        strfname,strfpath = self.arrfpathname[i]
        self.filepatharray[self.tabs.currentIndex()] = strfpath
        self.funcopen(strfpath)
        
    def funcfname5(self):
        
        i = self.arrfname.index(fname5)
        strfname,strfpath = self.arrfpathname[i]
        self.filepatharray[self.tabs.currentIndex()] = strfpath
        self.funcopen(strfpath)
        
    def funcnewtab(self):
        
        self.filestate.append('new')
        self.linestrackarray.append([-1,-1,-1,-1,-1])
        self.txtarray.append(txtinput.codewidget("",self))
        page = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout()
        self.txtarray[self.tabs.count()].txtInput.setPlainText('')
        self.txtarray[self.tabs.count()].filename = ""
        vbox.addWidget(self.txtarray[self.tabs.count()])
        page.setLayout(vbox)
        self.tabs.addTab(page, 'New File')
        self.filepatharray.append('')
        self.connect(self.txtarray[self.tabs.count() - 1].txtInput, QtCore.SIGNAL('textChanged()'),self.textchanged)
        self.connect(self.txtarray[self.tabs.count() - 1].txtInput, QtCore.SIGNAL('cursorPositionChanged()'),self.OnMousePressed)
        txtInput = self.txtarray[self.tabs.count() - 1].txtInput
        self.txtarray[self.tabs.count() - 1].indentwidth = self.indentwidth
        self.txtarray[self.tabs.count() - 1].indentTF = self.indent
        self.txtarray[self.tabs.count() - 1].inc_indent_syms = self.inc_indent_syms
        self.txtarray[self.tabs.count() - 1].dec_indent_syms = self.dec_indent_syms
        print self.wordwrap
        if self.wordwrap == 'False':
            self.txtarray[self.tabs.count()-1].txtInput.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        else:
            self.txtarray[self.tabs.count()-1].txtInput.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)
        doc = QtGui.QTextDocument(self)
        doc.setPlainText('')
        doc.setDefaultFont(txtInput.currentFont())
        txtInput.setDocument(doc)
        
        if self.defaultencoding == 'C':
            highlight = syntaxc.CHighlighter(txtInput.document())
            self.addtoencodingarray(self.tabs.count(),'C')
            
        else:
            if self.defaultencoding == 'C++':
                highlight = syntaxcpp.CPPHighlighter(txtInput.document())
                self.addtoencodingarray(self.tabs.count(),'C++') 
            else:
                self.addtoencodingarray(self.tabs.count(),'PlainText')

    def funcremovealltab(self):
        
        for i in range(self.tabs.count()):
            del self.txtarray[0]
            del self.filepatharray[0]
            del self.filestate[0]
            del self.encodingarray[0]
            self.tabs.removeTab(i)
            
            if self.mode == 'Project':
                del self.tracktabsarray[0]      
        
    def funcremovetab(self):
        
        del self.txtarray[self.tabs.currentIndex()]
        del self.filepatharray[self.tabs.currentIndex()]
        del self.filestate[self.tabs.currentIndex()]
        del self.encodingarray[self.tabs.currentIndex()]
        if self.mode=='Project':
            del self.tracktabsarray[self.tabs.currentIndex()]
        self.tabs.removeTab(self.tabs.currentIndex())
        
    def end(self):
        
        sys.exit()
        
    def textchanged(self):
        
        pass
               
    def updatefilemenu(self, filename):
        
        try:
            d = filename.split('/')
            r = 0
            while d[r] != '':
                r = r + 1
        except:
            pass
        
        s = d[r-1]
        q = s.split('.')
        try:
            ext = q[1]
        except IndexError:
            ext = ''
                                      
        i = 0
        allowremove = True
            
        try:
            while (i>=0):
                strfname,strfpath = self.arrfpathname[i]
                if len(s) >18:
                    s = self.shortfname(s)
                if s==strfname and filename==strfpath:
                    self.arrfpathname.remove((strfname,strfpath))
                    fname = self.arrfname[i]
                    self.arrfname.remove(fname)
                    if self.fpathnameindex <=4:
                        self.arrfname.append(fname)
                        self.fpathnameindex -=1
                    filemenu.removeAction(fname)
                    allowremove = False
                    break
                i += 1
        except:
            pass
        
        if self.fpathnameindex<=4:
            if len(s) >18:
                    s = self.shortfname(s)
                
            self.arrfpathname.append((str(s),str(filename)))
            fname = self.arrfname[self.fpathnameindex]
            strfname,strfpath = self.arrfpathname[self.fpathnameindex]
            fname.setText(strfname)
            filemenu.addAction(fname)
            self.fpathnameindex += 1
        else:
            if len(s) >18:
                    s = self.shortfname(s)
                
            if allowremove==True:
                fname = self.arrfname[0]
                filemenu.removeAction(fname)
                strfname,strfpath = self.arrfpathname[0]
                self.arrfname.remove(fname)
                self.arrfpathname.remove((strfname,strfpath))
                
            self.arrfpathname.append((str(s),str(filename)))
            fname.setText(s)
            self.arrfname.append(fname)
            filemenu.addAction(fname)
        if self.canwrite_recentfiles == True:                
            try:
                f = open('./recentfiles.ini','r+')
                recentfiles_text = ''
                for i in range(len(self.arrfpathname)):
                    recentfiles_text = recentfiles_text + '<file>'+self.arrfpathname[i][1]+'</file>\n'
                f.write(recentfiles_text)
                f.close()
            except:
                pass

        returnarr = s,ext
        return returnarr
    
    def shortfname(self,filename):
        
        shortfilename=''
        for i in range(0,15):
            shortfilename = shortfilename + filename[i]
        shortfilename = shortfilename + '...'
        return shortfilename

    def strequal(self,s1,s2):

        equal = False
        if len(s1) != len(s2):
            return False
        else:
            for i in range(len(s1)):
                if s1[i] == s2[i]:
                    equal = True
                else:
                    equal = False
                    return False
            if equal == True:
                return True
        
    def opendialog(self):
        
        text = self.txtarray[self.tabs.currentIndex()].txtInput.toPlainText()       
        x = self.filestate[self.tabs.currentIndex()]
        print self.mode
        if self.mode == 'File':            
            if self.filepatharray[self.tabs.currentIndex()] !='':
                
                f = open(self.filepatharray[self.tabs.currentIndex()],'r')
                s = ''
                
                for d in f:
                    s += d
                f.close()
                a = str(self.txtarray[self.tabs.currentIndex()].txtInput.toPlainText())
                if self.strequal(s,a):
                    y = ''
                else:
                    y = 'textchanged'
                            
            if x == 'opened':
                if y == 'textchanged':
                    self.askopenfile(self.filepatharray[self.tabs.currentIndex()])
                else:
                    self.funcopenfile()
            if x == 'saved':
                if y == 'textchanged':
                    self.askopenfile(self.filepatharray[self.tabs.currentIndex()])
                else:
                    self.funcopenfile()
            if x == 'new':
                if text == '':
                    self.funcopenfile()
                else:
                    self.askopenfile(self.filepatharray[self.tabs.currentIndex()])
                    
        if self.mode == 'Project':
            self.funcopenfile()            
            
    def funcopen(self,openfname):
        
        global docstr
        
        docstr = ''                    
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        self.txtarray[self.tabs.currentIndex()].filename = openfname
        ff = open(openfname,'r+')
        if self.recentfiles=='True':
            self.fileandext = self.updatefilemenu(openfname)
        else:
            self.fileandext = openfname[:openfname.rindex('.')],openfname[openfname.rindex('.')+1:]
        s,ext = self.fileandext
        
        for line in ff:
            docstr = docstr+line
        self.tabs.setTabText(self.tabs.currentIndex(),s)
        self.linestrackarray[self.tabs.currentIndex()]=[-1,-1,-1,-1,-1]
        doc = QtGui.QTextDocument(txtInput)
        doc.setDefaultFont(txtInput.currentFont())
        txtInput.setDocument(doc)        
        txtInput.setPlainText(docstr)
        if ext == 'c' or ext=='C':
            self.txtarray[self.tabs.currentIndex()].show_combo_boxes('C File')
            txtInput.fill_c_code_completion()
            highlight = syntaxc.CHighlighter(self.txtarray[self.tabs.currentIndex()].txtInput.document())
            self.addtoencodingarray(self.tabs.currentIndex(),'C') 
        else:
            if ext == 'cpp' or ext =='CPP':
                #Remember to add fill_c_code_completion like function for C++
                self.txtarray[self.tabs.currentIndex()].show_combo_boxes('C++ File')
                txtInput.fill_cpp_code_completion()
                highlight = syntaxcpp.CPPHighlighter(self.txtarray[self.tabs.currentIndex()].txtInput.document())
                self.addtoencodingarray(self.tabs.currentIndex(),'C++') 
            else:
                if ext == 'h' or ext == 'H':
                    highlight = syntaxcpp.CPPHighlighter(self.txtarray[self.tabs.currentIndex()].txtInput.document())
                    self.addtoencodingarray(self.tabs.currentIndex(),self.defaultencoding)
                else:
                    self.addtoencodingarray(self.tabs.currentIndex(),'PlainText')
                
        #self.projectdock.close()
        self.tabs.show()
        self.filestate[self.tabs.currentIndex()] = 'opened'
        self.mode = 'File'
        ff.close()
                
    def funcopenfile(self):
        
        global openfarray,openf1name
        global ff
        filename = ''
        if self.tabs.isVisible() == False:
            self.tabs.clear()
            self.txtarray = []
            self.filestate = []
            self.filestate.append('')
            self.encodingarray = []
            self.encodingarray.append('')
            self.txtarray.append(txtinput.codewidget("",self))
            self.connect(self.txtarray[0].txtInput, QtCore.SIGNAL('textChanged()'),self.textchanged)
            self.connect(self.txtarray[0].txtInput, QtCore.SIGNAL('cursorPositionChanged()'),self.OnMousePressed)
            self.tabs.addTab(self.txtarray[0],"New File")
        try:            
            txtInput = self.txtarray[0].txtInput        
            filename = str(QtGui.QFileDialog.getOpenFileName(self,'Open File',self.filedialogdir,('C Files(*.c);;C++ Files(*.cpp);;All Files(*.*)')))
            if filename != '':
                if self.mode == 'Project':
                    self.filepatharray = ['']
                    self.tabs.clear()
                    self.projectdock.setVisible(False)
                    self.txtarray = []
                    self.tabs.clear()
                    self.txtarray = []
                    self.filestate = []
                    self.filestate.append('')
                    self.encodingarray = []
                    self.encodingarray.append('')
                    self.txtarray.append(txtinput.codewidget("",self))
                    self.connect(self.txtarray[0].txtInput, QtCore.SIGNAL('textChanged()'),self.textchanged)
                    self.connect(self.txtarray[0].txtInput, QtCore.SIGNAL('cursorPositionChanged()'),self.OnMousePressed)
                    self.tabs.addTab(self.txtarray[0],"New File")
                self.filepatharray[self.tabs.currentIndex()] = filename
                self.filedialogdir = self.getdir(self.filepatharray[self.tabs.currentIndex()])
                openf1name = self.filepatharray[self.tabs.currentIndex()]
                self.funcopen(openf1name)
        except IOError:
            pass
            
    def askopenfile(self,filename):
        
        ask = QtGui.QMessageBox.question(self,'Open File','Your File is not saved, do u want to save changes before opening a new file?',QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
        if ask == QtGui.QMessageBox.Yes:
            if filename != '':
                self.funcsaveasfile(filename)
            else:
                self.saveas()
            self.funcopenfile()
        if ask == QtGui.QMessageBox.No:
            self.funcopenfile()
    
    def funcsaveall(self):
        
        current_index = self.tabs.currentIndex()
        self.save_copy = False
        for i in range(self.tabs.count()):
            self.tabs.setCurrentIndex(i)
            savedialog()
        self.tabs.setCurrentIndex(current_index)
        
    def savedialog(self):
        
        self.save_copy = False
        if self.mode == 'File':
            txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
            x = self.filestate[self.tabs.currentIndex()]
            q = txtInput.toPlainText()
            savefname = self.filepatharray[self.tabs.currentIndex()]
            
            s = ''
            if savefname != '':

                f = open(savefname,'r')
                for d in f:
                    s +=d
                f.close()
            if self.strequal(s,str(self.txtarray[self.tabs.currentIndex()].txtInput.toPlainText())):
                y = ''
            else:
                y = 'textchanged'
        
            if x == 'new':
                savefname = str(QtGui.QFileDialog.getSaveFileName(self,'Save File',self.filedialogdir,('C Files(*.c);;C++ Files(*.cpp);;All Files(*.*)')))
                if savefname != '':
                    self.funcsaveasfile(savefname)
                            
            if x == 'opened':
                
                if y == 'textchanged':
                    
                    try:
                        q = txtInput.toPlainText()
                        os.remove(savefname)
                        ff = open(savefname,'w')
                        ff.write(q)
                        ff.close()
                        if savefname[savefname.find(".")+1:] == 'c':
                            txtInput.fill_c_code_completion()
                        if savefname[savefname.find(".")+1:] == 'cpp':
                            txtInput.fill_cpp_code_completion()
                        self.filestate[self.tabs.currentIndex()] = 'saved'
                        self.filepatharray[self.tabs.currentIndex()] = savefname
                    except OSError:
                        pass
                
            if x == 'saved':
                if y == 'textchanged':
                    q = txtInput.toPlainText()
                
                    try:
                        os.remove(savefname)
                        f = open(savefname,'w')
                        f.write(q)
                        f.close()
                        if savefname[savefname.find(".")+1:] == 'c':
                            txtInput.fill_c_code_completion()
                        if savefname[savefname.find(".")+1:] == 'cpp':
                            txtInput.fill_cpp_code_completion()                        
                        
                    except OSError:
                        pass

        if self.mode == 'Project':
            filepath = self.projfilepatharray[self.tracktabsarray[self.tabs.currentIndex()]]
            ff = open(filepath,'w')
            ff.write(self.txtarray[self.tabs.currentIndex()].txtInput.toPlainText())
            ff.close()
            if filepath[filepath.find(".")+1:] == 'c':
                self.txtarray[self.tabs.currentIndex()].txtInput.fill_c_code_completion()
            if filepath[filepath.find(".")+1:] == 'cpp':
                self.txtarray[self.tabs.currentIndex()].txtInput.fill_cpp_code_completion()
            if filepath[filepath.find(".")+1:] == 'h':
                if self.projtype == 'C++ Project':
                    self.txtarray[self.tabs.currentIndex()].show_combo_boxes('C++ Project')
                    self.txtarray[self.tabs.currentIndex()].txtInput.fill_cpp_code_completion()
                if self.projtype == 'C Project':
                    self.txtarray[self.tabs.currentIndex()].show_combo_boxes('C Project')
                    self.txtarray[self.tabs.currentIndex()].txtInput.fill_c_code_completion()
                
            
    def funcsaveasfile(self,savefname):
        
        try:
            txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
            self.filedialogdir = self.getdir(savefname)
            doc = QtGui.QTextDocument(self)
            doc.setPlainText(txtInput.toPlainText())
            doc.setDefaultFont(txtInput.currentFont())
            txtInput.setDocument(doc)
            q = str(txtInput.toPlainText())
            f = open(savefname,'w')
            f.write(q)
            f.close()
            if self.recentfiles=='True':
                self.fileandext = self.updatefilemenu(savefname)
            else:
                self.fileandext = openfname[:openfname.rindex('.')],savefname[openfname.rindex('.')+1:]          
            s,ext = self.fileandext
            
            if ext == 'c' or ext =='C':
                if self.mode == 'File':
                    self.txtarray[self.tabs.currentIndex()].show_combo_boxes('C File')
                if self.mode == 'Project':
                    self.txtarray[self.tabs.currentIndex()].show_combo_boxes('C Project')
                txtInput.fill_c_code_completion()
                highlight = syntaxc.CHighlighter(self.txtarray[self.tabs.currentIndex()].txtInput.document())
                self.addtoencodingarray(self.tabs.currentIndex(),'C')               
            else:
                if ext == 'cpp' or ext =='CPP':
                    #Remember to add fill_c_code_completion like function for C++
                    if self.mode == 'File':
                        self.txtarray[self.tabs.currentIndex()].show_combo_boxes('C++ File')
                    if self.mode == 'Project':
                        self.txtarray[self.tabs.currentIndex()].show_combo_boxes('C++ Project')
                    txtInput.fill_cpp_code_completion()
                    highlight = syntaxcpp.CPPHighlighter(self.txtarray[self.tabs.currentIndex()].txtInput.document())
                    self.addtoencodingarray(self.tabs.currentIndex(),'C++')
                else:
                    if ext == 'h' or ext == 'H':
                        if self.defaultencoding == 'C++':                            
                            if self.mode == 'File':
                                self.txtarray[self.tabs.currentIndex()].show_combo_boxes('C++ File')                            
                            
                            txtInput.fill_cpp_code_completion()
                            highlight = syntaxcpp.CPPHighlighter(self.txtarray[self.tabs.currentIndex()].txtInput.document())
                            self.addtoencodingarray(self.tabs.currentIndex(),self.defaultencoding)
                        if self.defaultencoding == 'C':
                            if self.mode == 'File':
                                self.txtarray[self.tabs.currentIndex()].show_combo_boxes('C File')
                            if self.mode == 'Project':
                                self.txtarray[self.tabs.currentIndex()].show_combo_boxes('C Project')
                            
                            txtInput.fill_c_code_completion()
                            highlight = syntaxc.CHighlighter(self.txtarray[self.tabs.currentIndex()].txtInput.document())
                            self.addtoencodingarray(self.tabs.currentIndex(),self.defaultencoding)

                    else:
                        self.addtoencodingarray(self.tabs.currentIndex(),'PlainText')
            
        
            if self.save_copy == False:
                self.tabs.setTabText(self.tabs.currentIndex(),s)
                self.filestate[self.tabs.currentIndex()] = 'saved'
                self.fileandext = self.updatefilemenu(savefname)
                try:
                    self.filepatharray[self.tabs.currentIndex()] = savefname
                except IndexError:
                    self.filepatharray.append(savefname)
                self.mode = 'File'
        except OSError:
            pass
        
    def addtoencodingarray(self,index,encoding):

        error = True
        try:
            b = self.encodingarray[index]
            error = False
        
        except IndexError:
            error = True

        if error == False:
            self.encodingarray[index] = encoding
        if error == True:
            self.encodingarray.append(encoding)
    
    
    def funcsaveallas(self):
        
        self.save_copy = False
        current_index = self.tabs.currentIndex()
        for i in range(self.tabs.count()):
            self.tabs.setCurrentIndex(i)
            saveas()
        self.tabs.setCurrentIndex(current_index)
    
    def funcsavecopyas(self):
        
        self.save_copy = True
        savefname = QtGui.QFileDialog.getSaveFileName(self,'Save File',self.filedialogdir,('C Files(*.c);;C++ Files(*.cpp);;All Files(*.*)'))
        self.funcsaveasfile(savefname)
        
    def saveas(self):
        
         self.save_copy = False
         savefname = QtGui.QFileDialog.getSaveFileName(self,'Save File',self.filedialogdir,('C Files(*.c);;C++ Files(*.cpp);;All Files(*.*)'))
         if savefname != '':
             self.funcsaveasfile(savefname)
        
    def new(self):

        self.tabs.clear()
        for i in range(len(self.txtarray)):
            del self.txtarray[i]
            del self.filestate[i]
            del self.encodingarray[i]

        self.filestate.append('new')
        
        self.txtarray.append(txtinput.codewidget("",self))
        self.addtoencodingarray(0,self.defaultencoding)        
        self.connect(self.txtarray[self.tabs.count() - 1].txtInput, QtCore.SIGNAL('textChanged()'),self.textchanged)
        self.connect(self.txtarray[self.tabs.count() - 1].txtInput, QtCore.SIGNAL('cursorPositionChanged()'),self.OnMousePressed)
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        page = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout()
        #self.txtarray[self.tabs.count()-1].txtInput.setPlainText('')
        txtInput.setPlainText('')
        vbox.addWidget(self.txtarray[self.tabs.count()-1])
        page.setLayout(vbox)
        self.tabs.addTab(page, 'New File')        
        self.tabs.setTabText(self.tabs.currentIndex(),"New File")
        self.txtarray[self.tabs.count() - 1].indentwidth = self.indentwidth
        self.txtarray[self.tabs.count() - 1].indentTF = self.indent
        self.txtarray[self.tabs.count() - 1].inc_indent_syms = self.inc_indent_syms
        self.txtarray[self.tabs.count() - 1].dec_indent_syms = self.dec_indent_syms
        if self.wordwrap == 'False':
            txtInput.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        else:
            txtInput.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)
        doc = QtGui.QTextDocument(self)
        doc.setPlainText('')
        doc.setDefaultFont(txtInput.currentFont())
        txtInput.setDocument(doc)
        #self.projectdock.close()
        self.mode = 'File'
        self.tabs.show()
        if self.defaultencoding == 'C':
                highlight = syntaxc.CHighlighter(txtInput.document())
                
        if self.defaultencoding == 'C++':
                highlight = syntaxcpp.CPPHighlighter(txtInput.document())
                
    def end(self):
        
        sys.exit()
        
    def paste(self):
        
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        txtInput.paste()
        
    def copy(self):
        
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        txtInput.copy()
        
    def cut(self):
        
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        txtInput.cut()
        
    def redo(self):
        
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        txtInput.redo()
        
    def undo(self):
        
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        txtInput.undo()
        
    def selectal(self):
        
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        txtInput.selectAll()
        
    def dattime(self):
        
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        datetime = str(strftime('%d/%m/%y %H:%M:%S'))
        txtInput.textCursor().insertText(datetime)

    def funcfindselected(self):

        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        cc = txtInput.textCursor()
        if cc.hasSelection() == True:
            selected_text = cc.selectedText()
        txtInput.find(selected_text)
        
    def funcregexpsearch(self):
        
        self.winregexp = QtGui.QDialog(self)
        self.winregexp.setWindowTitle("Regular Expression Search")
        self.winregexp.setGeometry(100,100,310,116)
        self.winregexp.search_count = 0
        
        def funcfind():
            
            text_regexp = str(self.winregexp.txtregexp.text())
            textregexp = ""          
            
            search_iter = re.finditer(r'%s'%text_regexp,str(self.txtarray[self.tabs.currentIndex()].txtInput.toPlainText()))
            cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
            pos = cc.position()
            for m in  search_iter:
                if m.start() > cc.position():
                    cc.setPosition(m.start(),cc.MoveAnchor)
                    cc.setPosition(m.end(),cc.KeepAnchor)
                    self.txtarray[self.tabs.currentIndex()].txtInput.setTextCursor(cc)
                    break
              
        self.winregexp.label = QtGui.QLabel("Regular Expression",self.winregexp)
        self.winregexp.txtregexp = QtGui.QLineEdit("",self.winregexp)
        self.winregexp.cmdfind = QtGui.QPushButton("Find",self.winregexp)
        self.winregexp.cmdclose = QtGui.QPushButton("Close",self.winregexp)
        
        self.winregexp.label.setGeometry(6,10,131,21)
        self.winregexp.txtregexp.setGeometry(6,40,301,31)
        self.winregexp.cmdfind.setGeometry(110,80,95,31)
        self.winregexp.cmdclose.setGeometry(210,80,95,31)
        
        self.winregexp.connect(self.winregexp.cmdfind,QtCore.SIGNAL("clicked()"),funcfind)
        self.winregexp.connect(self.winregexp.cmdclose,QtCore.SIGNAL("clicked()"),self.winregexp.close)
        self.winregexp.show()
        
    def funcfindinfile(self):

        self.winfindinfile.setGeometry(100,100,456,124)

        def funcfind():

            filename = str(self.winfindinfile.txtfile.text())
            if filename !='':
                filestr = ''
                f = open(filename,'r')
                for d in f:
                    filestr +=d
                f.close()
                if str(self.winfindinfile.txtfind.text()) !="":
                    if filestr.find(str(self.winfindinfile.txtfind.text()),0)!=-1:
                        self.winfindinfile.lblstatus.setText("Text found in file")
                    else:
                        self.winfindinfile.lblstatus.setText("Text not found in file")

        def funcopenfile():

            filename = str(QtGui.QFileDialog.getOpenFileName(self,'Open File',self.filedialogdir,('C Files(*.c);;C++ Files(*.cpp);;All Files(*.*)')))
            if filename !='':
                self.winfindinfile.txtfile.setText(filename)
        
        self.winfindinfile.lblfind = QtGui.QLabel("Find",self.winfindinfile)
        self.winfindinfile.lblfile  = QtGui.QLabel("File",self.winfindinfile)
        self.winfindinfile.txtfind = QtGui.QLineEdit("",self.winfindinfile)
        self.winfindinfile.lblstatus = QtGui.QLabel("",self.winfindinfile)
        self.winfindinfile.txtfile = QtGui.QLineEdit("",self.winfindinfile)
        self.winfindinfile.cmdfind = QtGui.QPushButton("Find",self.winfindinfile)
        self.winfindinfile.cmdopenfile = QtGui.QPushButton("Open File",self.winfindinfile)
        self.winfindinfile.cmdclose = QtGui.QPushButton("Close",self.winfindinfile)

        self.winfindinfile.lblfind.setGeometry(5,16,66,21)
        self.winfindinfile.lblfile.setGeometry(5,50,66,21)
        self.winfindinfile.lblstatus.setGeometry(5,93,350,21)
        self.winfindinfile.txtfind.setGeometry(80,10,271,31)
        self.winfindinfile.txtfile.setGeometry(80,50,271,31)
        self.winfindinfile.cmdfind.setGeometry(360,10,95,31)
        self.winfindinfile.cmdopenfile.setGeometry(360,50,95,31)
        self.winfindinfile.cmdclose.setGeometry(360,90,95,31)

        self.winfindinfile.connect(self.winfindinfile.cmdfind,QtCore.SIGNAL("clicked()"),funcfind)
        self.winfindinfile.connect(self.winfindinfile.cmdopenfile,QtCore.SIGNAL("clicked()"),funcopenfile)
        self.winfindinfile.connect(self.winfindinfile.cmdclose,QtCore.SIGNAL("clicked()"),self.winfindinfile.close)

        self.winfindinfile.show()

    def openfind(self):
        
        def funcfind():
            
            txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
            if self.winfind.optwholeword.isChecked() == True:
                d = txtInput.find(self.winfind.txtfind.text(),QtGui.QTextDocument.FindWholeWords)
            if self.winfind.optcase.isChecked() == True:
                d = txtInput.find(self.winfind.txtfind.text(),QtGui.QTextDocument.FindCaseSensitively)
            if self.winfind.optwholeword.isChecked() == True and self.winfind.optcase.isChecked() == True:
                d = txtInput.find(self.winfind.txtfind.text(),QtGui.QTextDocument.FindCaseSensitively and QtGui.QTextDocument.FindWholeWords)
            if self.winfind.optwholeword.isChecked() == False and self.winfind.optcase.isChecked() == False:
                d = txtInput.find(self.winfind.txtfind.text())    
            return d
        
        self.winfind.label = QtGui.QLabel("Find",self.winfind)
        self.winfind.txtfind = QtGui.QLineEdit(self.winfind)
        self.winfind.optwholeword = QtGui.QCheckBox("Match Whole Word",self.winfind)
        self.winfind.optcase = QtGui.QCheckBox("Match Case",self.winfind)
        self.winfind.cmdfind = QtGui.QPushButton("Find",self.winfind)
        self.winfind.cmdclose = QtGui.QPushButton("Close",self.winfind)

        self.winfind.setGeometry(100,100,381,123)
        self.winfind.label.setGeometry(10,16,41,21)
        self.winfind.txtfind.setGeometry(45,10,330,31)
        self.winfind.optcase.setGeometry(10,50,160,26)
        self.winfind.optwholeword.setGeometry(180,50,161,26)
        self.winfind.cmdfind.setGeometry(160,80,95,31)
        self.winfind.cmdclose.setGeometry(270,80,95,31)
        self.winfind.connect(self.winfind.cmdfind, QtCore.SIGNAL('clicked()'),funcfind)
        self.winfind.connect(self.winfind.cmdclose, QtCore.SIGNAL('clicked()'),self.winfind.close)
        self.winfind.setWindowTitle("Find")
        self.winfind.show()
        
    def openfindandreplace(self):

        global findarray,i
        findarray = []
        i = 0 
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        
        def funcfind():
            
            global findarray,i
            txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
            if self.winfindandreplace.optwholeword.isChecked() == True:
                d = txtInput.find(self.winfindandreplace.txtfind.text(),QtGui.QTextDocument.FindWholeWords)
            if self.winfindandreplace.optcase.isChecked() == True:
                d = txtInput.find(self.winfindandreplace.txtfind.text(),QtGui.QTextDocument.FindCaseSensitively)
            if self.winfindandreplace.optwholeword.isChecked() == True and self.winfindandreplace.optcase.isChecked() == True:
                d = txtInput.find(self.winfindandreplace.txtfind.text(),QtGui.QTextDocument.FindCaseSensitively and QtGui.QTextDocument.FindWholeWords)
            if self.winfindandreplace.optwholeword.isChecked() == False and self.winfindandreplace.optcase.isChecked() == False:
                d = txtInput.find(self.winfindandreplace.txtfind.text())    
            cc = txtInput.textCursor()
            findarray.append(int(cc.position()))
            return d
        
        def replace():
            
            global findarray,i
            txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
            cc = txtInput.textCursor()
            if cc.hasSelection() == True and cc.selectedText() == self.winfindandreplace.txtfind.text():
                cc.insertText(self.winfindandreplace.txtreplace.text())
            else:                
                if self.winfindandreplace.optwholeword.isChecked() == True:
                    d = txtInput.find(self.winfindandreplace.txtfind.text(),QtGui.QTextDocument.FindWholeWords)
                if self.winfindandreplace.optcase.isChecked() == True:
                    d = txtInput.find(self.winfindandreplace.txtfind.text(),QtGui.QTextDocument.FindCaseSensitively)
                if self.winfindandreplace.optwholeword.isChecked() == True and self.winfindandreplace.optcase.isChecked() == True:
                    d = txtInput.find(self.winfindandreplace.txtfind.text(),QtGui.QTextDocument.FindCaseSensitively and QtGui.QTextDocument.FindWholeWords)
                if self.winfindandreplace.optwholeword.isChecked() == False and self.winfindandreplace.optcase.isChecked() == False:
                    d = txtInput.find(self.winfindandreplace.txtfind.text())
                findarray.append(int(txtInput.textCursor().position()))
               
                if i !=0:
                    if findarray[i] != findarray[i-1] and d == True:
                        txtInput.textCursor().insertText(self.winfindandreplace.txtreplace.text())
                        
                else:
                    txtInput.textCursor().insertText(self.winfindandreplace.txtreplace.text())

                cc = txtInput.textCursor()
                cc.setPosition(cc.position()-len(self.winfindandreplace.txtreplace.text()),cc.MoveAnchor)
                cc.setPosition(cc.position()+len(self.winfindandreplace.txtreplace.text()),cc.KeepAnchor)
                txtInput.setTextCursor(cc)
                    
                i +=1

        def replaceall():

            global findarray,i
            findarray = []
            txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
            cc = txtInput.textCursor()
            if cc.position != 0:
                cc.setPosition(0,cc.MoveAnchor)
                txtInput.setTextCursor(cc)
            while(True):
                
                if self.winfindandreplace.optwholeword.isChecked() == True:
                    d = txtInput.find(self.winfindandreplace.txtfind.text(),QtGui.QTextDocument.FindWholeWords)
                if self.winfindandreplace.optcase.isChecked() == True:
                    d = txtInput.find(self.winfindandreplace.txtfind.text(),QtGui.QTextDocument.FindCaseSensitively)
                if self.winfindandreplace.optwholeword.isChecked() == True and self.winfindandreplace.optcase.isChecked() == True:
                    d = txtInput.find(self.winfindandreplace.txtfind.text(),QtGui.QTextDocument.FindCaseSensitively and QtGui.QTextDocument.FindWholeWords)
                if self.winfindandreplace.optwholeword.isChecked() == False and self.winfindandreplace.optcase.isChecked() == False:
                    d = txtInput.find(self.winfindandreplace.txtfind.text())
                findarray.append(int(txtInput.textCursor().position()))
           
                if i !=0:
                    if findarray[i] != findarray[i-1] and d == True:
                        txtInput.textCursor().insertText(self.winfindandreplace.txtreplace.text())
                    else:
                        break
                else:
                    txtInput.textCursor().insertText(self.winfindandreplace.txtreplace.text())
                    

                i +=1
            
        self.winfindandreplace.setGeometry(100,100,427,226)
        self.winfindandreplace.setWindowTitle('Find And Replace')
        
        self.winfindandreplace.txtfind = QtGui.QLineEdit('',self.winfindandreplace)
        self.winfindandreplace.txtfind.setGeometry(90,20,211,31)

        self.winfindandreplace.cmdfind = QtGui.QPushButton('Find',self.winfindandreplace)
        self.winfindandreplace.cmdfind.setGeometry(310,10,90,31)
        
        self.winfindandreplace.txtreplace = QtGui.QLineEdit('',self.winfindandreplace)
        self.winfindandreplace.txtreplace.setGeometry(90,70,210,31)
        
        self.winfindandreplace.cmdreplace = QtGui.QPushButton('Replace',self.winfindandreplace)
        self.winfindandreplace.cmdreplace.setGeometry(310,70,95,31)
        
        self.winfindandreplace.optwholeword = QtGui.QCheckBox('Match Whole Word',self.winfindandreplace)
        self.winfindandreplace.optwholeword.setGeometry(10,130,161,26)
        
        self.winfindandreplace.optcase = QtGui.QCheckBox('Match Case',self.winfindandreplace)
        self.winfindandreplace.optcase.setGeometry(180,130,111,26)
        
        self.winfindandreplace.cmdreplaceall = QtGui.QPushButton('Replace All',self.winfindandreplace)
        self.winfindandreplace.cmdreplaceall.setGeometry(310,120,95,31)
        
        self.winfindandreplace.cmdclose = QtGui.QPushButton('Close',self.winfindandreplace)
        self.winfindandreplace.cmdclose.setGeometry(310,170,95,31)

        self.winfindandreplace.lblfind = QtGui.QLabel("Find",self.winfindandreplace)
        self.winfindandreplace.lblfind.setGeometry(10,25,66,21)
        
        self.winfindandreplace.lblreplace = QtGui.QLabel("Replace",self.winfindandreplace)
        self.winfindandreplace.lblreplace.setGeometry(10,73,66,21)
        
        self.winfindandreplace.show()
        self.winfindandreplace.connect(self.winfindandreplace.cmdfind, QtCore.SIGNAL('clicked()'),funcfind)
        self.winfindandreplace.connect(self.winfindandreplace.cmdreplace, QtCore.SIGNAL('clicked()'),replace)
        self.winfindandreplace.connect(self.winfindandreplace.cmdreplaceall, QtCore.SIGNAL('clicked()'),replaceall)
        self.winfindandreplace.connect(self.winfindandreplace.cmdclose, QtCore.SIGNAL('clicked()'),self.winfindandreplace.close)
        
    def font(self):
        
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        font, ok = QtGui.QFontDialog.getFont()
        if ok:
            txtInput.setCurrentFont(font)
                    
    def color(self):
        
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        col = QtGui.QColorDialog.getColor()
        if col.isValid():
            txtInput.setTextBackgroundColor(col)
            
    def funcprint(self):
        
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        dialog_print = QtGui.QPrintPreviewDialog(self)
        dialog_print.paintRequested.connect(txtInput.print_)
        dialog_print.exec_()        

app = QtGui.QApplication(sys.argv)
nt = athena()
nt.show()
app.exec_()
