#2834 Lines
#7873 Total Lines

#!/usr/bin/python
# -*- coding: utf-8 -*-

###The cause of C++ Big Programs Compiling Problem could be line no. 1660
###Add running a program with arguments, environment variables and current

import syntaxc,syntaxcpp,project_class,save_as_project
import txtinput,compiler,options,newproject,proj_manager,classbrowser
import gdb_interface,about_file,breakpoints_dialog,set_breakpoint,locals_dlg
import sip
import sys,re
from PyQt4 import QtGui,QtCore
from PyQt4.Qt import QSyntaxHighlighter,QTextCursor,QPoint
from time import strftime
import os,threading,pty,termios,fcntl

class ReadFileThread(QtCore.QThread):

    def __init__(self,filename,parent=None):

        QtCore.QThread.__init__(self,parent)
        self.filename = filename
        self.file_string = ''
        
    def run(self):
        
        f = open(self.filename,'r')
        self.file_string = ''
        #for s in f:
        self.file_string+=unicode(f.read(),'utf-8',errors='ignore')
        
        f.close()

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

#######Creating the psuedoterminal and child process###########
        return_val = pty.fork()

        if return_val[0]==0:

            os.execv("/bin/bash",["/bin/bash"])

        self.state=0
        self.fd = return_val[1]
        tc_attr = termios.tcgetattr(self.fd)
        tc_attr[3] = tc_attr[3] & ~termios.ECHO
        termios.tcsetattr(self.fd,termios.TCSANOW,tc_attr)
        fl = fcntl.fcntl(self.fd,fcntl.F_GETFL)
        fcntl.fcntl(self.fd,fcntl.F_SETFL,fl|os.O_NONBLOCK)
