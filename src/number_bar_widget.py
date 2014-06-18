from PyQt4 import QtGui,QtCore
import time,random

class CodeRect(object):

    def __init__(self,x1,y1,x2,y2,start_pos,end_pos):

        self.x1=x1
        self.y1 = y1
        self.x2=x2
        self.y2=y2
        self.start_pos = start_pos
        self.end_pos = end_pos
        super(CodeRect,self).__init__()

    def is_point_inside(self,x,y):

        if x > self.x1 and x < self.x2:
            if y > self.y1 and y < self.y2:
                return True
        return False
    
class NumberBar(QtGui.QWidget):
 
    def __init__(self, parent= None, *args):
        
        QtGui.QWidget.__init__(self, parent,*args)
        self.edit = None            
        self.highest_line = 0
        self.rect_array = []
        self.parent = parent
        self.first_color = QtGui.QColor(0,0,0)
        
    def setTextEdit(self, edit):
        
        self.edit = edit
        
    def mouseReleaseEvent(self, mouse_event):

        inside_rect_array=[]
        
        for i,x in enumerate(self.rect_array):                                
            if x.is_point_inside(mouse_event.x(),mouse_event.y())==True:
                inside_rect_array.append(x)

        if inside_rect_array!=[]:
            
            smallest_one = inside_rect_array[0]
            min_height=inside_rect_array[0].y2-inside_rect_array[0].y1
            for i,x in enumerate(inside_rect_array):
                if min_height > x.y2-x.y1:
                    #print min_height
                    min_height=x.y2-x.y1
                    smallest_one = x
        
            self.edit.setTextVisible(smallest_one.start_pos,smallest_one.end_pos)
            
        QtGui.QWidget.mouseReleaseEvent(self,mouse_event)
        
    def update(self, *args):
        
        width = self.fontMetrics().width(str(self.highest_line)) + 7
        if self.width() != width:
            self.setFixedWidth(width)
        QtGui.QWidget.update(self, *args)

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        s = self.style()
        painter = QtGui.QPainter(self)
        s.drawPrimitive (QtGui.QStyle.PE_Widget, opt, painter, self)        
        contents_y = self.edit.verticalScrollBar().value()
        page_bottom = contents_y + self.edit.viewport().height()
        font_metrics = self.fontMetrics()
        current_block = self.edit.document().findBlock(self.edit.textCursorWithHiddenText().position())
        block_count = self.edit.document().blockCount()            

        block = current_block
        line_count_prev = block.blockNumber()+1            
            
        while block.isValid():               
            
            position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()                            
            if position.y() < contents_y:
                break                
            block = block.previous()               
            
        if not block.isValid():
            block = self.edit.document().findBlock(0)
            
        line_count_next = block.blockNumber()
        count = 0
        drawLine = False
        x1 = -1
        y1 = -1
        x2 = -1
        y2 = -1
        
        begining_block= block
        self.rect_array = []
        self.added_array=[]
        stack_point = []
        stack_begining_block=[]
        position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()
        last_used_color = self.first_color
        
        while block.isValid() and position.y() <= page_bottom:
            
            line_count_next += 1                
            position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()

            if position.y() >= contents_y and position.y() <=page_bottom:
                bold = False
                
                ##For updating line numbers
                for i,x in enumerate(self.parent.txtInput.hidden_text_array):
                    if block.position()>x.start_pos and i not in self.added_array:
                        self.added_array.append(i)
                        line_count_next += x.get_number_of_lines()
                #########################
                pen = painter.pen()
                pen.setColor(self.first_color)
                painter.setPen(pen)
                if block == current_block:
                    bold = True
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                painter.drawText(1, round(position.y()) - contents_y + font_metrics.ascent(), str(line_count_next))
                
                if bold:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)

                line = unicode(block.text(),'utf-8',errors='ignore')
                    
                count += line.count('{') - line.count('}')
                
                if count == 0:
                    last_used_color = self.first_color
                    
                if count <0:
                    
                    count = 0
                    last_used_color = self.first_color
                    block = block.next()
                    continue
                
                if line.find('{')!=-1:
                    if x2 != -1 and y2 !=-1:
                        pass
                        
                    #drawLine = True
                    stack_begining_block.append(block)
                    stack_point.append((0,round(position.y()) - contents_y)) # font_metrics.ascent()                                            
                
                if line.find('}')!=-1:                        
                    x2 = self.width()
                    y2 = round(position.y()) - contents_y + font_metrics.ascent()
                    pen = painter.pen()
                    pen.setWidth(2)                        
                    last_used_color = QtGui.QColor(random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))                        
                    pen.setColor(last_used_color)
                    painter.setPen(pen)                        

                    x1,y1 = stack_point.pop()
                    painter.drawLine(x1,y1,x2,y1)
                    painter.drawLine(x1,y1,x1,y2)
                    painter.drawLine(x1,y2,x2,y2)
                    begining_block = stack_begining_block.pop()
                    begining_text = str(begining_block.text())
                    self.rect_array.append(CodeRect(0,y1,x2,y2,begining_block.position()+begining_text.find('{')+1,block.position()))
                    
            block = block.next()
            
        while count > 0:
            x1,y1 = stack_point.pop()
            begining_block = stack_begining_block.pop()
            begining_text = str(begining_block.text())
            
            pen = painter.pen()
            pen.setWidth(2)
            painter.setPen(pen)        
            x2 = self.width()
            y2 = round(position.y()) - contents_y + font_metrics.ascent() 
            painter.drawLine(x1,y1,x2,y1)
            painter.drawLine(x1,y1,x1,y2)
            painter.drawLine(x1,y2,x2,y2)
            ##Here, remember the position of first character of block
            ##will be passed not 1+position of {
            self.rect_array.append(CodeRect(0,y1,x2,y2,begining_block.position(),-1)) 
            count -=1
            
        self.highest_line = line_count_next
        #painter.end()
        QtGui.QWidget.paintEvent(self, event)
