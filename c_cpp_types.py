import re
global list_primitive_types

def isThisAFunction(string):

    if '+' in string or '-' in string or '/' in string:
        return False
    
    args_correct=True
    for arg in string[string.find('('):string.rfind(')')].split(','):
        if arg.find(' ')==-1:
            args_correct  = False
            return False

class character(object):

    def __init__(self):

        self.name = 'char'
    
class double(object):

    def __init__(self):

        self.name='double'

class integer(object):

    def __init__(self):

        self.name='int'


class floating_number(object):

    def __init__(self):

        self.name='float'


class void(object):

    def __init__(self):

        self.name='void'

list_primitive_types = [character(),double(),integer(),floating_number(),void()]

class CVariable(object):

    def __init__(self,var_name="",var_type=""):

        self.name=var_name
        self.type = var_type
        self.return_type=""
        self.var_type="Variable"
        self.isPointer = False
        self.isReference = False
        self.isObject = False
        
    def createFromDeclaration(self,declaration):

        declaration = declaration.replace(';','')
        if declaration.find('=')!=-1:
            declaration = declaration[:declaration.find('=')]
        if declaration.find('(')!=-1:
            declaration = declaration[:declaration.find('(')]
        if declaration.find(')')!=-1:
            declaration = declaration[:declaration.find(')')]
        if '*' in declaration:
            self.isPointer = True
        elif '&' in declaration:
            self.isReference = True
        else:
            self.isObject=True
        if declaration.find('[')!=-1:
            declaration = declaration[:declaration.find('[')]
        declaration = declaration.strip()
        declaration = declaration.replace('*','')
        self.type = declaration[:declaration.rfind(' ')]
        self.name = declaration[declaration.find(self.type)+len(self.type):]
        self.type = self.type.strip()
        self.name = self.name.strip()

    def getDeclaration(self):
        
        if self.isPointer == True:
            return self.type + '* ' + self.name
        if self.isReference == True:
            return self.type + '& ' + self.name
        if self.isObject == True:
            return self.type + ' ' + self.name
    
class CFunction(object):

    def __init__(self,name="",return_type=""):

        self.name=name
        self.return_type=return_type
        self.list_params=[]
        self.pos = -1
        self.type = ""
        self.var_type="Function"
        
    def createFromDeclaration(self,declaration):

        declaration = declaration.replace(';','')
        declaration = declaration.replace('{','')
        self.name = declaration[:declaration.rfind('(')]
        self.name = self.name.strip()
        self.return_type = self.name[:self.name.rfind(' ')]
        self.name = self.name[self.name.find(self.return_type)+len(self.return_type):]
        self.name = self.name.strip()
        self.return_type = self.return_type.strip()

        declaration = declaration[declaration.rfind('(')+1:]
        for args in declaration.split(','):
            args = args.replace('(','')
            args = args.strip()
            param = CVariable()
            param.createFromDeclaration(args)
            self.list_params.append(param)        
        
    def getDeclaration(self):

        dec = '('
        for param in self.list_params:
            dec += param.getDeclaration() + ','
        if dec[len(dec)-1]==',':
            dec = dec[:len(dec)-1]
        dec+=')'
        dec = self.return_type + ' ' +self.name+dec
        return dec
    
    def isEqualTo(self,func):

        if self.name == func.name:
            if self.return_type == func.return_type:
                if len(self.list_params)==len(func.list_params):
                    for param in func.list_params:
                        if param not in self.list_params:
                            return False
                    return True
        return False

class CStruct(object):

    def __init__(self):

        self.name = None
        self.list_members = []
        self.list_typedef = []

    def createFromDeclaration(self,declaration):

        s = re.findall(r'.+?{',declaration,re.DOTALL)
        s = s[0]
        self.name = re.findall(r'\bstruct\b\s*\w+',s)[0]
        self.name = self.name.replace('struct','')
        self.name = self.name.strip()
        declaration = declaration.replace(s,'')
        for search_iter in re.finditer(r'\s+(.+\w+.+)\s*?\;',declaration):
            d = search_iter.group()
                
            if "(" not in d and ")" not in d:
                if ',' not in d:
                    var = CVariable()
                    var.createFromDeclaration(d)
                    self.list_members.append(var)
                else:
                    d_split  = d.split(',')
                    var = CVariable()
                    var.createFromDeclaration(d_split[0])
                    self.addAccToScope(var,search_iter.end())
                    for g in d_split[1:]:
                        _var = CVariable()
                        _var.createFromDeclaration(var.type+' '+ g)
                        self.list_members.append(_var)

    def getDeclaration(self):

        return 'struct ' + self.name

    def getFullPublicList(self):

        return [member.getDeclaration() for member in self.list_members]
