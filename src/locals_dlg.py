from PyQt4 import QtCore, QtGui

class LocalVarsDialog(QtGui.QDialog):
    
    def __init__(self, parent=None):

        QtGui.QDialog.__init__(self,parent)
        self.resize(565, 300)
        self.treeWidget = QtGui.QTreeWidget(self)
        self.treeWidget.setGeometry(QtCore.QRect(2, 3, 561, 291))

        self.treeWidget.setColumnCount(2)
        self.treeWidget.setHeaderLabels(['Name','Value'])        
        self.exp_type=""
        self.exp_value=""
        self.struct_inspected=False
        self.treeWidgetItemList=[]

    def get_full_string(self,string):

        s = ''
        for d in string.split('}'):
            s+=d +'}'
            if s.count('{')==s.count('}'):
                break
        return s

    def setExpressions(self,string,parent=None):

        string = str(string)
        while string != '':
            full_string = self.get_full_string(string)
            string = string.replace(full_string,'')
            full_string = full_string[full_string.find('{')+1:full_string.rfind('}')]
            if full_string.find('name')!=-1 and full_string.find('value')!=-1:                
                exp_name = full_string[full_string.find('name="')+len('name="'):full_string.find('"',full_string.find('name="')+len('name="')+1)]
                exp_val = full_string[full_string.find('value="')+len('value="'):full_string.find('"',full_string.find('value="')+len('value="')+1)]
            else:
                exp_name = full_string[:full_string.find('=')]
                exp_val = full_string[full_string.find('=')+1:]
                
            string = string.strip()

            if parent == None:
                parent = QtGui.QTreeWidgetItem(self.treeWidget)
            else:
                parent = QtGui.QTreeWidgetItem(self.treeWidget,parent)           

            if exp_val.find('{')==0:
                exp_val = exp_val.replace('{','',1)
            if exp_val.rfind('}')==len(exp_val)-1:
                exp_val = exp_val[:len(exp_val)-1]
            
            self.treeWidgetItemList.append(parent)
            parent.setText(0,exp_name)
            parent.setText(1,exp_val)
