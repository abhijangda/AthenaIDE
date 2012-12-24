
#696 Lines

from PyQt4 import QtGui,QtCore
import sys,os,re
import loadexecutable
import breakpoints,call_function_file
import terminal_file,jump_win_file,get_variable_value_file,syntaxcpp

class NewTextEdit(QtGui.QTextEdit):

    def __init__(self,parent=None):

        QtGui.QTextEdit.__init__(self,parent)
        self.setWordWrapMode(0)
        
    def keyPressEvent(self,event):

        pass
        
class main_window(QtGui.QMainWindow):

    def __init__(self,parent=None):

        QtGui.QMainWindow.__init__(self,parent)

        self.setWindowTitle('AthenaDB')
        self.setGeometry(100,100,600,400)
        self.showMaximized()
        
        menubar = self.menuBar()
        
        filemenu = menubar.addMenu('&File')
        
        file_open_executable = QtGui.QAction(QtGui.QIcon('load-executable.png'),'Open Executable File',self)
        self.connect(file_open_executable,QtCore.SIGNAL('triggered()'),self.func_openexecutable)
        filemenu.addAction(file_open_executable)        
        file_open_executable.setShortcut('CTRL+O')
        file_open_executable.setStatusTip('Open an executable file')
        
        file_exit = QtGui.QAction(QtGui.QIcon('exit.png'),'Exit',self)
        self.connect(file_exit,QtCore.SIGNAL('triggered()'),self.funcexit)
        filemenu.addAction(file_exit)
        file_exit.setShortcut('CTRL+Q')
        file_exit.setStatusTip('Exit debugger')
        
        breakpointsmenu = menubar.addMenu('Breakpoints')

        self.breakpoints_create = QtGui.QAction(QtGui.QIcon('breakpoint-new.png'),'Create Breakpoint',self)
        self.connect(self.breakpoints_create,QtCore.SIGNAL('triggered()'),self.func_createbreakpoints)
        breakpointsmenu.addAction(self.breakpoints_create)
        self.breakpoints_create.setShortcut('CTRL+B')
        self.breakpoints_create.setStatusTip('Create a new breakpoint at specified location')
        self.breakpoints_create.setEnabled(False)
        
        breakpointsmenu.addSeparator()

        self.breakpoints_disable = QtGui.QAction(QtGui.QIcon('breakpoint-disable.png'),'Disable Breakpoint',self)
        self.connect(self.breakpoints_disable,QtCore.SIGNAL('triggered()'),self.func_disablebreakpoints)
        breakpointsmenu.addAction(self.breakpoints_disable)
        self.breakpoints_disable.setShortcut('CTRL+D')
        self.breakpoints_disable.setStatusTip('Disable the currently selected breakpoint')
        self.breakpoints_disable.setEnabled(False)
        
        self.breakpoints_disableall = QtGui.QAction(QtGui.QIcon('breakpoint-disableall.png'),'Disable All Breakpoints',self)
        self.connect(self.breakpoints_disableall,QtCore.SIGNAL('triggered()'),self.func_disableallbreakpoints)
        breakpointsmenu.addAction(self.breakpoints_disableall)
        self.breakpoints_disableall.setShortcut('CTRL+SHIFT+D')
        self.breakpoints_disableall.setStatusTip('Disable all the breakpoints')
        self.breakpoints_disableall.setEnabled(False)
        
        breakpointsmenu.addSeparator()

        self.breakpoints_enable = QtGui.QAction(QtGui.QIcon('breakpoint-enable.png'),'Enable Breakpoint',self)
        self.connect(self.breakpoints_enable,QtCore.SIGNAL('triggered()'),self.func_enablebreakpoints)
        breakpointsmenu.addAction(self.breakpoints_enable)
        self.breakpoints_enable.setShortcut('CTRL+E')
        self.breakpoints_enable.setStatusTip('Enable the currently selected breakpoint')
        self.breakpoints_enable.setEnabled(False)
        
        self.breakpoints_enableall = QtGui.QAction(QtGui.QIcon('breakpoint-enableall.png'),'Enable All Breakpoints',self)
        self.connect(self.breakpoints_enableall,QtCore.SIGNAL('triggered()'),self.func_enableallbreakpoints)
        breakpointsmenu.addAction(self.breakpoints_enableall)
        self.breakpoints_enableall.setShortcut('CTRL+SHIFT+E')
        self.breakpoints_enableall.setStatusTip('Enable the all the breakpoints')
        self.breakpoints_enableall.setEnabled(False)
        
        breakpointsmenu.addSeparator()
        
        self.breakpoints_remove = QtGui.QAction(QtGui.QIcon('breakpoint-remove.png'),'Remove Breakpoint',self)
        self.connect(self.breakpoints_remove,QtCore.SIGNAL('triggered()'),self.func_removebreakpoints)
        breakpointsmenu.addAction(self.breakpoints_remove)
        self.breakpoints_remove.setShortcut('CTRL+R')
        self.breakpoints_remove.setStatusTip('Removes the currently selected breakpoint')
        self.breakpoints_remove.setEnabled(False)
        
        self.breakpoints_removeall = QtGui.QAction(QtGui.QIcon('breakpoint-removeall.png'),'Remove All Breakpoints',self)
        self.connect(self.breakpoints_removeall,QtCore.SIGNAL('triggered()'),self.func_removeallbreakpoints)
        breakpointsmenu.addAction(self.breakpoints_removeall)      
        self.breakpoints_removeall.setShortcut('CTRL+SHIFT+R')
        self.breakpoints_removeall.setStatusTip('Remove all the breakpoints')
        self.breakpoints_removeall.setEnabled(False)
        
        viewmenu = menubar.addMenu('View')

        self.backtrace_show = QtGui.QAction('Backtrace',self)
        self.connect(self.backtrace_show,QtCore.SIGNAL('triggered()'),self.func_showbacktrace)
        viewmenu.addAction(self.backtrace_show)
        self.backtrace_show.setShortcut('ALT+B')
        self.backtrace_show.setStatusTip('Show Backtrace')
        self.backtrace_show.setEnabled(False)
        
        self.list_source = QtGui.QAction('Source',self)
        self.connect(self.list_source, QtCore.SIGNAL('triggered()'),self.func_list_source)
        viewmenu.addAction(self.list_source)
        self.list_source.setShortcut('ALT+S')
        self.list_source.setStatusTip('Show Source Code the current file')
        self.list_source.setEnabled(False)
        
        self.disassembly = QtGui.QAction('Assembly',self)
        self.connect(self.disassembly, QtCore.SIGNAL('triggered()'),self.func_disassembly)
        viewmenu.addAction(self.disassembly)
        self.disassembly.setShortcut('ALT+D')
        self.disassembly.setStatusTip('Show Assembly of the current file')
        self.disassembly.setEnabled(False)
        
        self.stack = QtGui.QAction('Stack',self)
        self.connect(self.stack, QtCore.SIGNAL('triggered()'),self.func_stack)
        viewmenu.addAction(self.stack)
        self.stack.setShortcut('ALT+SHIFT+S')
        self.stack.setStatusTip('Show Current Stack Frame')
        self.stack.setEnabled(False)
        
        self.registers = QtGui.QAction('Registers',self)
        self.connect(self.registers, QtCore.SIGNAL('triggered()'),self.func_registers)
        viewmenu.addAction(self.registers)
        self.registers.setShortcut('ALT+R')
        self.registers.setStatusTip('Show Registers in the Current Stack Frame')
        self.registers.setEnabled(False)
        
        runmenu = menubar.addMenu('Run')

        self.run_runprocess = QtGui.QAction(QtGui.QIcon('gdb-run.png'),'Run Process',self)
        self.connect(self.run_runprocess,QtCore.SIGNAL('triggered()'),self.func_run_process)
        runmenu.addAction(self.run_runprocess)
        self.run_runprocess.setShortcut('F5')
        self.run_runprocess.setStatusTip('Run Current Loaded File')
        self.run_runprocess.setEnabled(False)
        
        self.run_continue = QtGui.QAction(QtGui.QIcon('continue.png'),'Continue',self)
        self.connect(self.run_continue,QtCore.SIGNAL('triggered()'),self.func_run_continue)
        runmenu.addAction(self.run_continue)
        self.run_continue.setShortcut('CTRL+F5')
        self.run_continue.setStatusTip('Continue the Execution')
        self.run_continue.setEnabled(False)
        
        self.run_restartprocess = QtGui.QAction(QtGui.QIcon('restart.png'),'Restart Process',self)
        self.connect(self.run_restartprocess,QtCore.SIGNAL('triggered()'),self.func_run_restartprocess)
        runmenu.addAction(self.run_restartprocess)
        self.run_restartprocess.setShortcut('F10')
        self.run_restartprocess.setStatusTip('Restart the Current Loaded File')
        self.run_restartprocess.setEnabled(False)
        
        self.run_stopprocess = QtGui.QAction(QtGui.QIcon('stop.png'),'Stop Process',self)
        self.connect(self.run_stopprocess,QtCore.SIGNAL('triggered()'),self.func_run_stopprocess)
        runmenu.addAction(self.run_stopprocess)
        self.run_stopprocess.setShortcut('CTRL+X')
        self.run_stopprocess.setStatusTip('Kill the current inferior process')
        self.run_stopprocess.setEnabled(False)
        
        debugmenu = menubar.addMenu('Debug')
        
        self.debug_next = QtGui.QAction('Next',self)
        self.connect(self.debug_next, QtCore.SIGNAL('triggered()'),self.func_next)
        debugmenu.addAction(self.debug_next)
        self.debug_next.setShortcut('CTRL+N')
        self.debug_next.setStatusTip('Executes next line stepping over next function, if any')
        self.debug_next.setEnabled(False)
        
        self.debug_step = QtGui.QAction('Step',self)
        self.connect(self.debug_step, QtCore.SIGNAL('triggered()'),self.func_step)
        debugmenu.addAction(self.debug_step)
        self.debug_step.setShortcut('CTRL+S')
        self.debug_step.setStatusTip('Executes next line stepping into the function, if any')
        self.debug_step.setEnabled(False)
        
        self.debug_finish = QtGui.QAction('Finish',self)
        self.connect(self.debug_finish, QtCore.SIGNAL('triggered()'),self.func_finish)
        debugmenu.addAction(self.debug_finish)
        self.debug_finish.setShortcut('CTRL+F')
        self.debug_finish.setStatusTip('Executes next line stepping out the function, if any')
        self.debug_finish.setEnabled(False)
        
        self.debug_jump = QtGui.QAction('Jump to location',self)
        self.connect(self.debug_jump, QtCore.SIGNAL('triggered()'),self.func_jump)
        debugmenu.addAction(self.debug_jump)
        self.debug_jump.setShortcut('CTRL+J')
        self.debug_jump.setStatusTip('Start execution from specified location')
        self.debug_jump.setEnabled(False)
        
        debugmenu.addSeparator()
        
        self.call_function = QtGui.QAction('Call Function',self)
        self.connect(self.call_function, QtCore.SIGNAL('triggered()'),self.func_call_function)
        debugmenu.addAction(self.call_function)
        self.call_function.setShortcut('CTRL+SHIFT+F')
        self.call_function.setStatusTip('Call a function')
        self.call_function.setEnabled(False)
        
        self.print_value = QtGui.QAction('Print Variable',self)
        self.connect(self.print_value, QtCore.SIGNAL('triggered()'),self.func_print_value)
        debugmenu.addAction(self.print_value)
        self.print_value.setShortcut('CTRL+P')
        self.print_value.setStatusTip('Print Value of a Variable')
        self.print_value.setEnabled(False)
        
        self.tabs = QtGui.QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.txtoutput = NewTextEdit(self)
        self.tabs.addTab(self.txtoutput,"Output")

        self.txtbacktrace = NewTextEdit(self)
        self.tabs.addTab(self.txtbacktrace,"Backtrace")

        toolbar = self.addToolBar('Toolbar')
        toolbar.addAction(file_open_executable)
        toolbar.addSeparator()
        toolbar.addAction(self.run_runprocess)
        toolbar.addAction(self.run_continue)
        toolbar.addAction(self.run_restartprocess)
        toolbar.addAction(self.run_stopprocess)
        toolbar.addSeparator()
        toolbar.addAction(self.breakpoints_create)
        toolbar.addAction(self.breakpoints_disable)
        toolbar.addAction(self.breakpoints_disableall)
        toolbar.addAction(self.breakpoints_enable)
        toolbar.addAction(self.breakpoints_enableall)
        toolbar.addAction(self.breakpoints_remove)
        toolbar.addAction(self.breakpoints_removeall)
        toolbar.addSeparator()
        toolbar.addAction(file_exit)        
        
        self.tablebreakpoints = QtGui.QTableWidget(self)
        self.tablebreakpoints.setColumnCount(6)
        self.tablebreakpoints.setHorizontalHeaderLabels(['Enable','ID','Filename','Line','Function','Address'])
        self.tablebreakpoints.itemClicked.connect(self.tablebreakpoints_clicked)
        self.tablebreakpoints.setRowCount(1)
        self.tablebreakpoints_itemarray=[]
        self.breakpoints_count = 0
        self.breakpoints_array = []
        
        self.tabs.addTab(self.tablebreakpoints,"Breakpoints")

        self.txtsource = NewTextEdit(self)
        self.tabs.addTab(self.txtsource,"Source Code")

        self.txtassembly = NewTextEdit(self)
        self.tabs.addTab(self.txtassembly,"Assembly")

        self.tablestack = QtGui.QTableWidget(self)
        self.tabs.addTab(self.tablestack,"Stack")
        self.tablestack.setColumnCount(5)
        self.tablestack.setHorizontalHeaderLabels(['Frame','Function','Arguments','Location','Address'])
        self.tablestack.itemClicked.connect(self.tablebreakpoints_clicked)
        self.tablestack_itemarray=[]
        self.tablestack.setRowCount(1) 

        self.txtregister = NewTextEdit(self)
        self.tabs.addTab(self.txtregister,"Registers")
        
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("")
        
        self.process = QtCore.QProcess(self)
        self.command = ''
        self.direct_to_terminal = False

    def closeEvent(self,event):
        
        try:            
            if self.terminal_win.isVisible() == True:
                self.terminal_win.close()
        except:
            pass
        
    def print_variable(self):

        self.command = 'print ' + str(self.print_variable_win.txtvariable.text()) + '\n'
        self.process.write(self.command)
        
    def func_print_value(self):

        self.print_variable_win = get_variable_value_file.get_variable_value_dialog(self)
        self.connect(self.print_variable_win, QtCore.SIGNAL('print()'),self.print_variable)
        self.print_variable_win.show()
        
    def call_function(self):

        self.command = 'call ' + str(self.call_func_win.txtfunction.text()) + '\n'
        self.process.write(self.command)
        
    def func_call_function(self):

        self.call_func_win = call_function_file.call_function_dialog(self)
        self.call_func_win.show()
        self.connect(self.call_func_win, QtCore.SIGNAL('call()'),self.call_function)
        
    def func_stack(self):

        self.command = 'frame 0\n'
        self.process.write(self.command)
        self.frame_count = 0
        self.tabs.setCurrentIndex(5)
        self.tablestack.clearContents()
        
    def func_list_source(self):
        
        self.command = 'list 0\n'
        self.process.write(self.command)
        self.tabs.setCurrentIndex(3)        
        
    def tablebreakpoints_clicked(self,item):
        
        for i in range(6):
            self.tablebreakpoints.setItemSelected(self.tablebreakpoints.item(item.row(),i),True)

    def func_registers(self):

        self.command = 'info all-registers\n'
        self.process.write(self.command)
        self.tabs.setCurrentIndex(6)
        
    def func_disassembly(self):

        self.command = 'info line 1\n'
        self.process.write(self.command)        
        self.info_line = 1
        self.address_line = []
        self.tabs.setCurrentIndex(4)
        
    def read_process(self):

        self.output = str(self.process.readAll())       
            
        if self.command == 'backtrace\n':
            self.txtbacktrace.setPlainText(self.output)
        else:
            if 'list' in self.command:                
                if 'out of range' not in self.output and 'Line number' not in self.output and self.output.find('(gdb)') != 0:
                    self.txtsource.append(self.output[:self.output.find('\n(gdb)')])
                    highlight = syntaxcpp.CPPHighlighter(self.txtsource.document())
                    self.command = 'list\n'
                    self.process.write(self.command)
            else:
                if 'info line ' in self.command and '\n'in self.command:
                    if self.info_line == 1:
                        self.address_line.append(re.findall(r'0x\w+',self.output)[0])
                        self.address_line.append([])
                    if 'out of range' not in self.output and 'Line number' not in self.output:
                        self.address_line[1] = re.findall(r'0x\w+',self.output)[0]
                        self.info_line += 1
                        self.command = 'info line ' +str(self.info_line) + '\n'
                        self.process.write(self.command)
                    else:
                        self.command = 'disas ' + self.address_line[0] + ', ' + self.address_line[1] + '\n'
                        self.process.write(self.command)
                else:                    
                    if 'disas ' in self.command:
                        self.txtassembly.setPlainText(self.output)
                    else:
                        if 'frame ' in self.command:
                            for search_iter in re.finditer(r'0x\w+',self.output):                                
                                frame_address = search_iter.group()                                
                                if frame_address.find('0x00000000') ==-1:
                                    frame_index = self.output[self.output.find('#')+1:self.output.find(' ')]
                                    frame_index = frame_index.rstrip()
                                    func_name = ''
                                    for search_iter in re.finditer(r'\bin+.+at\b',self.output):
                                        func_name = search_iter.group()
                                        arguments = func_name[func_name.find('('):func_name.find(')')+1]
                                        func_name = func_name[func_name.find('in ')+len('in '):func_name.find(' (')]
                                    
                                    if func_name == '':
                                        func_name = self.output[self.output.find(' '):self.output.find(')')+1]
                                        arguments = func_name[func_name.find('('):func_name.find(')')+1]
                                        func_name = func_name[func_name.find(' ') +1: func_name.find('(')]
                                    
                                    location = re.findall(r'/+.+[0-9]*',self.output)[0]
                                    self.tablestack.setRowCount(self.frame_count+1)
                                    self.tablestack_itemarray=[]
                                    for i in range(5):
                                        self.tablestack_itemarray.append(QtGui.QTableWidgetItem(0))
                                        self.tablestack.setItem(self.frame_count,i,self.tablestack_itemarray[i])
                                    self.tablestack_itemarray[0].setText(frame_index)
                                    self.tablestack_itemarray[1].setText(func_name)
                                    self.tablestack_itemarray[2].setText(arguments)
                                    self.tablestack_itemarray[3].setText(location)
                                    self.tablestack_itemarray[4].setText(frame_address)
                                    self.frame_count +=1
                                    self.command =  'frame ' + str(self.frame_count) +'\n'
                                    self.process.write(self.command)
                                    self.direct_to_terminal = False
                                else:                                
                                    self.command = ''
                        else:
                            if self.command == 'info all-registers\n':
                                self.txtregister.setPlainText(self.output)
                            else:                                
                                if self.direct_to_terminal == True and 'Breakpoint' not in self.output:                
                                    self.terminal_win.set_output_text(self.output)
                                else:
                                    self.direct_to_terminal = False
                                    self.txtoutput.append(self.output)        
            
        if 'Inferior' in self.output and 'exited' in self.output:
            self.direct_to_terminal = False
            
        if 'SIGSEGV' in self.output:
            msg_box = QtGui.QMessageBox.information(self,"AthenaDB","Program recieved SIGSEGV",QtGui.QMessageBox.Ok)
            self.statusbar.showMessage("Program recieved signal SISEGV and exited")
            self.txtoutput.append(self.output)
        
        if "Make breakpoint pending on future shared library load" in self.output:
                self.process.write('n\n')
                msg_box = QtGui.QMessageBox.information(self,"AthenaDB","Cannot create the breakpoint",QtGui.QMessageBox.Ok)                
        else:                
            if 'break' in self.command and 'delete' not in self.command and 'info' not in self.command:
                self.tablebreakpoints.setRowCount(len(self.breakpoints_array)+1)
                self.tablebreakpoints_itemarray = []
                self.breakpoints_count +=1                    
                for i in range(6):
                    self.tablebreakpoints_itemarray.append(QtGui.QTableWidgetItem(0))
                    self.tablebreakpoints.setItem(len(self.breakpoints_array),i,self.tablebreakpoints_itemarray[i])
                if 'line:' not in self.command:
                    self.tablebreakpoints_itemarray[4].setText(self.breakpoint_at)
                self.tablebreakpoints_itemarray[0].setFlags(QtCore.Qt.ItemIsUserCheckable)
                self.tablebreakpoints_itemarray[0].setCheckState(QtCore.Qt.Checked)
                self.tablebreakpoints_itemarray[1].setText(str(self.breakpoints_count))
                self.tablebreakpoints_itemarray[2].setText(self.output[self.output.find('file ')+len('file '):self.output.find(',',self.output.find('file'))])
                self.tablebreakpoints_itemarray[3].setText(self.output[self.output.find('line ')+len('line '):self.output.find('.',self.output.find('line'))])
                self.command = 'info break ' + str(self.breakpoints_count) + '\n'
                self.process.write(self.command)
                self.breakpoints_array.append(self.breakpoints_count) 
            else:
                if 'info break ' in self.command:                    
                    func = self.output[self.output.find('in ')+3:self.output.find(' at')]                    
                    self.tablebreakpoints_itemarray[4].setText(func)
                    address = re.findall(r'0x\w+',self.output)[0]
                    self.tablebreakpoints_itemarray[5].setText(address)

        if 'jump' in self.command:            
            if 'Jump anyway' in self.output:
                self.process.write('y\n')

        if 'print ' in self.command:
            if 'No symbol ' not in self.output:
                value = self.output[self.output.find('= ')+len('= '):]
                msg_box = QtGui.QMessageBox.information(self,'Variable Value','Value of ' + self.command[self.command.find('t ')+2:] + ' is ' + str(value),QtGui.QMessageBox.Ok)
            else:
                msg_box = QtGui.QMessageBox.information(self,'Variable Value','Cannot find specified variable',QtGui.QMessageBox.Ok)

        if '(no debugging symbols found)' in self.output:
            msg_box = QtGui.QMessageBox.information(self,'','No debugging symbols found by gdb, please recompile code with gcc using -g flag',QtGui.QMessageBox.Ok)
            
    def func_run_stopprocess(self):

        self.command = 'stop\n'
        self.process.write(self.command)
        self.process.write('y\n')
        self.statusbar.showMessage('Inferior Process killed')
        self.run_runprocess.setEnabled(True)
        self.run_stopprocess.setEnabled(False)
        
    def finished_process(self):

        msg_box = QtGui.QMessageBox("gdb exited")
        msg_box.exec_()

    def func_run_continue(self):

        self.command = 'cont\n'
        self.direct_to_terminal = True
        self.process.write(self.command)        
        
    def func_run_restartprocess(self):

        f = open('/media/sda6/Python/gdbfile','w')
        f.write('')
        f.close()
        self.command = 'run '+self.arguments + '\n'
        self.process.write(self.command)
        self.process.write('y\n')
        
    def func_run_process(self):

        if self.working_directory !='':
            self.process.write('cd ' + self.working_directory +'\n')
            
        self.command = 'run '+self.arguments+'\n'
        self.process.write(self.command)
        self.terminal_win = terminal_file.terminal(self)
        self.terminal_win.show()
        self.direct_to_terminal = True
        self.statusbar.showMessage("Running " + self.exec_file)
        
        self.run_runprocess.setEnabled(False)
        self.run_restartprocess.setEnabled(True)
        self.run_continue.setEnabled(True)        
        self.run_stopprocess.setEnabled(True)
        
        self.debug_jump.setEnabled(True)
        self.debug_next.setEnabled(True)
        self.debug_step.setEnabled(True)
        self.debug_finish.setEnabled(True)
        self.call_function.setEnabled(True)
        self.print_value.setEnabled(True)

        self.backtrace_show.setEnabled(True)
        self.list_source.setEnabled(True)
        self.disassembly.setEnabled(True)
        self.stack.setEnabled(True)
        self.registers.setEnabled(True)
        
    def func_finish(self):

        self.command = 'finish\n'
        self.process.write(self.command)

    def func_jump(self):

        self.jump_win = jump_win_file.jump_win(self)
        self.connect(self.jump_win,QtCore.SIGNAL('jump()'),self.jump_location)
        self.jump_win.show()

    def jump_location(self):

        if self.jump_win.radio_func.isChecked() == True:
            self.jump_at = str(self.jump_win.txtfunc.text())                
            self.command = 'jump ' + self.jump_at + '\n'
            
        if self.jump_win.radio_line.isChecked() == True:
            self.jump_at = 'jump ' + str(self.jump_win.txtfile.text()) + ': ' + str(self.jump_win.txtline.text())            
            self.command = self.jump_at + '\n'

        if self.jump_win.radio_address.isChecked() == True:
            self.jump_at = 'jump *' + str(self.jump_win.txtaddress.toPlainText())
            self.command = self.jump_at + '\n'
        
        self.process.write(self.command)        
    
    def func_step(self):

        self.command = 'step\n'
        self.process.write(self.command)
        
    def func_next(self):

        self.command = 'next\n'
        self.process.write(self.command)
        
    def set_process_values(self):

        self.exec_file = str(self.load_exec_win.txt_executable_path.text())
        self.arguments = str(self.load_exec_win.txt_arguments_path.text())
        self.working_directory = str(self.load_exec_win.txt_working_directory_path.text())        
        self.process.start('gdb',[self.exec_file])
        self.output = ''        
        self.connect(self.process,QtCore.SIGNAL('readyRead()'),self.read_process)
        self.connect(self.process,QtCore.SIGNAL('finished()'),self.finished_process)
        
        self.statusbar.showMessage('File ' + self.exec_file + 'Loaded')        
        self.breakpoints_create.setEnabled(True)
        self.run_runprocess.setEnabled(True)
        self.list_source.setEnabled(True)
        self.disassembly.setEnabled(True)        
        self.registers.setEnabled(True)

    def run_gdb_gui(self,exec_file,arguments,working_directory):

        if exec_file != '':            
            self.exec_file = exec_file
            self.arguments = arguments
            self.working_directory = working_directory
            self.process.start('gdb',[self.exec_file])
            self.output = ''        
            self.connect(self.process,QtCore.SIGNAL('readyRead()'),self.read_process)
            self.connect(self.process,QtCore.SIGNAL('finished()'),self.finished_process)
            
            self.statusbar.showMessage('File ' + self.exec_file + 'Loaded')        
            self.breakpoints_create.setEnabled(True)
            self.run_runprocess.setEnabled(True)
            self.list_source.setEnabled(True)
            self.disassembly.setEnabled(True)
            self.registers.setEnabled(True)
        
    def func_openexecutable(self):

        self.load_exec_win = loadexecutable.load_executable_window(self)
        self.load_exec_win.show()
        self.connect(self.load_exec_win,QtCore.SIGNAL('run_gdb()'),self.set_process_values)
        
    def funcexit(self):

        self.close()

    def set_breakpoint(self):
        
        if self.create_breakpoints_win.radio_func.isChecked() == True:
            self.breakpoint_at = str(self.create_breakpoints_win.txtfunc.text())                
            self.command = 'break ' + self.breakpoint_at + '\n'
            
        if self.create_breakpoints_win.radio_line.isChecked() == True:
            self.breakpoint_at = 'break ' + str(self.create_breakpoints_win.txtfile.text()) + ': ' + str(self.create_breakpoints_win.txtline.text())            
            self.command = self.breakpoint_at + '\n'

        if self.create_breakpoints_win.radio_address.isChecked() == True:
            self.breakpoint_at = 'break *' + str(self.create_breakpoints_win.txtaddress.toPlainText())
            self.command = self.breakpoint_at + '\n'
            
        self.breakpoints_enable.setEnabled(True)
        self.breakpoints_enableall.setEnabled(True)
        self.breakpoints_disable.setEnabled(True)
        self.breakpoints_disableall.setEnabled(True)
        self.breakpoints_remove.setEnabled(True)
        self.breakpoints_removeall.setEnabled(True)
        
        self.process.write(self.command)
        
    def func_createbreakpoints(self):

        self.create_breakpoints_win = breakpoints.create_breakpoints(self)
        self.create_breakpoints_win.show()
        self.connect(self.create_breakpoints_win,QtCore.SIGNAL('setbreakpoint()'),self.set_breakpoint)
        
    def func_disablebreakpoints(self):

        row = self.tablebreakpoints.currentRow()
        item = self.tablebreakpoints.item(row,0)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
            self.command = 'disable ' + str(self.breakpoints_array[row])
            self.process.write(self.command + '\n')
        
    def func_disableallbreakpoints(self):

        for i in range(self.tablebreakpoints.rowCount()):            
            item = self.tablebreakpoints.item(i,0)
            item.setCheckState(QtCore.Qt.Unchecked)
        self.command = 'disable'
        self.process.write(self.command + '\n')

    def func_enablebreakpoints(self):

        row = self.tablebreakpoints.currentRow()
        item = self.tablebreakpoints.item(row,0)
        if item.checkState() == QtCore.Qt.Unchecked:            
            item.setCheckState(QtCore.Qt.Checked)
            self.command = 'enable ' + str(self.breakpoints_array[row])
            self.process.write(self.command + '\n')
        
    def func_enableallbreakpoints(self):

        for i in range(self.tablebreakpoints.rowCount()):            
            item = self.tablebreakpoints.item(i,0)
            item.setCheckState(QtCore.Qt.Unchecked)
        self.command = 'enable'
        self.process.write(self.command + '\n')
        
    def func_removebreakpoints(self):

        break_point = self.breakpoints_array[self.tablebreakpoints.currentRow()]
        del self.breakpoints_array[self.tablebreakpoints.currentRow()]
        self.command = 'delete break ' + str(break_point)        
        self.tablebreakpoints.removeRow(self.tablebreakpoints.currentRow())
        self.process.write(self.command + '\n')

    def func_removeallbreakpoints(self):

        for i in range(len(self.breakpoints_array)):
            break_point = self.breakpoints_array[i]
            self.command = 'delete break ' + str(break_point)
            self.process.write(self.command + '\n')
            self.tablebreakpoints.removeRow(0)
        self.breakpoints_array=[]
        
    def func_showbreakpoints(self):

        self.tabs.setCurrentIndex(2) 

    def func_showbacktrace(self):

        self.command = 'backtrace\n'
        self.process.write(self.command)
        self.tabs.setCurrentIndex(1)        