###############################################################
        
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

        self.list_gdb_commands=[]
        self.list_breakpoints=[]
        self.current_proj=project_class.project("","","")
        
        self.save_copy = False
        self.linestrackarray = [[-1,-1,-1,-1,-1]]
        self.boollinetrack = True
        self.projCompiledTimes=[0]
        
        QtGui.QMainWindow.__init__(self,parent)
        
        self.showMaximized()
        self.setWindowTitle("AthenaIDE")
        self.setWindowIcon(QtGui.QIcon('../icons/texteditor.png'))

        self.gdbConsoleDialog = gdb_interface.GdbConsoleDlg(self.fd,self)
        self.connect(self.gdbConsoleDialog,QtCore.SIGNAL('processStoppedBreakpointHit(QString,int)'),self.processStoppedBreakpointHit)        
        self.connect(self.gdbConsoleDialog,QtCore.SIGNAL('processStoppedSignalRecieved(QString,QString,int)'),self.processStoppedSignalRecieved)
        self.connect(self.gdbConsoleDialog,QtCore.SIGNAL('processStopped()'),self.processStopped)
        self.connect(self.gdbConsoleDialog,QtCore.SIGNAL('showLocals(QString)'),self.gdbConsoleDialogShowLocals)
        
        self.projectdock = QtGui.QDockWidget(self)
        self.projectdock.setWindowTitle('')
        self.addDockWidget(0x1,self.projectdock) #Qt.LeftDockWidgetArea = 0x1
        self.projectdock.setFixedWidth(200)
        self.projectTree = QtGui.QTreeWidget(self.projectdock)
        self.projectdock.setWidget(self.projectTree)
        self.projectTree.itemDoubleClicked.connect(self.projectTreeClicked)
        self.projectTree.setHeaderLabel('Project')
        self.projectdock.hide()
        
        fileopen = QtGui.QAction(QtGui.QIcon('../icons/open.png'),'Open',self)
        self.connect(fileopen,QtCore.SIGNAL('triggered()'),self.opendialog)        
        
        filesave = QtGui.QAction(QtGui.QIcon('../icons/save.png'),'Save',self)
        self.connect(filesave,QtCore.SIGNAL('triggered()'),self.savedialog)
        filesave.setShortcut('CTRL+S')
        filesave.setStatusTip('Save the current file')
        
        filenew = QtGui.QAction(QtGui.QIcon('../icons/new.ico'),'New',self)
                
        exitnt = QtGui.QAction('Exit',self)
        self.connect(exitnt,QtCore.SIGNAL('triggered()'),self.end)        

        copy = QtGui.QAction(QtGui.QIcon('../icons/copy.png'),'Copy',self)
        self.connect(copy,QtCore.SIGNAL('triggered()'),self.copy)
        copy.setShortcut('CTRL+C')
        copy.setStatusTip('Copies the currently selected text to clipboard')

        paste = QtGui.QAction(QtGui.QIcon('../icons/paste.png'),'Paste',self)
        self.connect(paste,QtCore.SIGNAL('triggered()'),self.paste)
        paste.setShortcut('CTRL+V')
        paste.setStatusTip('Paste the current text in clipboard')
        
        cut = QtGui.QAction(QtGui.QIcon('../icons/cut.png'),'Cut',self)
        self.connect(cut,QtCore.SIGNAL('triggered()'),self.cut)
        cut.setShortcut('CTRL+X')
        cut.setStatusTip('Cut the currently selected text to clipboard')
        
        undo = QtGui.QAction(QtGui.QIcon('../icons/undo.png'),'Undo',self)
        self.connect(undo,QtCore.SIGNAL('triggered()'),self.undo)
        undo.setShortcut('CTRL+Z')
        undo.setStatusTip('Undo the last operation')
        
        redo = QtGui.QAction(QtGui.QIcon('../icons/redo.png'),'Redo',self)
        self.connect(redo,QtCore.SIGNAL('triggered()'),self.redo)
        redo.setShortcut('CTRL+SHIFT+Z')
        redo.setStatusTip('Redo the last operation')
        
        selectall = QtGui.QAction(QtGui.QIcon('../icons/selectall.png'),'Select All',self)
        self.connect(selectall,QtCore.SIGNAL('triggered()'),self.selectal)
        selectall.setShortcut('CTRL+A')
        selectall.setStatusTip('Selects all the text')

        select_current_function = QtGui.QAction('Select Current Function',self)
        self.connect(select_current_function,QtCore.SIGNAL('triggered()'),self.select_current_function_triggered)
        
        select_current_block = QtGui.QAction('Select Current Block',self)
        self.connect(select_current_block,QtCore.SIGNAL('triggered()'),self.select_current_block_triggered)
        
        datentime = QtGui.QAction('Insert Date and Time',self)
        self.connect(datentime,QtCore.SIGNAL('triggered()'),self.dattime)

        find = QtGui.QAction(QtGui.QIcon('../icons/find.png'),'Find',self)
        self.connect(find,QtCore.SIGNAL('triggered()'),self.openfind)
        find.setShortcut('CTRL+F')
        find.setStatusTip('Find text in current file')

        findandreplace = QtGui.QAction(QtGui.QIcon('../icons/findandreplace.png'),'Find And Replace',self)
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

        fold_all_functions = QtGui.QAction('Fold All Functions',self)
        self.connect(fold_all_functions,QtCore.SIGNAL('triggered()'),self.fold_all_functions_triggered)
        
        unfold_all_functions = QtGui.QAction('Unfold All Functions',self)
        self.connect(unfold_all_functions,QtCore.SIGNAL('triggered()'),self.unfold_all_functions_triggered)
                                  
        fold_current_block = QtGui.QAction('Fold Current Block',self)
        self.connect(fold_current_block,QtCore.SIGNAL('triggered()'),self.fold_current_block_triggered)
        
        fold_current_function = QtGui.QAction('Fold Current Function',self)
        self.connect(fold_current_function,QtCore.SIGNAL('triggered()'),self.fold_current_function_triggered)

        auto_complete = QtGui.QAction('Auto Complete',self)
        self.connect(auto_complete,QtCore.SIGNAL('triggered()'),self.auto_complete_triggered)
        
        changefont = QtGui.QAction('Font',self)
        self.connect(changefont,QtCore.SIGNAL('triggered()'),self.font)

        changecolor = QtGui.QAction('Text Color',self)
        self.connect(changecolor,QtCore.SIGNAL('triggered()'),self.color)

        mnuincindent = QtGui.QAction(QtGui.QIcon('../icons/indent.png'),'Increase Indent',self)
        self.connect(mnuincindent,QtCore.SIGNAL('triggered()'),self.incindent)
        mnuincindent.setShortcut('CTRL+]')
        mnuincindent.setStatusTip('Increase Indent of currently selected region')
        
        mnudecindent = QtGui.QAction(QtGui.QIcon('../icons/dedent.png'),'Decrease Indent',self)
        self.connect(mnudecindent,QtCore.SIGNAL('triggered()'),self.decindent)
        mnudecindent.setShortcut('CTRL+[')
        mnudecindent.setStatusTip('Decrease Indent of currently selected region')
        
        mnuaddcppcomment = QtGui.QAction('Add Comment',self)
        self.connect(mnuaddcppcomment,QtCore.SIGNAL('triggered()'),self.addcppcomment)
        mnuaddcppcomment.setStatusTip('Add a comment to current file')
        
        commentout_multiline = QtGui.QAction(QtGui.QIcon('../icons/commentout.png'),'Multi-Line Comment Out Region',self)
        self.connect(commentout_multiline,QtCore.SIGNAL('triggered()'),self.funccommentout)
        commentout_multiline.setShortcut('CTRL+SHIFT+C')
        commentout_multiline.setStatusTip('Comment out the currently selected text')
        
        uncommentout_multiline = QtGui.QAction(QtGui.QIcon('../icons/uncommentout.png'),'Multi-Line Uncomment Out Region',self)
        self.connect(uncommentout_multiline, QtCore.SIGNAL('triggered()'),self.funcuncommentout)
        uncommentout_multiline.setShortcut('CTRL+SHIFT+U')
        uncommentout_multiline.setStatusTip('Uncomment out the currently selected text')

        commentout_singleline = QtGui.QAction(QtGui.QIcon('../icons/commentout.png'),'Single-Line Comment Out Region',self)
        self.connect(commentout_singleline, QtCore.SIGNAL('triggered()'),self.commentout_singleline_triggered)
        
        uncommentout_singleline = QtGui.QAction(QtGui.QIcon('../icons/commentout.png'),'Single-Line Uncomment Out Region',self)
        self.connect(uncommentout_singleline, QtCore.SIGNAL('triggered()'),self.uncommentout_singleline_triggered)
        
        tabifyregion = QtGui.QAction('Tabify Region',self)
        self.connect(tabifyregion, QtCore.SIGNAL('triggered()'),self.functabifyregion)
        tabifyregion.setShortcut('CTRL+SHIFT+T')
        tabifyregion.setStatusTip('Replaces Spaces with Tabs according to Tab Width')
        
        untabifyregion = QtGui.QAction('Untabify Region',self)
        self.connect(untabifyregion, QtCore.SIGNAL('triggered()'),self.funcuntabifyregion)
        untabifyregion.setShortcut('CTRL+SHIFT+R')
        untabifyregion.setStatusTip('Replaces Tabs with Spaces according to Tab Width')
        
        uppercaseselection = QtGui.QAction(QtGui.QIcon('../icons/uppercase.png'),'Uppercase Selection',self)
        self.connect(uppercaseselection, QtCore.SIGNAL('triggered()'),self.funcuppercaseselection)
        uppercaseselection.setShortcut('CTRL+SHIFT+O')
        uppercaseselection.setStatusTip('Uppercase each character in the selected text')
        
        lowercaseselection = QtGui.QAction(QtGui.QIcon('../icons/lowercase.png'),'Lowercase Selection',self)
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
        
        filesaveas = QtGui.QAction(QtGui.QIcon('../icons/saveas.png'),'Save As',self)
        self.connect(filesaveas,QtCore.SIGNAL('triggered()'),self.saveas)
        filesaveas.setShortcut('CTRL+SHIFT+S')
        filesaveas.setStatusTip('SaveAs the current file')
        
        filesaveall = QtGui.QAction("Save All",self)
        self.connect(filesaveall,QtCore.SIGNAL('triggered()'),self.funcsaveall)
        
        filesaveallas = QtGui.QAction("Save All As",self)
        self.connect(filesaveall,QtCore.SIGNAL('triggered()'),self.funcsaveallas)
        
        filesavecopyas = QtGui.QAction("Save Copy As",self)
        self.connect(filesaveall,QtCore.SIGNAL('triggered()'),self.funcsavecopyas)
        
        eXit = QtGui.QAction(QtGui.QIcon('../icons/exit.png'),'Exit',self) 
        self.connect(eXit,QtCore.SIGNAL('triggered()'),self.end)
        eXit.setShortcut('CTRL+Q')
        eXit.setStatusTip('Exits Athena')
        
        fileprint = QtGui.QAction(QtGui.QIcon('../icons/print.png'),'Print',self)
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

        showoptions = QtGui.QAction(QtGui.QIcon('../icons/options.png'),'Options',self)
        self.connect(showoptions,QtCore.SIGNAL('triggered()'),self.funcoptions)
        
        toolbarrun = QtGui.QAction(QtGui.QIcon('../icons/run.png'),'Run',self)
        self.connect(toolbarrun,QtCore.SIGNAL('triggered()'),self.toolbarrun)
        toolbarrun.setShortcut('F5')
        toolbarrun.setStatusTip('Run')
        
        toolbarcompile = QtGui.QAction(QtGui.QIcon('../icons/compile.png'),'Compile And Run', self)
        self.connect(toolbarcompile,QtCore.SIGNAL('triggered()'),self.toolbarcompile)
        toolbarcompile.setShortcut('SHIFT+F5')
        toolbarcompile.setStatusTip('Compile')

        save_project=QtGui.QAction('Save Project',self)
        self.connect(save_project,QtCore.SIGNAL('triggered()'),self.save_project_triggered)

        save_project_as=QtGui.QAction('Save Project As',self)
        self.connect(save_project_as,QtCore.SIGNAL('triggered()'),self.save_project_as_triggered)

        save_project_copy_as=QtGui.QAction('Save Project Copy As',self)
        self.connect(save_project_copy_as,QtCore.SIGNAL('triggered()'),self.save_project_copy_as_triggered)

        empty_project=QtGui.QAction('Empty Project',self)
        self.connect(empty_project,QtCore.SIGNAL('triggered()'),self.empty_project_triggered)

        close_project=QtGui.QAction(QtGui.QIcon('../icons/project_close.png'),'Close Project',self)
        self.connect(close_project,QtCore.SIGNAL('triggered()'),self.close_project_triggered)       
        
        projectmanager = QtGui.QAction(QtGui.QIcon('../icons/project_options.png'),'Project Preferences',self)
        projectmanager.setStatusTip('Edit Project Name, Type and Files')
        
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
        
        newprojectaction = QtGui.QAction(QtGui.QIcon('../icons/project_new.png'),'New Project',self)
        newprojectaction.setShortcut('CTRL+SHIFT+N')
        newprojectaction.setStatusTip('Create a New Project')
        
        newfileaction = QtGui.QAction('New File',self)
        newfileaction.setShortcut('CTRL+N')
        newfileaction.setStatusTip('Create a New File')
        
        self.addnew = QtGui.QAction('Add New File',self)
        self.addexisting = QtGui.QAction('Add Existing File',self)
        self.addnew.setEnabled(False)
        self.addexisting.setEnabled(False)

        openproj = QtGui.QAction(QtGui.QIcon('../icons/project_open.png'),'Open Project',self)
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
        
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(newfileaction)
        filemenu.addAction(newtab)
        
        filemenu.addAction(openfile)
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
        editmenu.addSeparator()
        editmenu.addAction(select_current_block)
        editmenu.addAction(select_current_function)
        editmenu.addAction(selectall)
        editmenu.addSeparator()
        editmenu.addAction(find)
        editmenu.addAction(findandreplace)
        editmenu.addAction(findinfile)
        editmenu.addAction(findselectedtext)
        editmenu.addAction(regexpsearch)
        editmenu.addSeparator()
        editmenu.addAction(datentime)        
        editmenu.addSeparator()
        editmenu.addAction(fold_all_functions)
        editmenu.addAction(unfold_all_functions)
        editmenu.addAction(fold_current_block)
        editmenu.addAction(fold_current_function)
        editmenu.addSeparator()
        editmenu.addAction(auto_complete)
        
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
        formatmenu.addAction(commentout_singleline)
        formatmenu.addAction(uncommentout_singleline)
        formatmenu.addSeparator()
        formatmenu.addAction(tabifyregion)
        formatmenu.addAction(untabifyregion)
        formatmenu.addSeparator()
        formatmenu.addAction(uppercaseselection)
        formatmenu.addAction(lowercaseselection)
        formatmenu.addSeparator()
        formatmenu.addAction(striptrailingspaces)
        
        self.navigationmenu = menubar.addMenu('Navi&gaton')
        go_to_matching_brace = QtGui.QAction('Go To Matching Brace',self)
        
        back_line = QtGui.QAction(QtGui.QIcon('../icons/backline'),'Back',self)
        back_line.setShortcut(QtCore.Qt.ALT+QtCore.Qt.Key_Left)
        back_line.setStatusTip('Go to previous line in line history')
        forward_line = QtGui.QAction(QtGui.QIcon('../icons/nextline'),'Forward',self)
        forward_line.setShortcut(QtCore.Qt.ALT+QtCore.Qt.Key_Right)
        forward_line.setStatusTip('Go to next line in line history')
        last_line = QtGui.QAction(QtGui.QIcon('../icons/lastline'),'End of file',self)
        last_line.setShortcut(QtCore.Qt.ALT+QtCore.Qt.Key_Down)
        last_line.setStatusTip('Go to last line in the file')
        first_line = QtGui.QAction(QtGui.QIcon('../icons/firstline'),'Start of file',self)
        first_line.setShortcut(QtCore.Qt.ALT+QtCore.Qt.Key_Up)
        first_line.setStatusTip('Go to first line')
        add_bookmark = QtGui.QAction(QtGui.QIcon('../icons/bookmarksadd.png'),'Add Bookmark',self)
        add_bookmark.setShortcut(QtCore.Qt.CTRL+QtCore.Qt.Key_B)
        add_bookmark.setStatusTip('Add current line to bookmark')
        next_bookmark = QtGui.QAction(QtGui.QIcon('../icons/bookmarksnext.png'),'Next Bookmark',self)
        next_bookmark.setShortcut(QtCore.Qt.CTRL+QtCore.Qt.Key_Right)
        next_bookmark.setStatusTip('Go to next line in bookmarks')
        prev_bookmark = QtGui.QAction(QtGui.QIcon('../icons/bookmarksprev.png'),'Previous Bookmark',self)
        prev_bookmark.setShortcut(QtCore.Qt.CTRL+QtCore.Qt.Key_Left)
        prev_bookmark.setStatusTip('Go to previous line in bookmarks')
        clear_bookmark = QtGui.QAction(QtGui.QIcon('../icons/bookmarksclear.png'),'Clear Bookmarks',self)
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
        self.navigationmenu.addAction(go_to_matching_brace)
        self.navigationmenu.addSeparator()
        self.navigationmenu.addAction(add_bookmark)
        self.navigationmenu.addAction(next_bookmark)
        self.navigationmenu.addAction(prev_bookmark)
        self.navigationmenu.addAction(clear_bookmark)
        self.navigationmenu.addSeparator()

        projectmenu = menubar.addMenu('&Project')
        projectmenu.addAction(newprojectaction)        
        projectmenu.addAction(openproj)
        projectmenu.addSeparator() 
        projectmenu.addAction(self.addnew)
        projectmenu.addAction(self.addexisting)
        projectmenu.addSeparator() 
        projectmenu.addAction(save_project)
        projectmenu.addAction(save_project_as)
        projectmenu.addAction(save_project_copy_as)
        projectmenu.addSeparator() 
        projectmenu.addAction(empty_project)
        projectmenu.addAction(close_project)
        projectmenu.addSeparator() 
        projectmenu.addAction(projectmanager)

        self.connect(go_to_matching_brace,QtCore.SIGNAL('triggered()'),self.go_to_matching_brace_triggered)
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

        ####Debug Menu#####
        self.gdb_console = QtGui.QAction('Open GDB Console',self)
        self.gdb_console.setShortcut('F9')
        self.connect(self.gdb_console,QtCore.SIGNAL('triggered()'),self.gdb_console_triggered)

        self.gdb_run = QtGui.QAction(QtGui.QIcon('../icons/gdb_run.png'),"Run with GDB",self)
        self.connect(self.gdb_run,QtCore.SIGNAL('triggered()'),self.gdb_run_triggered)
                                                                                      
        self.gdb_continue=QtGui.QAction(QtGui.QIcon('../icons/continue.png'),'Continue',self)
        self.connect(self.gdb_continue,QtCore.SIGNAL('triggered()'),self.gdb_continue_triggered)
        
        self.gdb_stop=QtGui.QAction(QtGui.QIcon('../icons/stop.ico'),'Stop',self)
        self.connect(self.gdb_stop,QtCore.SIGNAL('triggered()'),self.gdb_stop_triggered)
        
        self.gdb_breakpoint_new=QtGui.QAction(QtGui.QIcon('../icons/breakpoint-new.png'),'New Breakpoint',self)
        self.connect(self.gdb_breakpoint_new,QtCore.SIGNAL('triggered()'),self.gdb_breakpoint_new_triggered)
        
        self.gdb_breakpoint_enable_all=QtGui.QAction(QtGui.QIcon('../icons/breakpoint-enableall.png'),'Enable All Breakpoints',self)
        self.connect(self.gdb_breakpoint_enable_all,QtCore.SIGNAL('triggered()'),self.gdb_breakpoint_enable_all_triggered)
        
        self.gdb_breakpoint_disable_all=QtGui.QAction(QtGui.QIcon('../icons/breakpoint-disableall.png'),'Disable All Breakpoints',self)
        self.connect(self.gdb_breakpoint_disable_all,QtCore.SIGNAL('triggered()'),self.gdb_breakpoint_disable_all_triggered)
        
        self.gdb_breakpoint_remove_all=QtGui.QAction(QtGui.QIcon('../icons/breakpoint-removeall.png'),'Remove All Breakpoints',self)
        self.connect(self.gdb_breakpoint_remove_all,QtCore.SIGNAL('triggered()'),self.gdb_breakpoint_remove_all_triggered)
        
        self.gdb_next=QtGui.QAction(QtGui.QIcon('../icons/next.ico'),'Next',self)
        self.connect(self.gdb_next,QtCore.SIGNAL('triggered()'),self.gdb_next_triggered)
        
        self.gdb_step_out=QtGui.QAction(QtGui.QIcon('../icons/step_out.ico'),'Step Out',self)
        self.connect(self.gdb_step_out,QtCore.SIGNAL('triggered()'),self.gdb_step_out_triggered)
        
        self.gdb_step=QtGui.QAction(QtGui.QIcon('../icons/step.ico'),'Step',self)
        self.connect(self.gdb_step,QtCore.SIGNAL('triggered()'),self.gdb_step_triggered)
        
        self.gdb_step_into_asm=QtGui.QAction(QtGui.QIcon('../icons/step_into_asm.ico'),'Step into asm',self)
        self.connect(self.gdb_step_into_asm,QtCore.SIGNAL('triggered()'),self.gdb_step_into_asm_triggered)
        
        self.gdb_step_over_asm=QtGui.QAction(QtGui.QIcon('../icons/step_over_asm.ico'),'Step over asm',self)
        self.connect(self.gdb_step_over_asm,QtCore.SIGNAL('triggered()'),self.gdb_step_over_asm_triggered)

        self.show_locals = QtGui.QAction('Local Variables',self)
        self.connect(self.show_locals,QtCore.SIGNAL('triggered()'),self.show_locals_triggered)
        
        debugmenu = menubar.addMenu('Debug')
        debugmenu.addAction(self.gdb_console)
        debugmenu.addSeparator()
        debugmenu.addAction(self.gdb_run)
        debugmenu.addAction(self.gdb_continue)
        debugmenu.addAction(self.gdb_stop)
        debugmenu.addSeparator()
        debugmenu.addAction(self.gdb_breakpoint_new)
        debugmenu.addAction(self.gdb_breakpoint_enable_all)
        debugmenu.addAction(self.gdb_breakpoint_disable_all)
        debugmenu.addAction(self.gdb_breakpoint_remove_all)
        debugmenu.addSeparator()
        debugmenu.addAction(self.gdb_next)
        debugmenu.addAction(self.gdb_step)
        debugmenu.addAction(self.gdb_step_out)
        debugmenu.addAction(self.gdb_step_into_asm)
        debugmenu.addAction(self.gdb_step_over_asm)
        debugmenu.addSeparator()
        debugmenu.addAction(self.show_locals)
            
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
        toolbar = self.addToolBar('Toolbar')
        toolbar.addAction(filenew)
        toolbar.addAction(fileopen)
        toolbar.addAction(filesave)
        toolbar.addAction(filesaveas)
        toolbar.addAction(fileprint)
        toolbar.addSeparator()
        toolbar.addAction(newprojectaction)
        toolbar.addAction(openproj)
        toolbar.addAction(close_project)
        toolbar.addAction(projectmanager)
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
        toolbar.addAction(uppercaseselection)
        toolbar.addAction(lowercaseselection)
        toolbar.addAction(commentout_multiline)
        toolbar.addAction(uncommentout_multiline)
        toolbar.addSeparator()
        toolbar.addAction(toolbarcompile)
        toolbar.addAction(toolbarrun)
        toolbar.addSeparator()
        toolbar.addAction(self.gdb_run)
        toolbar.addAction(self.gdb_continue)
        toolbar.addAction(self.gdb_stop)
        toolbar.addSeparator()
        toolbar.addAction(self.gdb_breakpoint_new)
        toolbar.addAction(self.gdb_breakpoint_enable_all)
        toolbar.addAction(self.gdb_breakpoint_disable_all)
        toolbar.addAction(self.gdb_breakpoint_remove_all)
        toolbar.addSeparator()
        toolbar.addAction(self.gdb_next)
        toolbar.addAction(self.gdb_step)
        toolbar.addAction(self.gdb_step_out)
        toolbar.addAction(self.gdb_step_into_asm)
        toolbar.addAction(self.gdb_step_over_asm)
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
        toolbar_rect = toolbar.geometry()
        toolbar_rect.setHeight(60)
        toolbar.setGeometry(toolbar_rect)
        
        toolbar.setIconSize(QtCore.QSize(20,20))
        
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
        
        self.projtreeitemarray = []
        self.tracktabsarray = []
        self.funcnewprojcalled = False
        self.funcaddnewcalled = False
        
        self.createTreeItem = True
        
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

    def setFilePointer(self,filepath,line):

        filepath=str(filepath)
        for txtInput in self.txtarray:
            if txtInput.filename==filepath:
                txtInput.setLinePointerAtLine(line)
        self.activateWindow()
        
    def processStoppedBreakpointHit(self,filepath,line):

        self.setFilePointer(filepath,line)

    def processStoppedSignalRecieved(self,signal_name,filepath,line):

        self.setFilePointer(filepath,line)
        QtGui.QMessageBox.information(self,"AthenaIDE","Program Received "+signal_name,QtGui.QMessageBox.Ok)

    def processStopped(self):

        QtGui.QMessageBox.information(self,"AthenaIDE","Program Stopped ",QtGui.QMessageBox.Ok)
        
