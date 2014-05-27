from PyQt4 import QtGui,QtCore
import os
from breakpoints import *
import helper_functions

class BreakpointsBar(QtGui.QWidget):

    def __init__(self, parent= None, *args):
        
        QtGui.QWidget.__init__(self, parent,*args)
        self.edit = None
        self.parent = parent
        self.first_line = 0
        self.highest_line=0
        self.acceptBreakpoints = True
        self.showing_breakpoints = False
        self.breakpoint_enable_image=QtGui.QImage(os.path.join (helper_functions.getRootDir (), "icons/breakpoint-enable1.png"))
        self.breakpoint_disable_image=QtGui.QImage(os.path.join (helper_functions.getRootDir (), "icons/breakpoint-disable1.png"))
        self.arrow_image = QtGui.QImage(os.path.join (helper_functions.getRootDir (), "icons/arrow.png"))
            
    def setTextEdit(self, edit):
        
        self.edit = edit
        
    def mouseReleaseEvent(self, mouse_event):           

        if self.acceptBreakpoints==False:
            QtGui.QWidget.mouseReleaseEvent(self,mouse_event)
            return
        
        line = -1
        for i in range(len(self.list_draw_text_y)-1,-1,-1):

            if mouse_event.y() >= self.list_draw_text_y[i][0]-self.fontMetrics().ascent():
                line = self.list_draw_text_y[i][1]
                break            
        print line
        if line!=-1:
            found = False
            breakpoint = LineBreakpoint(0,0,"")
            for breakpoint in self.parent.list_breakpoints:
                if int(breakpoint.line)==line:
                    found = True
                    break
            if found==True:
                if breakpoint.state == BREAKPOINT_STATE_DISABLED:
                    breakpoint.state = BREAKPOINT_STATE_ENABLED
                else:
                    breakpoint.state = BREAKPOINT_STATE_DISABLED
                self.parent.breakpointChange(breakpoint)
            else:
                self.parent.list_breakpoints.append(LineBreakpoint(BREAKPOINT_STATE_ENABLED,line,self.parent.filename)) 
                self.parent.sendSetBreakpointSignal(line)
            self.repaint()
            
        QtGui.QWidget.mouseReleaseEvent(self,mouse_event)
        
    def update(self, *args):

        if self.parent.drawLinePointer==True:
            width = 22
        else:
            width = 20
            
        if self.width() != width:
            self.setFixedWidth(width)
        
        QtGui.QWidget.update(self, *args)

    def paintEvent(self, event):
        
        contents_y = self.edit.verticalScrollBar().value()
        page_bottom = contents_y + self.edit.viewport().height()
        font_metrics = self.fontMetrics()
        current_block = self.edit.document().findBlock(self.edit.textCursor().position())
        block_count = self.edit.document().blockCount()            
        painter = QtGui.QPainter(self)

        block = current_block
        line_count_prev = block.blockNumber()+1            
        self.list_draw_text_y = []

        self.showing_breakpoints = False
        
        while block.isValid():               
            
            position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()
            if position.y() < contents_y:
                break                
            block = block.previous()               
            
        if not block.isValid():
            block = self.edit.document().findBlock(0)
            
        line_count_next = block.blockNumber()
        self.first_line= line_count_next
        count = 0            
        
        begining_block= block
        position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()            
        
        while block.isValid() and position.y() <= page_bottom:                
            line_count_next += 1                
            position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()
            
            if position.y() >= contents_y and position.y() <=page_bottom:
                self.list_draw_text_y.append((round(position.y()) - contents_y + font_metrics.ascent(),line_count_next))

            found = False
            breakpoint = LineBreakpoint(0,0,"")
            for breakpoint in self.parent.list_breakpoints:                    
                if int(breakpoint.line)==line_count_next:
                    found = True
                    break
            
            if found==True:
                
                if breakpoint.state == BREAKPOINT_STATE_ENABLED:                        
                    point = QtCore.QPoint(0,round(position.y())-contents_y+2)
                    rect = QtCore.QRect(0,0,17,17)
                    painter.drawImage(point,self.breakpoint_enable_image,rect)
                    self.showing_breakpoints = True
                    
                if breakpoint.state == BREAKPOINT_STATE_DISABLED:
                    point = QtCore.QPoint(0,round(position.y())-contents_y+2)
                    rect = QtCore.QRect(0,0,17,17)
                    painter.drawImage(point,self.breakpoint_disable_image,rect)
                    self.showing_breakpoints = True
                    
            if self.parent.drawLinePointer==True:

                if self.parent.linePointer==line_count_next:
                    point = QtCore.QPoint(0,round(position.y())-contents_y)
                    rect = QtCore.QRect(0,0,22,22)
                    painter.drawImage(point,self.arrow_image,rect)
                    self.showing_breakpoints = True
                    
            block = block.next()
            
        self.highest_line = line_count_next
        painter.end()
        QtGui.QWidget.paintEvent(self, event)
