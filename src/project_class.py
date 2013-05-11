import os
from helper_functions import *

class env_var(object):

    def __init__(self,full_str):

        self.name = full_str[:full_str.find(" ")]
        self.val = full_str[full_str.find(" ")+1:]

    def to_string(self):

        return self.name + ' ' + self.val

    def get_key_val_pair(self):

        return self.name + '='+self.val
    
class project(object):

    def __init__(self,proj_name,proj_file,proj_type):

        self.proj_name = proj_name
        self.list_files=[]
        self.proj_file = proj_file
        self.proj_path = proj_file[:proj_file.rfind("/")]
        self.proj_type = proj_type
        self.proj_gtk_type = ''
        self.compile_only=False
        self.disable_inline=False
        self.define_symbols=False
        self.add_dir=False
        self.warning_as_errors=False
        self.support_c89=False
        self.compile_assemble=False
        self.optimize=False
        self.optimize_level=0
        self.other_args=""
        self.out_dir=self.proj_path+"/bin"
        if self.proj_path!="":
            try:
                os.mkdir(self.out_dir)
            except OSError:
                pass
            
        self.curr_dir=self.proj_path
        self.params=""
        self.run_on_ext_console=True
        self.list_dir=[]
        self.symbols=""
        self.list_env_var=""
        
    def clear_files(self):

        self.list_files=[]
        self.write_to_file()
        
    def append_file(self,filepath):

        self.list_files.append(filepath)
        self.write_to_file()

    def write_to_file(self):

        proj_str = self.get_proj_str()
        if self.proj_file=="":
            if self.proj_type=="C Project":
                self.proj_file = os.path.join(self.proj_path,self.proj_name+".cproj")
            elif self.proj_type=="C++ Project":
                self.proj_file = os.path.join(self.proj_path,self.proj_name+".cppproj")
        
        f = open(self.proj_file,'w')
        f.write(proj_str)
        f.close()

    def get_proj_str(self):

        proj_str=""
        proj_str = "<name>"+self.proj_name+"</name>\n"+"<type>"+self.proj_type+"</type>\n"
        print self.proj_gtk_type+" FFFFF"
        proj_str += '<proj_gtk_type>' + self.proj_gtk_type + '</proj_gtk_type>\n'
        proj_str += "<path>"+self.proj_path+"</path>\n"
        for _file in self.list_files:
            proj_str+="<file>"+_file+"</file>\n"
        
        proj_str+="<compile_only>" +str(self.compile_only)+"</compile_only>\n" 
        proj_str+="<disable_inline>"+str(self.disable_inline)+"</disable_inline>\n"
        proj_str+="<define_symbols>"+str(self.define_symbols)+"</define_symbols>\n"
        proj_str+="<symbols>"+self.symbols+"</symbols>\n"
        proj_str+="<add_dir>"+str(self.add_dir)+"</add_dir>\n"
        for _dir in self.list_dir:
            proj_str+="<dir>"+_dir+"</dir>\n"
                   
        proj_str+="<warning_as_errors>"+str(self.warning_as_errors)+"</warning_as_errors>\n"
        proj_str+="<support_c89>"+str(self.support_c89)+"</support_c89>\n"
        proj_str+="<compile_assemble>"+str(self.compile_assemble)+"</compile_assemble>\n"
        proj_str+="<optimize>"+str(self.optimize)+"</optimize>\n"
        proj_str+="<optimize_level>"+str(self.optimize_level)+"</optimize_level>\n"
        proj_str+="<run_on_ext_console>"+str(self.run_on_ext_console)+"</run_on_ext_console>\n"
        proj_str+="<out_dir>"+self.out_dir+"</out_dir>\n"
        proj_str+="<curr_dir>"+self.curr_dir+"</curr_dir>\n"
        proj_str+="<params>"+self.params+"</params>\n"    
        proj_str+="<other_args>"+self.other_args+"</other_args>\n"
        for env in self.list_env_var:
            proj_str+="<env>"+env.to_string()+"</env>\n"

        return proj_str

    def set_path(self,path):

        self.proj_path=path
        self.out_dir = path+"/bin"
        self.curr_dir = path

    def clear(self):

        self.proj_name = ""
        self.proj_gtk_type = ""
        self.list_files=[]
        self.proj_file = ""
        self.proj_path = ""
        self.proj_type=None
        self.compile_only=False
        self.disable_inline=False
        self.define_symbols=False
        self.add_dir=False
        self.warning_as_errors=False
        self.support_c89=False
        self.compile_assemble=False
        self.optimize=False
        self.optimize_level=0
        self.other_args=""
        self.out_dir=self.proj_path+"/bin"        
        self.curr_dir=self.proj_path
        self.params=""
        self.run_on_ext_console=True
        self.list_dir=[]
        self.symbols=""
        self.list_env_var=""

    def create_from_string(self,string):

        if self.proj_file!="":
            self.set_path(self.proj_file[:self.proj_file.rfind('/')])            
    
        pos_start = string.find("<name>")+6
        pos_end= string.find("</name>")    
        self.proj_name = string[pos_start:pos_end]        
        
        pos_start = string.find("<type>")+6
        pos_end = string.find("</type>")    
        self.proj_type = string[pos_start:pos_end]      

        pos_start = string.find ('<proj_gtk_type>') + len('<proj_gtk_type>')
        pos_end = string.find ('</proj_gtk_type>')
        self.proj_gtk_type = string [pos_start:pos_end]
        
        pos_start = string.find("<location>")+10
        pos_end=string.find("</location>")
        self.location  = string[pos_start:pos_end]       
        
        pos_start = 0
        pos_end = 0
        pos_start=string.find("<file>",pos_start+1)
        pos_end=string.find("</file>",pos_end+1)
        while  pos_start!=-1 and pos_end!=-1:
            self.list_files.append(string[pos_start+6:pos_end])
            pos_start=string.find("<file>",pos_start+1)
            pos_end=string.find("</file>",pos_end+1)
            
        pos_start = string.find("<run_on_ext_console>")+len ('<run_on_ext_console>')
        pos_end = string.find("</run_on_ext_console>")
        self.run_on_ext_console=str_to_bool(string[pos_start:pos_end])       
        
        pos_start = string.find("<optimize>")+10
        pos_end=string.find("</optimize>")
        self.optimize=str_to_bool(string[pos_start:pos_end])      
        
        if self.optimize==True:
            pos_start = string.find("<optimize_level>")+16
            pos_end=string.find("</optimize_level>")
            self.optimize_level=int(string[pos_start:pos_end])
            
        else:
            self.optimize_level=-1
        
        pos_start = string.find("<compile_assemble>")+18
        pos_end=string.find("</compile_assemble>")
        self.compile_assemble=str_to_bool(string[pos_start:pos_end])       
        
        pos_start = string.find("<support_c89>")+13
        pos_end=string.find("</support_c89>")
        self.support_c89=str_to_bool(string[pos_start:pos_end])       
        
        pos_start = string.find("<warning_as_errors>")+19
        pos_end=string.find("</warning_as_errors>")
        self.warning_as_errors=str_to_bool(string[pos_start:pos_end])
        
        pos_start = string.find("<add_dir>")+9
        pos_end=string.find("</add_dir>")
        self.add_dir=str_to_bool(string[pos_start:pos_end])
        
        if self.add_dir==True:
              
            pos_start = 0
            pos_end = 0
            pos_start=string.find("<dir>",pos_start+1)
            pos_end=string.find("</dir>",pos_end+1)
            while pos_start!=-1 and pos_end!=-1:                
                self.list_dir.append(string[pos_start+5:pos_end])
                pos_start=string.find("<dir>",pos_start+1)
                pos_end=string.find("</dir>",pos_end+1)

        pos_start = string.find("<define_symbols>")+16
        pos_end=string.find("</define_symbols>")
        self.define_symbols=str_to_bool(string[pos_start:pos_end])
        
        pos_start = string.find("<symbols>")+9
        pos_end=string.find("</symbols>")
        self.symbols=string[pos_start:pos_end]
        
        pos_start = string.find("<disable_inline>")+16
        pos_end=string.find("</disable_inline>")
        self.disable_inline=str_to_bool(string[pos_start:pos_end])
        
        pos_start = string.find("<compile_only>")+14
        pos_end=string.find("</compile_only>")
        self.compile_only=str_to_bool(string[pos_start:pos_end])
        
        pos_start = string.find("<params>")+8
        pos_end=string.find("</params>")    
        self.params=string[pos_start:pos_end]
        
        pos_start = string.find("<curr_dir>")+10
        pos_end=string.find("</curr_dir>")    
        self.curr_dir =string[pos_start:pos_end]      
        
        pos_start = string.find("<out_dir>")+9
        pos_end=string.find("</out_dir>")
        self.out_dir=string[pos_start:pos_end]       
        
        pos_start = string.find("<other_args>")+12
        pos_end=string.find("</other_args>")
        self.other_args=string[pos_start:pos_end]      
        
        pos_start = 0
        pos_end = 0
        pos_start=string.find("<env>",pos_start+1)
        pos_end=string.find("</env>",pos_end+1)
        while pos_start!=-1 and pos_end!=-1:
            self.list_env_var.append(env_var(string[pos_start+5,pos_end-5]))
            pos_start=string.find("<env>",pos_start+1)
            pos_end=string.find("</env>",pos_end+1)

    def get_compiler_command(self):

        command = ''
        if self.proj_type == 'C++ Project':
            command = 'g++ '
        else:
            command = 'gcc '

        command += '<input> -o <output> '
        command += self.other_args

        if self.compile_only==True:
            command += ' -S'
        if self.disable_inline==True:
            command += ' -fno-asm'
        if self.define_symbols==True:
            command += ' -D '+self.symbols
        if self.add_dir == True:
            command +=' -B'
            command += self.list_dir[0]
            for d in self.list_dir[1:]:
                command += ' '+ d
        if self.warning_as_errors==True:
            command += ' -Werror'
        if self.support_c89==True:
            command += ' -ansi'
        if self.compile_assemble==True:
            command += ' -c'
        if self.optimize==True:
            command += ' -O'+str(self.optimize_level)

        return command

    def get_compiler_flags(self):

        s = self.get_compiler_command()
        s = s.replace('<input> -o <output>','')        
        s = s.replace('gcc','')
        s = s.replace('g++','')
        s = s.replace(s[s.find('`pkg-config'):s.find('`')],'')
        return s
    
    def write(self):

        try:
            os.mkdir(self.proj_path)
        except OSError:
            pass

        self.write_to_file()
        try:
            os.mkdir(self.out_dir)
        except OSError:
            pass