###Debug Menu#####

    def gdbConsoleDialogShowLocals(self,string):

        self.show_locals_dlg.setExpressions(string)
        
    def show_locals_triggered(self):

        self.show_locals_dlg = locals_dlg.LocalVarsDialog(self)
        self.gdbConsoleDialog.gdbConsoleEdit.runCommand('-stack-list-variables 1')
        self.show_locals_dlg.exec_()
        
    def gdb_console_triggered(self):

        self.gdbConsoleDialog.show()

    def gdb_run_triggered(self):

        if self.filestate[self.tabs.currentIndex()] == 'opened':
            
                try:
                    f1 = self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.current_proj.list_files[self.tabs.currentIndex()])
                    
                
        if self.filestate[self.tabs.currentIndex()] == 'saved':
            
                try:
                    f1 = self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.current_proj.list_files[self.tabs.currentIndex()])
                
        if self.filestate[self.tabs.currentIndex()] == 'new':
            ask = QtGui.QMessageBox.question(self,'Compile','Your File is not saved, file should be saved before compilation! ',QtGui.QMessageBox.Ok,QtGui.QMessageBox.Cancel)
            if ask == QtGui.QMessageBox.Ok:
                self.funcsaveasfile()
                
                try:
                    f1= self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.current_proj.list_files[self.tabs.currentIndex()])
        
        s,ext = self.fileandext
        if self.mode == 'Project':
            f1 = []
            
            for d in self.current_proj.list_files:
                f1.append(self.correctfilename(d))
            a = f1[0].split('/')
            s = ''
            for i in range(1,len(a)-1):
                    s = s + '/' + a[i]
            ext = f1[0].split('.')[1]
            
            if os.path.exists(self.current_proj.out_dir)==False:
                os.mkdir(self.current_proj.out_dir)
            self.compilefile = os.path.join(self.current_proj.out_dir,'tempfile')
            f2 = self.compilefile
            
        if self.mode == 'File':
                
            a = f1.split('/')
            
            s = ''
            for i in range(1,len(a)-1):
                s = s + '/' + a[i]
            ext = f1.split('.')[1]
            self.compilefile = s +'/'+ 'tempfile'
            f2 = self.compilefile
        
        if s != '':
                if ext == 'C' or ext == 'c' or self.current_proj.proj_type == "C Project":
                        if f2 != '':
                            
                            if self.mode == "File":
                                self.runcompiler.gcccompiler_run_debug(f1,f2,self.mode,self.txtarray,self.tabs,self.filepatharray,self.tracktabsarray)
                            if self.mode == "Project":                                
                                self.runcompiler.gcccompiler_run_debug(f1,f2,self.mode,self.txtarray,self.tabs,self.current_proj.list_files,self.tracktabsarray,self.current_proj.get_compiler_command())
                            self.runcompiler.show()
                                                                      
                if ext == 'CPP' or ext == 'cpp' or self.current_proj.proj_type == "C++ Project":
                    if f2 != '':
                        if self.mode == "File":
                            self.runcompiler.gppcompiler_run_debug(f1,f2,self.mode,self.txtarray,self.tabs,self.filepatharray,self.tracktabsarray,[])
                        if self.mode == "Project":                            
                            self.runcompiler.gppcompiler_run_debug(f1,f2,self.mode,self.txtarray,self.tabs,self.current_proj.list_files,self.tracktabsarray,self.projCompiledTimes,self.current_proj.get_compiler_command())
                            self.projCompiledTimes[0]+=1
                        self.runcompiler.show()

    def gdb_continue_triggered(self):

        self.gdbConsoleDialog.process_terminal.runCommand('Continuing Program')
        self.gdbConsoleDialog.process_terminal.show()
        for txtInput in self.txtarray:
            txtInput.hideLinePointer()
        self.gdbConsoleDialog.gdbConsoleEdit.runCommand('-exec-continue')        

    def gdb_stop_triggered(self):

        self.gdbConsoleDialog.gdbConsoleEdit.runCommand('stop')
        self.gdbConsoleDialog.process_terminal.runCommand('Program Stopped')
        self.gdbConsoleDialog.process_terminal.show()
        
    def gdb_breakpoint_new_triggered(self):

        self.set_breakpoint_dlg = set_breakpoint.SetBreakpointDialog(self)
        self.connect(self.set_breakpoint_dlg,QtCore.SIGNAL('finished(int)'),self.set_breakpoint_dlg_finished)
        self.set_breakpoint_dlg.exec_()

    def set_breakpoint_dlg_finished(self,result):

        if result==1:
            command=""
            if self.set_breakpoint_dialog.rbFunction.isChecked()==True:
                command = '-break-insert ' + str(self.set_breakpoint_dialog.lineEditFunction.text()) + '\n'                
                self.list_breakpoints.append(FunctionBreakpoint(1,str(self.set_breakpoint_dialog.lineEditFunction.text())))
                
            if self.set_breakpoint_dialog.rbSourceFile.isChecked()==True:
                command = '-break-insert ' + str(self.set_breakpoint_dialog.lineEditFileName.text()) +':'+ str(self.set_breakpoint_dialog.lineEditLineNumber.text())+'\n'                
                self.list_breakpoints.append(LineBreakpoint(1,str(self.set_breakpoint_dialog.lineEditLineNumber.text()),str(self.set_breakpoint_dialog.lineEditFileName.text())))
                
            if self.set_breakpoint_dialog.rbAddress.isChecked()==True:
                command = '-break-insert *' + str(self.set_breakpoint_dialog.lineEditAddress.text()) + '\n'                
                self.list_breakpoints.append(AddressBreakpoint(1,str(self.set_breakpoint_dialog.lineEditAddress.text())))
            self.list_gdb_commands.append(command)
            
    def gdb_breakpoint_enable_all_triggered(self):

        self.gdb_breakpoint_disable_all_triggered()
        ###Enable all
    
    def gdb_breakpoint_disable_all_triggered(self):

        self.list_gdb_commands=[]
        if self.mode=="File":
            self.txtarray[self.tabs.currentIndex()].list_breakpoints_command=[]
        else:
            for txt in self.txtarray:
                txt.list_breakpoints_command=[]
            
    def gdb_breakpoint_remove_all_triggered(self):
        
        if self.mode=="File":
            self.txtarray[self.tabs.currentIndex()].list_breakpoints_command=[]
            self.txtarray[self.tabs.currentIndex()].list_breakpoints=[]
        else:
            for txt in self.txtarray:
                txt.list_breakpoints_command=[]
                txt.list_breakpoints=[]
                
    def gdb_next_triggered(self):
        
        self.gdbConsoleDialog.gdbConsoleEdit.runCommand('-exec-next')
        
    def gdb_step_out_triggered(self):
        
        self.gdbConsoleDialog.gdbConsoleEdit.runCommand('-exec-finish')
        
    def gdb_step_triggered(self):
        
        self.gdbConsoleDialog.gdbConsoleEdit.runCommand('-exec-step')
        
    def gdb_step_into_asm_triggered(self):
        
        self.gdbConsoleDialog.gdbConsoleEdit.runCommand('-exec-next-instruction')
                                                                 
    def gdb_step_over_asm_triggered(self):

        self.gdbConsoleDialog.gdbConsoleEdit.runCommand('-exec-step-instruction')
        
