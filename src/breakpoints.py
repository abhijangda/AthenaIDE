BREAKPOINT_STATE_ENABLED = 1
BREAKPOINT_STATE_DISABLED=2

class BreakpointBase(object):

    def __init__(self,_type,state=1):

        self.state=1
        self.type=_type

    def set_id(self,i):
        
        self.id = i
        
class LineBreakpoint(BreakpointBase):

    def __init__(self,state,line,filename):

        BreakpointBase.__init__(self,"LineBreakpoint",state)
        self.line = line
        self.filename= filename

class AddressBreakpoint(BreakpointBase):

    def __init__(self,state,address):

        BreakpointBase.__init__(self,"AddressBreakpoint",state)
        self.address=address

class FunctionBreakpoint(BreakpointBase):

    def __init__(self,state,func):

        BreakpointBase.__init__(self,"FunctionBreakpoint",state)
        self.func=func

class Watchpoint(BreakpointBase):

    def __init__(self,var,condition,state=1):

        BreakpointBase.__init__(self,"Watchpoint",1)
        self.var = var
        self.condition=condition
        
class CatchpointBase(BreakpointBase):

    def __init__(self,state=1):

        BreakpointBase.__init__(self,"Catchpoint",state)

class CatchpointThrow(CatchpointBase):

    def __init__(self,state=1):

        CatchpointBase.__init__(self,state)
        self.type="Catchpoint Throw"
        
class CatchpointExec(CatchpointBase):

    def __init__(self,state=1):

        CatchpointBase.__init__(self,state)
        self.type="Catchpoint Exec"
        
class CatchpointCatch(CatchpointBase):

    def __init__(self,state=1):

        CatchpointBase.__init__(self,state)
        self.type="Catchpoint Catch"
        
class CatchpointSysCall(CatchpointBase):

    def __init__(self,syscall,state=1):

        self.syscall=syscall
        CatchpointBase.__init__(self,state)
        self.type="Catchpoint SysCall"