class CObject(CVariable):

    def __init__(self):

        CVariable.__init__(self)
        self.class_type = None
        self.scope = None

class CTypedef(object):

    def __init__(self):

        self.name = None
        self.typedef_with = None
        self.typedef_with_name  = ""
        
    def createFromDeclaration(self,dec):

        self.name = dec[dec.rfind(' '):]
        self.name = self.name.strip()
        dec = dec.replace('typedef','')
        self.typedef_with_name = dec.strip()
        
class CPPClass(object):

    def __init__(self):

        self.name = None
        self.is_template=False
        self.template=None
        self.list_public_members = []
        self.list_private_members = []
        self.list_protected_members = []
        self.list_nested_class_structs = []
        self.list_public_base_classes = []
        self.list_private_base_classes = []
        self.list_public_base_classes_name = []
        self.list_private_base_classes_name = []
        self.list_child_classes = []
        
    def createFromDeclaration(self,declaration):

        #print 'lll' ,declaration,'kk;'
        s = re.findall(r'.+?{',declaration,re.DOTALL)
        s = s[0]
        declaration = declaration.replace(s,'')
        template = re.findall(r'\btemplate\s*<class\s+\w+\s*>',s)
        #print 'template is ',template,'thats it'
        if template!=[]:            
            template = template[0]            
            self.is_template = True
            self.template = template[template.find('class')+len('class'):template.find('>')]
            self.template = self.template.strip()            
            s = s.replace(template,'')
        d = re.findall(r'\bclass\b\s*\w+',s)[0]
        self.name = d[d.find('class')+len('class'):]
        self.name = self.name.strip()
        s = s.replace(d,'')
        if s.find(':')!=-1:
            for q in s.split(','):
                q = q.strip()
                if q.find('public ')!=-1:
                    public_base_class = q[q.find('public ')+len('public '):]
                    public_base_class = public_base_class.strip()
                    self.list_public_base_classes_name.append(public_base_class)
                if q.find('private ')!=-1:
                    private_base_class = q[q.find('private ')+len('private '):]
                    private_base_class = private_base_class.strip()
                    self.list_private_base_classes_name.append(public_base_class)
        #print 'declaration i', declaration,'iiii'
        declaration = declaration.replace(s,'')
        #print 's is ',s,'lllll'        
        declaration = 'private:\n' + declaration

        self.list_private =[]
        self.list_public =[]
        self.list_protected =[]
        
        index = declaration.find('private:')
        while(index!=-1):
            self.list_private.append(index)
            index = declaration.find('private:',index+1)

        index = declaration.find('public:')
        while(index!=-1):
            self.list_public.append(index)
            index = declaration.find('public:',index+1)

        index = declaration.find('protected:')
        while(index!=-1):
            self.list_protected.append(index)
            index = declaration.find('protected:',index+1)

        #print 'before finding cpp_reg_array declaration is',declaration,'thats it'
        ###Finding nested classes and enums and structs
        for _type in ["class","enum","struct"]:            
            cpp_reg_array = re.findall(r'[\btemplate\s*<class\s+\w+\s*>]*\b%s\b\s*\w+.+?\}\s*\;'%_type,declaration,re.DOTALL)

            if cpp_reg_array!=[]:
                for class_definition in cpp_reg_array:
                    if class_definition.count('{')>class_definition.count('}'):
                        regex_array = re.findall(r'(?<=\}\;)\s*\w+.+?(?=\}\;)',declaration,re.DOTALL)
                        count = class_definition.count('{')-class_definition.count('}')
                        i=0
                        while count>0 and i<len(regex_array):
                           class_definition += regex_array[i] + '};'
                           count = class_definition.count('{')-class_definition.count('}')
                    if _type=="class" or _type=="struct":
                        nested = CPPClass()
                        nested.createFromDeclaration(class_definition)
                        self.list_nested_class_structs.append(nested)
                    elif _type=="enum":
                        enum = CEnum()
                        class_def = class_definition.replace('enum','')
                        class_def = class_def.replace('{','')
                        enum.createFromDeclaration(class_definition)
                    
                    declaration = declaration.replace(class_definition,'')

        ###Finding inline functions
        for search_iter in re.finditer(r'\s*(\w+.+)\s*\{',declaration):
            inline_func_dec = search_iter.group()
            inline_func = search_iter.group()
            bracket_array=[j.start() for j in re.finditer(r'\}',declaration)]
            for i,pos in enumerate(bracket_array):                
                    inline_func += declaration[declaration.find(inline_func)+len(inline_func):bracket_array[i]+1]
                    if inline_func.count('{')==inline_func.count('}'):
                        declaration = declaration.replace(inline_func,'')
                        scope = self.memberScope(pos)
                        func = CFunction()
                        func.createFromDeclaration(inline_func_dec)
                        if scope == "private":
                            self.list_private_members.append(func)
                        elif scope == "public":
                            self.list_public_members.append(func)
                        elif scope == "protected":
                            self.list_protected_members.append(func)

                        bracket_array = bracket_array[i+1:]
                        break

        ###Finding other members        
        for search_iter in re.finditer(r'\s+(.+\w+.+)\s*?\;',declaration):
            d = search_iter.group()
            
            if d.find('=')!=-1:
                d = d[:d.find('=')]
                
            if "(" in d and ")" in d:

                func = CFunction()
                func.createFromDeclaration(d)
                self.addAccToScope(func,search_iter.end())
                
            if "(" not in d and ")" not in d:
                if ',' not in d:

                    var = CVariable()
                    var.createFromDeclaration(d)
                    self.addAccToScope(var,search_iter.end())
                else:
                    d_split  = d.split(',')
                    var = CVariable()
                    var.createFromDeclaration(d_split[0])
                    self.addAccToScope(var,search_iter.end())
                    for g in d_split[1:]:
                        _var = CVariable()
                        _var.createFromDeclaration(var.type+' '+ g)
                        self.addAccToScope(_var,search_iter.end())

    def addAccToScope(self,member,pos):

        scope = self.memberScope(pos)
        if scope=="private":
            self.list_private_members.append(member)
        elif scope=="public":
            self.list_public_members.append(member)
        elif scope=="protected":
            self.list_protected_members.append(member)
            
    def memberScope(self,pos):

        min_diff = pos - self.list_private[0]
        scope="private"
        for i in self.list_private:
            if pos-i > 0 and (pos-i)<min_diff:
                min_diff = pos-i
                scope="private"
                
        for i in self.list_public:
            if pos-i > 0 and(pos-i)<min_diff:
                min_diff = pos-i
                scope="public"
                
        for i in self.list_protected:
            if pos-i > 0 and (pos-i)<min_diff:
                min_diff = pos-i
                scope="protected"

        return scope

    def getDeclaration(self):

        if self.is_template == True:
            return 'template<class '+self.template +'>class ' + self.name
        else:
            return 'class ' + self.name

    def getFullPublicList(self):

        list_public_members = [_class.getDeclaration() for _class in self.list_nested_class_structs]
        list_public_members += [member.getDeclaration() for member in self.list_public_members]
        
        for _class in self.list_public_base_classes:
            list_public_members += [_class.getDeclaration() for _class in self.list_nested_class_structs()]
            list_public_members += [member.getDeclaration() for member in _class.list_public_members]
        
        return list_public_members

    def getFullList(self):

        list_public_members = [_class.getDeclaration() for _class in self.list_nested_class_structs]
        list_public_members += [member.getDeclaration() for member in self.list_public_members+self.list_private_members+self.list_protected_members]
        for _class in self.list_public_base_classes:
            list_public_members += [_class.getDeclaration() for _class in self.list_nested_class_structs]
            list_public_members += [member.getDeclaration() for member in _class.list_public_members+self.list_private_members+self.list_protected_members]

        return list_public_members
    
class CEnum(object):

    def __init__(self):

        self.list_members=[]

    def createFromDeclaration(self,dec):

        for member in re.findall(r'.+',dec):

            member = member[:member.find('=')]
            member = member.strip()
            self.list_members.append(member)

class CPPObject(CVariable):

    def __init__(self):

        CVariable.__init__(self)
        self.class_type = None
        self.scope = None
