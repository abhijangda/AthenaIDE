from PyQt4 import QtGui,QtCore
import sip,sys,os,pty,time
import select,fcntl,termios

class ReadingThread(QtCore.QThread):

    def __init__(self,fd,parent=None):

        QtCore.QThread.__init__(self,parent)
        self.fd=fd
        self.parent=parent

    def run(self):

        while True:
            r,w,e = select.select([self.fd],[],[])
            s=''
            d='1'
            try:                
                while d != '':                
                    d = os.read(r[0],1)
                    s+=d
            except OSError:
                pass
            self.emit(QtCore.SIGNAL('readOutput(QString)'),QtCore.QString(s))        
      