#Project Menu Functions
    def save_project_triggered(self):

        if mode=="File":
            return

        for i in range(self.tabs.count()):
            self.tabs.setCurrentIndex(i)
            self.savedialog()
            
    def save_project_as_triggered(self):

        self.save_project_as_dlg = save_as_project.SaveAsProjectDlg(self)
        self.connect(self.save_project_as_dlg,QtCore.SIGNAL('finished(int)'),self.save_project_as_dlg_finished)
        self.save_project_as_dlg.exec_()
        
    def save_project_as_dlg_finished(self,state):

        if state == 1:

            self.current_proj.proj_name = str(self.save_project_as_dlg.lineEditName.text())
            self.current_proj.proj_path = str(self.save_project_as_dlg.lineEditLocation.text())
            self.current_proj.proj_file=""
            self.current_proj.write_to_file()
            for file_path in self.current_proj.list_files:
                f = open(filepath,'r')
                s = ""
                for d in f:
                    s+=d
                f.close()
                f = open(os.path.join(self.current_proj.proj_path),filepath[filepath.rfind('/')+1:],'w')
                f.write(s)
                f.close()
            
    def save_project_copy_as_triggered(self):
        pass
    
    def empty_project_triggered(self):

        msg = QtGui.QMessageBox.question(self,'Empty Project','Are you sure you want to empty the project?',QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
        if msg == QtGui.QMessageBox.Yes:
            self.current_proj.clear_files()
            self.projectTree.clear()
            self.projectTreeItem = QtGui.QTreeWidgetItem(self.projectTree)
            self.projectTreeItem.setText(0,self.current_proj.proj_name)
            self.filepatharray=[]
            self.tabs.clear()
            
    def close_project_triggered(self):

        if self.current_proj.proj_name == "" and self.current_proj.proj_type=="" and self.current_proj.proj_file=="":
            return
        
        msg = QtGui.QMessageBox.question(self,'Close Project','Do you want to close the current project?',QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
        if msg == QtGui.QMessageBox.Yes:
            msg = QtGui.QMesssageBox.question(self,'Close Project','Do you want to save the project?',QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
            if msg==QtGui.QMessageBox.Yes:
                self.save_project_triggered()
            
            self.projectTree.clear()
            self.projectTree.hide()
            self.filepatharray=[]
            self.current_proj=project_class.project("","","")
            self.tabs.clear()
            self.tabs.hide()
            
####################
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

    def go_to_matching_brace_triggered(self):

        cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
        text = str(self.txtarray[self.tabs.currentIndex()].txtInput.toPlainText())
        brace_count = 0
        pos = cc.position()
        if text[cc.position()]=='{':
            
            pos = cc.position()+1
            brace_count = 1
            while brace_count !=0:
                if text[pos]=='{':
                    brace_count+=1
                if text[pos]=='}':
                    brace_count -=1
                pos+=1
        elif text[cc.position()-1]=='{':
            
            pos = cc.position()+2
            brace_count = 1
            while brace_count !=0:
                if text[pos]=='{':
                    brace_count+=1
                if text[pos]=='}':
                    brace_count -=1
                pos+=1
        elif text[cc.position()]=='}':
            
            pos = cc.position()-1
            brace_count = -1
            while brace_count !=0:
                if text[pos]=='{':
                    brace_count+=1
                if text[pos]=='}':
                    brace_count -=1
                pos-=1
        elif text[cc.position()-1]=='}':
            
            pos = cc.position()-1
            brace_count = -1
            while brace_count !=0:
                if text[pos]=='{':
                    brace_count+=1
                if text[pos]=='}':
                    brace_count -=1
                pos-=1
        cc.setPosition(pos,cc.MoveAnchor)
        self.txtarray[self.tabs.currentIndex()].txtInput.setTextCursor(cc)
            
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
                
        if self.mode=="File" or self.mode=="FILE":
            return
        if self.current_proj.proj_file=="":
            return
        
        self.winprojmanager = proj_manager.ProjManagerDlg(self.current_proj.proj_file,self)
        self.connect(self.winprojmanager,QtCore.SIGNAL('finished(int)'),self.projmanager_close_event)
        self.winprojmanager.exec_()
        
    def projmanager_close_event(self,state):

        if state==1:
            self.current_proj.proj_name = str(self.winprojmanager.lineEditName.text())
            self.projectTreeItem.setText(0,self.current_proj.proj_name)            
                
            newprojfilepatharray = []
            for i in range(self.winprojmanager.listViewFiles.count()):
                newprojfilepatharray.append(str(self.winprojmanager.listViewFiles.item(i).text()))   
            
            if newprojfilepatharray != self.current_proj.list_files:
                if len(newprojfilepatharray) == len(self.current_proj.list_files):
                    for i in range(len(newprojfilepatharray)):
                        self.projtreeitemarray[i].setText(0,self.getprojfilename(newprojfilepatharray[i]))
                        
                if len(newprojfilepatharray) < len(self.current_proj.list_files):
                    self.projectTree.clear()
                    self.projectTreeItem = QtGui.QTreeWidgetItem(self.projectTree)
                    self.projectTreeItem.setText(0,self.current_proj.proj_name)
                    self.projtreeitemarray=[]
                    for i in range(len(newprojfilepatharray)):
                        self.projtreeitemarray.append(QtGui.QTreeWidgetItem(self.projectTreeItem))
                        self.projtreeitemarray[len(self.projtreeitemarray)-1].setText(0,self.getprojfilename(newprojfilepatharray[len(self.projtreeitemarray)-1]))                
                        
                if len(newprojfilepatharray) > len(self.current_proj.list_files):
                    for i in range(len(self.current_proj.list_files)):
                        self.projtreeitemarray[i].setText(0,self.getprojfilename(newprojfilepatharray[i]))
                        
                    for i in range(len(newprojfilepatharray)-len(self.current_proj.list_files)):
                        self.projtreeitemarray.append(QtGui.QTreeWidgetItem(self.projectTreeItem))
                        self.projtreeitemarray[len(self.projtreeitemarray)-1].setText(0,self.getprojfilename(newprojfilepatharray[len(self.projtreeitemarray)-1]))
                
            self.current_proj.compile_only=self.winprojmanager.chkS.isChecked()
            self.current_proj.disable_inline=self.winprojmanager.chkfnoasm.isChecked()
            self.current_proj.define_symbols=self.winprojmanager.chkDefineSymbols.isChecked()
            self.current_proj.add_dir=self.winprojmanager.chkAddDirectories.isChecked()
            self.current_proj.warning_as_errors=self.winprojmanager.chkWerror.isChecked()
            self.current_proj.support_c89=self.winprojmanager.chkAnsi.isChecked()
            self.current_proj.compile_assemble=self.winprojmanager.chkC.isChecked()
            self.current_proj.optimize=self.winprojmanager.chkO.isChecked()
            self.current_proj.optimize_level=0
            self.current_proj.other_args=str(self.winprojmanager.lineEditOtherArgs.text())               
            self.current_proj.params=str(self.winprojmanager.lineEditParams.text())
            self.current_proj.run_on_ext_console=str(self.winprojmanager.chkRunOnExternalConsole.isChecked())
            self.current_proj.list_dir=[]
            for i in range(self.winprojmanager.listViewDirs.count()):
                _dir = str(self.winprojmanager.listViewDirs.item(i).text())
                if _dir!="":
                    self.current_proj.list_dir.append(_dir)
            self.current_proj.symbols=str(self.winprojmanager.lineEditSymbols.text())
            self.current_proj.list_env_var=""
            self.current_proj.curr_dir = str(self.winprojmanager.lineEditCurrDir.text())
            self.current_proj.out_dir = str(self.winprojmanager.lineEditOutDir.text())                
            self.current_proj.list_files = newprojfilepatharray
            self.current_proj.write_to_file()               
        
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

    def commentout_singleline_triggered(self):

        cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()

        selection_start = cc.selectionStart()
        selection_end = cc.selectionEnd()
        cc.clearSelection()
        
        cc.setPosition(selection_start,cc.MoveAnchor)
        line_start = cc.blockNumber()

        cc.setPosition(selection_end,cc.MoveAnchor)
        line_end = cc.blockNumber()

        cc.setPosition(selection_start,cc.MoveAnchor)
        cc.movePosition(cc.StartOfLine,cc.MoveAnchor)
        
        while line_start != line_end:
            self.txtarray[self.tabs.currentIndex()].txtInput.setTextCursor(cc)
            cc.insertText('//')
            cc.movePosition(cc.Down,cc.MoveAnchor)
            cc.setPosition(cc.position()-2,cc.MoveAnchor)
            line_start +=1

    def uncommentout_singleline_triggered(self):

        cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()

        selection_start = cc.selectionStart()
        selection_end = cc.selectionEnd()
        cc.clearSelection()
        
        cc.setPosition(selection_start,cc.MoveAnchor)
        line_start = cc.blockNumber()

        cc.setPosition(selection_end,cc.MoveAnchor)
        line_end = cc.blockNumber()

        cc.setPosition(selection_start,cc.MoveAnchor)
        cc.movePosition(cc.StartOfLine,cc.MoveAnchor)
        
        while line_start != line_end:
            self.txtarray[self.tabs.currentIndex()].txtInput.setTextCursor(cc)          
            cc.setPosition(cc.position()+2,cc.KeepAnchor)
            if str(cc.selectedText())=='//':
                cc.removeSelectedText()            
            cc.movePosition(cc.Down,cc.MoveAnchor)            
            line_start +=1

        self.txtarray[self.tabs.currentIndex()].txtInput.setTextCursor(cc)          
        cc.setPosition(cc.position()+2,cc.KeepAnchor)
        if str(cc.selectedText())=='//':
            cc.removeSelectedText()            
        cc.movePosition(cc.Down,cc.MoveAnchor)
        
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
                        
                        if self.current_proj.list_files[self.tracktabsarray[self.notsavedarray[i]]] != '':

                            os.remove(self.current_proj.list_files[self.tracktabsarray[self.notsavedarray[i]]])
                            f = open(self.current_proj.list_files[self.tracktabsarray[self.notsavedarray[i]]],'w')
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
                    if self.strequal(s,unicode(self.txtarray[i].txtInput.toPlainText(),'utf-8',errors='ignore')) == False:
                        self.notsavedarray.append(i)
                else:
                    if str(self.txtarray[i].txtInput.toPlainText()) !='':
                        self.notsavedarray.append(i)
                        
        if self.mode == 'Project':
            self.notsavedarray = []
            for i in range(self.tabs.count()):
                
                projfilepath = self.current_proj.list_files[self.tracktabsarray[i]]                
                if projfilepath !="":
                    f = open(projfilepath,'r')
                    s = ''
                    for d in f:
                        s +=d
                    f.close()
                    s = unicode(s,'utf-8',errors='ignore')
                    if self.strequal(s,unicode(self.txtarray[i].txtInput.toPlainText(),'utf-8',errors='ignore')) == False:
                       self.notsavedarray.append(i)
                else:
                    if unicode(self.txtarray[i].txtInput.toPlainText(),'utf-8',errors='ignore') !='':
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

        filename = unicode(filename,'utf-8',errors='ignore')
        return filename[:filename.rfind('/')]
    
    def funcopenproj(self):

        projpath = ''
        
        projpath = str(QtGui.QFileDialog.getOpenFileName(self,'Open Project',self.filedialogdir,('C Project Files(*.cproj);;C++ Project Files(*.cppproj);;All Files(*.*)')))
            
        
        if projpath != '':
            self.projCompiledTimes=[0]
            filedialogdir = self.getdir(str(projpath))
            
            self.mode = 'Project'
            self.projtreeitemarray=[]
            self.tabs.clear()
            self.txtarray=[]
            self.filepatharray=[]
            self.filestate=[]
            self.encodingarray=[]
            self.linestrackarray=[]
            openprojfile = open(str(projpath),'r+')
            openprojstring = ''
            self.projectdock.show()
            for d in openprojfile:
                openprojstring = openprojstring + d
            
            if self.current_proj.proj_name == '':
                self.createTreeItem = True
            else:
                self.createTreeItem = False

            self.current_proj.clear()
            self.current_proj.proj_file=projpath
            self.current_proj.create_from_string(openprojstring)            
            
            if self.createTreeItem == True:
                self.projectTree.setColumnCount(1)
                self.projectTreeItem = QtGui.QTreeWidgetItem(self.projectTree)
                self.projectTreeItem.setText(0,self.current_proj.proj_name)
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
                self.projectTreeItem.setText(0,self.current_proj.proj_name)                
            
            list_proj_files = self.current_proj.list_files
            for i in range(0,len(list_proj_files)):
                self.projtreeitemarray.append(QtGui.QTreeWidgetItem(self.projectTreeItem))
                self.projtreeitemarray[i].setText(0,self.getprojfilename(list_proj_files[i]))
            
            self.addnew.setEnabled(True)
            self.addexisting.setEnabled(True)
            
    def getprojfilename(self,path):
        
        return path[path.rfind('/')+1:]
    
    def projectTreeClicked(self,item,index):

        global docstr
        ##Remember to correct this code of fucking function written by me, at that time I was just a kid :P
        index = self.projtreeitemarray.index(item)
        filepath = self.current_proj.list_files[index]
        self.fileandext = filepath[filepath.rfind('/')+1:],filepath[filepath.rfind('.')+1:]
        s,ext = self.fileandext
        self.index = index

        cancreate = False
        
        for i in range(0,int(self.tabs.count())):
            if s == str(self.tabs.tabText(i)):
                return        
    
        page = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout()
        self.txtarray.append(txtinput.codewidget(self.current_proj.proj_type,self))
        vbox.addWidget(self.txtarray[self.tabs.count()])
        page.setLayout(vbox)
        self.tabs.addTab(page, s)
        
        docstr = ''
        self.txtarray[self.tabs.count()-1].filename = filepath
        self.txtarray[self.tabs.count()-1].txtInput.setPlainText('')
        txtInput = self.txtarray[self.tabs.count()-1].txtInput
        self.txtarray[self.tabs.count() - 1].indentwidth = self.indentwidth
        self.txtarray[self.tabs.count() - 1].indentTF = self.indent
        self.txtarray[self.tabs.count() - 1].inc_indent_syms = self.inc_indent_syms
        self.txtarray[self.tabs.count() - 1].dec_indent_syms = self.dec_indent_syms
        
        self.readProjFileThread = ReadFileThread(filepath,self)
        #self.connect(self.readProjFileThread,QtCore.SIGNAL('finished()'),self.readProjFileThreadFinished)
        #self.readProjFileThread.start()
        self.readProjFileThread.run()
        self.readProjFileThreadFinished()
        
    def readProjFileThreadFinished(self):

        s,ext = self.fileandext
        docstr = self.readProjFileThread.file_string
        
        txtInput = self.txtarray[self.tabs.count()-1].txtInput
        txtInput.setPlainText(docstr)
        self.txtarray[self.tabs.count() - 1].show_combo_boxes(self.current_proj.proj_type)            
        self.tracktabsarray.append(self.index)#Here self.tracktabsarray stores the index of file and self.tracktabsindex[self.tabs.currentIndex()] will give the index of tabs which displays the file.
        #or you can say index of file in projfilepatharray = self.tracktabsarray[self.tabs.currentIndex()}
       
        if ext == 'c' or ext=='C' or self.current_proj.proj_type == 'C Project':
            
            highlight = syntaxc.CHighlighter(self.txtarray[self.tabs.count()-1].txtInput.document())            
            txtInput.fill_c_code_completion()
            self.addtoencodingarray(self.tabs.count()-1,'C') 
        else:
            if ext == 'cpp' or ext =='CPP' or self.current_proj.proj_type == 'C++ Project':                
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

        self.tabs.show()            
        self.connect(self.txtarray[self.tabs.count()-1].txtInput, QtCore.SIGNAL('textChanged()'),self.textchanged)
        self.connect(self.txtarray[self.tabs.count()-1].txtInput, QtCore.SIGNAL('cursorPositionChanged()'),self.OnMousePressed)
        
    def funcaddexisting(self):
        
        addexistingfilepath = QtGui.QFileDialog.getOpenFileName(self,'Open File',self.current_proj.proj_path,('C Files(*.c);;C++ Files(*.cpp);;Header Files(*.h);;All Files(*.*)'))
        if addexistingfilepath!="":            
            self.filedialogdir = self.getdir(addexistingfilepath)
            
            addexistingfilename = addexistingfilepath[addexistingfilepath.rfind('/')+1:]
            addexistingfilename = addexistingfilepath[addexistingfilepath.rfind('.')+1:]
            
            self.projtreeitemarray.append(QtGui.QTreeWidgetItem(self.projectTreeItem))
            self.projtreeitemarray[len(self.projtreeitemarray)-1].setText(0,addexistingfilename)
            self.current_proj.append_file(str(addexistingfilepath))
            self.projfile = open(self.projpath,'a')
            self.projfile.write('<file>' + addexistingfilepath + '</file>')
            self.projfile.close()
            if '.h' in self.addexistingfilepath:
                self.includefileslist.append(s)            
        
    def funcaddnew(self):

        addnewfilepath = str(QtGui.QFileDialog.getSaveFileName(self,'Save File',self.current_proj.proj_path,('C Files(*.c);;C++ Files(*.cpp);;Header Files(*.h);;All Files(*.*)')))
        if addnewfilepath !="":
            self.projtreeitemarray.append(QtGui.QTreeWidgetItem(self.projectTreeItem))
            self.projtreeitemarray[len(self.projtreeitemarray)-1].setText(0,addnewfilepath)
            self.current_proj.append_file(addnewfilepath)
        
    def newproj_dlg_finished(self,result):

        if result==1:

            self.projCompiledTimes=[0]
            if self.current_proj.proj_name == '':
                self.createTreeItem = True
            else:
                self.createTreeItem = False
            self.current_proj.clear()
            self.projectdock.show()
            self.current_proj.proj_name = str(self.newproj_dlg.txtname.text())
            self.current_proj.proj_path = str(self.newproj_dlg.txtlocation.text())
            self.current_proj.proj_type = str(self.newproj_dlg.proj_type)
            self.mode = 'Project'
                    
            if self.createTreeItem == True:
                self.projectTree.setColumnCount(1)
                self.projectTreeItem = QtGui.QTreeWidgetItem(self.projectTree)
                self.projectTreeItem.setText(0,self.current_proj.proj_name)
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
                self.projectTreeItem.setText(0,self.current_proj.proj_name)
                
            if self.current_proj.proj_type == "GTK+ Project":
                self.current_proj.proj_type="C Project"
                self.current_proj.other_args="`pkg-config --cflags --libs gtk+-2.0 gtksourceview-2.0 vte`"
            elif self.current_proj.proj_type == "gtkmm Project":
                self.current_proj.proj_type="C++ Project"
                self.current_proj.other_args="`pkg-config gtkmm-2.4 --cflags --libs gtksourceviewmm-2.0 libvtemm-1.2`"
                
            self.current_proj.write()
            
            self.tabs.clear()
            
            for i in range(len(self.txtarray)):
                del self.txtarray[i]
                del self.filepatharray[i]
                del self.filestate[i]
                del self.encodingarray[i]
                    
    def funcnewproject(self):

        self.newproj_dlg = newproject.newprojectwin(self)
        self.newproj_dlg.show()
        self.connect(self.newproj_dlg,QtCore.SIGNAL('finished(int)'),self.newproj_dlg_finished)
        
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

        if self.mode == "File" and self.filestate[self.tabs.currentIndex()] == 'opened' or self.filestate[self.tabs.currentIndex()] == 'saved':
            
                #try:
                    #print 'lll'
                    f1 = self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                #except IndexError:
                #    f1 = self.correctfilename(self.current_proj.list_files[self.tabs.currentIndex()])
                
        if self.filestate[self.tabs.currentIndex()] == 'new':
            ask = QtGui.QMessageBox.question(self,'Compile','Your File is not saved, file should be saved before compilation! ',QtGui.QMessageBox.Ok,QtGui.QMessageBox.Cancel)
            if ask == QtGui.QMessageBox.Ok:
                self.funcsaveasfile()
                
                try:
                    f1= self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.current_proj.list_files[self.tabs.currentIndex()])
        
        s,ext = self.fileandext
        if self.mode == 'Project':
            f1 = []
            
            for d in self.current_proj.list_files:
                f1.append(self.correctfilename(d))
            a = f1[0].split('/')
            s = ''
            for i in range(1,len(a)-1):
                    s = s + '/' + a[i]
            ext = f1[0].split('.')[1]
            
            if os.path.exists(self.current_proj.out_dir)==False:
                os.mkdir(self.current_proj.out_dir)
            self.compilefile = os.path.join(self.current_proj.out_dir,'tempfile')
            f2 = self.compilefile
            
        if self.mode == 'File':
                
            a = f1.split('/')
            
            s = ''
            for i in range(1,len(a)-1):
                s = s + '/' + a[i]
            ext = f1[f1.rfind('.')+1:]
            self.compilefile = s +'/'+ 'tempfile'
            f2 = self.compilefile
        
        if s != '':
                if ext == 'C' or ext == 'c' or self.current_proj.proj_type == "C Project":
                        if f2 != '':
                            
                            if self.mode == "File":
                                print 'llllllll'
                                self.runcompiler.gcccompiler_run(f1,f2,self.mode,self.txtarray,self.tabs,self.filepatharray,self.tracktabsarray)
                            if self.mode == "Project":                                
                                self.runcompiler.gcccompiler_run(f1,f2,self.mode,self.txtarray,self.tabs,self.current_proj.list_files,self.tracktabsarray,self.current_proj.get_compiler_command())
                            self.runcompiler.show()
                                                                      
                if ext == 'CPP' or ext == 'cpp' or self.current_proj.proj_type == "C++ Project":
                    if f2 != '':
                        if self.mode == "File":
                            self.runcompiler.gppcompiler_run(f1,f2,self.mode,self.txtarray,self.tabs,self.filepatharray,self.tracktabsarray,[])
                        if self.mode == "Project":                            
                            self.runcompiler.gppcompiler_run(f1,f2,self.mode,self.txtarray,self.tabs,self.current_proj.list_files,self.tracktabsarray,self.projCompiledTimes,self.current_proj.get_compiler_command())
                            self.projCompiledTimes[0]+=1
                        self.runcompiler.show()
                                               
    def rungcccompiler(self):
        
        f2 = ''
        
        if self.filestate[self.tabs.currentIndex()] == 'opened':
            
                try:
                    f1 = self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.current_proj.list_files[self.tabs.currentIndex()])
                    
                self.compilefile = QtGui.QFileDialog.getSaveFileName(self,'Save File','')
        if self.filestate[self.tabs.currentIndex()] == 'saved':
            
                try:
                    f1 = self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.current_proj.list_files[self.tabs.currentIndex()])
                self.compilefile = QtGui.QFileDialog.getSaveFileName(self,'Save File','')
        if self.filestate[self.tabs.currentIndex()] == 'new':
            ask = QtGui.QMessageBox.question(self,'Compile','Your File is not saved, file should be saved before compilation! ',QtGui.QMessageBox.Ok,QtGui.QMessageBox.Cancel)
            if ask == QtGui.QMessageBox.Ok:
                self.funcsaveasfile()
                self.compilefile = QtGui.QFileDialog.getSaveFileName(self,'Save File','')
                try:
                    f1= self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.current_proj.list_files[self.tabs.currentIndex()])
                
        if self.mode == 'Project':
                f1 = []
                for d in self.current_proj.list_files:
                    f1.append(self.correctfilename(d))
                self.compilefile = QtGui.QFileDialog.getSaveFileName(self,'Save File',self.filedialogdir)
                self.filedialogdir = self.getdir(self.compilefile)
                
        f2 = self.correctfilename(self.compilefile)
        if f2 != '':                
                if self.mode == "File":                    
                    self.runcompiler.gcccompiler(f1,f2,self.mode,self.txtarray,self.tabs,self.filepatharray,self.tracktabsarray)
                if self.mode == "Project":
                    self.runcompiler.gcccompiler(f1,f2,self.mode,self.txtarray,self.tabs,self.current_proj.list_files,self.tracktabsarray)
                self.runcompiler.show()
               
    def rungppcompiler(self):
        
        f2 = ''
        if self.mode == 'File':            
            if self.filestate[self.tabs.currentIndex()] == 'opened':                                    
                try:
                    f1 = self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.current_proj.list_files[self.tabs.currentIndex()])
                
                self.compilefile = QtGui.QFileDialog.getSaveFileName(self,'Save File','')
            if self.filestate[self.tabs.currentIndex()] == 'saved':                   
                try:
                    f1 = self.correctfilename(self.filepatharray[self.tabs.currentIndex()])

                except IndexError:
                    f1 = self.correctfilename(self.current_proj.list_files[self.tabs.currentIndex()])
                
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
                for d in self.current_proj.list_files:
                    f1.append(self.correctfilename(d))
                self.compilefile = QtGui.QFileDialog.getSaveFileName(self,'Save File',self.filedialogdir)
                self.filedialogdir = self.getdir(self.compilefile)
        f2 = self.correctfilename(self.compilefile)
        
        if f2 != '':
            if self.mode == "File":
                self.runcompiler.gppcompiler(f1,f2,self.mode,self.txtarray,self.tabs,self.filepatharray,self.tracktabsarray)
                
            if self.mode == "Project":
                
                self.runcompiler.gppcompiler(f1,f2,self.mode,self.txtarray,self.tabs,self.current_proj.list_files,self.tracktabsarray,self.projCompiledTimes)
                
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
        
        if self.mode == 'File':            
            if self.filepatharray[self.tabs.currentIndex()] !='':
                
                f = open(self.filepatharray[self.tabs.currentIndex()],'r')
                s = ''
                
                for d in f:
                    s += d
                f.close()
                a = unicode(self.txtarray[self.tabs.currentIndex()].txtInput.toPlainText().toUtf8(),'utf-8',errors='ignore')
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

    def readFileThreadFinished(self):

        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        docstr = self.readFileThread.file_string
        openfname = self.readFileThread.filename
        
        if self.recentfiles=='True':
            self.fileandext = self.updatefilemenu(openfname)
        else:
            self.fileandext = openfname[:openfname.rindex('.')],openfname[openfname.rindex('.')+1:]
        s,ext = self.fileandext
        
        self.tabs.setTabText(self.tabs.currentIndex(),s)
        self.linestrackarray[self.tabs.currentIndex()]=[-1,-1,-1,-1,-1]
        doc = QtGui.QTextDocument(txtInput)
        doc.setDefaultFont(txtInput.currentFont())
        txtInput.setDocument(doc)        
        txtInput.setPlainText(docstr)
        if ext == 'c' or ext=='C':
            self.txtarray[self.tabs.currentIndex()].show_combo_boxes('C File')
            txtInput.setFileType('C File')
            txtInput.fill_c_code_completion()            
            highlight = syntaxc.CHighlighter(self.txtarray[self.tabs.currentIndex()].txtInput.document())
            self.addtoencodingarray(self.tabs.currentIndex(),'C') 
        else:
            if ext == 'cpp' or ext =='CPP':
                #Remember to add fill_c_code_completion like function for C++
                txtInput.setFileType('C++ File')
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
    
    def funcopen(self,openfname):
        
        global docstr
        
        docstr = ''                    
        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        self.txtarray[self.tabs.currentIndex()].filename = openfname
        
        if self.recentfiles=='True':
            self.fileandext = self.updatefilemenu(openfname)
        else:
            self.fileandext = openfname[:openfname.rindex('.')],openfname[openfname.rindex('.')+1:]
        s,ext = self.fileandext
        
        self.readFileThread = ReadFileThread(openfname,self)
        self.connect(self.readFileThread,QtCore.SIGNAL('finished()'),self.readFileThreadFinished)
        self.readFileThread.start() 
                
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
            if self.strequal(s,unicode(self.txtarray[self.tabs.currentIndex()].txtInput.toPlainText().toUtf8(),'utf-8',
                                       errors='ignore')):
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
            filepath = self.current_proj.list_files[self.tracktabsarray[self.tabs.currentIndex()]]
            ff = open(filepath,'w')
            ff.write(self.txtarray[self.tabs.currentIndex()].txtInput.toPlainText())
            ff.close()
            if filepath[filepath.find(".")+1:] == 'c':
                self.txtarray[self.tabs.currentIndex()].txtInput.fill_c_code_completion()
            if filepath[filepath.find(".")+1:] == 'cpp':
                self.txtarray[self.tabs.currentIndex()].txtInput.fill_cpp_code_completion()
            if filepath[filepath.find(".")+1:] == 'h':
                if self.current_proj.proj_type == 'C++ Project':
                    self.txtarray[self.tabs.currentIndex()].show_combo_boxes('C++ Project')
                    self.txtarray[self.tabs.currentIndex()].txtInput.fill_cpp_code_completion()
                if self.current_proj.proj_type == 'C Project':
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
            q = txtInput.toPlainText()
            codec_utf_8 = QtCore.QTextCodec.codecForName('UTF-8')
            
            q = unicode(codec_utf_8.fromUnicode(q),'utf-8',errors='strict')
            
            f = open(savefname,'w')
            f.write(q)
            f.close()
            #f = QtCore.QFile(savefname)
            #f.open()
            #f.write(txtInput.toPlainText().toUtf8())
            #f.close()
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
        
    def select_current_function_triggered(self):

        current_index = self.txtarray[self.tabs.currentIndex()].combo_func.currentIndex()
        filetype = self.txtarray[self.tabs.currentIndex()].txtInput.filetype
        if filetype == 'C File' or filetype == 'C Project':
            current_func_pos = self.txtarray[self.tabs.currentIndex()].combo_funcposarray[current_index]
            cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
            text = str(self.txtarray[self.tabs.currentIndex()].txtInput.toPlainText())            
            pos = current_func_pos
            
            while text[pos]!='{':
                pos+=1
            
            cc.setPosition(pos+1,cc.MoveAnchor)
            cc = self.txtarray[self.tabs.currentIndex()].txtInput.setTextCursor(cc)
            self.select_current_block_triggered()
        elif filetype == 'C++ File' or filetype == 'C++ Project':
            class_current_index = self.txtarray[self.tabs.currentIndex()].combo_class.currentIndex()
            current_func_pos = self.txtarray[self.tabs.currentIndex()].combo_funcposarray[class_current_index][current_index]
            cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
            text = str(self.txtarray[self.tabs.currentIndex()].txtInput.toPlainText())            
            pos = current_func_pos
            while text[pos]!='{':
                pos+=1
            cc.setPosition(pos+1,cc.MoveAnchor)
            self.select_current_block_triggered()
            
    def select_current_block_triggered(self):

        cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
        text = str(self.txtarray[self.tabs.currentIndex()].txtInput.toPlainText())
        brace_count = 0
        pos = cc.position()
        while text[pos]!='{':
            pos-=1
        opening_brace_pos = pos
        pos = cc.position()+1
        brace_count = 1
        while brace_count !=0:
            if text[pos]=='{':
                brace_count+=1
            if text[pos]=='}':
                brace_count -=1
            pos+=1

        cc.setPosition(opening_brace_pos,cc.MoveAnchor)
        cc.setPosition(pos,cc.KeepAnchor)
        self.txtarray[self.tabs.currentIndex()].txtInput.setTextCursor(cc)
        
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

    def fold_all_functions_triggered(self):

        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        filetype = txtInput.filetype
        text = str(txtInput.toPlainTextWithHidden())
        if filetype == 'C File' or filetype == 'C Project':
            for i in range(len(self.txtarray[self.tabs.currentIndex()].combo_funcposarray)-1,-1,-1):
                pos = self.txtarray[self.tabs.currentIndex()].combo_funcposarray[i]                
                while text[pos]!='{':
                        pos+=1
    
                txtInput.setTextVisible(pos,-1)
        
    def unfold_all_functions_triggered(self):

        pass
                                  
    def fold_current_block_triggered(self):

        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        cc = txtInput.textCursor()
        pos = cc.position()
        text = str(txtInput.toPlainText())
        while text[pos]!='{':
            pos -=1
        txtInput.setTextVisible(pos,-1)
        
    def fold_current_function_triggered(self):

        txtInput = self.txtarray[self.tabs.currentIndex()].txtInput
        current_index = self.txtarray[self.tabs.currentIndex()].combo_func.currentIndex()
        filetype = self.txtarray[self.tabs.currentIndex()].txtInput.filetype
        text = str(self.txtarray[self.tabs.currentIndex()].txtInput.toPlainText())            
        pos = -1
        if filetype == 'C File' or filetype == 'C Project':
            current_func_pos = self.txtarray[self.tabs.currentIndex()].combo_funcposarray[current_index]
            cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()
            pos = current_func_pos            
            
        elif filetype == 'C++ File' or filetype == 'C++ Project':
            class_current_index = self.txtarray[self.tabs.currentIndex()].combo_class.currentIndex()
            current_func_pos = self.txtarray[self.tabs.currentIndex()].combo_funcposarray[class_current_index][current_index]
            cc = self.txtarray[self.tabs.currentIndex()].txtInput.textCursor()            
            pos = current_func_pos
            
        if pos==-1:
            return
        
        while text[pos]!='{':
                pos+=1
            
        cc.setPosition(pos+1,cc.MoveAnchor)
        cc = self.txtarray[self.tabs.currentIndex()].txtInput.setTextCursor(cc)
        txtInput.setTextVisible(pos,-1)
        
    def auto_complete_triggered(self):
        
        self.txtarray[self.tabs.currentIndex()].txtInput.show_word_completion()
    
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
