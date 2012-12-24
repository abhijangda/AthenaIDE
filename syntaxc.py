#209 Lines

import sys
from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

def format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format('blue'),
    'datatypes': format('darkorange'),
    'modifiers': format('darkblue'),        
    'operator': format('red'),
    'brace': format('darkGray'),
    'string': format('magenta'),
    'directive': format('darkMagenta'),
    'comment': format('darkGreen', 'italic'),
    'numbers': format('brown'),
    }


class CHighlighter (QSyntaxHighlighter):
    """Syntax highlighter for the C language.
    """
    # C keywords
    keywords = ['break','case','continue','default',
                'do','else','for','goto','if','return',
                'sizeof','switch','typedef','while']
    # C Datatypes
    datatypes = ['char','float','short','signed','struct','int',
                 'long','enum','double','unsigned','union','void']
    # C Modifiers
    modifiers = ['auto','extern','register','volatile','const','static']
        
    # C operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # C braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        
        rules = []
                
        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in CHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in CHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in CHighlighter.braces]
        rules += [(r'\b%s\b' % b, 0, STYLES['modifiers'])
            for b in CHighlighter.modifiers]
        rules += [(r'\b%s\b' % b, 0, STYLES['datatypes'])
            for b in CHighlighter.datatypes]
                
        # All other rules
        rules += [

            #For directives
            (r'#+(.)+',0,STYLES['directive']),
            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            #For includes with doubly quoted strings
            (r'#+(.)+"+(.)+"',0,STYLES['directive']),
            #For comment           
            #(r'/\*(.)+\*/',0,STYLES['comment']),
            (r'//[^\n]*', 0, STYLES['comment']),
            
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]

        self.comment_started = False
        self.index_comment_start = -1
        self.index_comment_end = -1

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        
        str_text = str(text)
        if self.comment_started == False:            
        # Do other syntax formatting
            for expression, nth, format in self.rules:
                index = expression.indexIn(text, 0)
                
                while index >= 0:
                    # We actually want the index of the nth match
                    index = expression.pos(nth)
                    length = expression.cap(nth).length()
                    self.setFormat(index, length, format)
                    index = expression.indexIn(text, index + length)
            self.setCurrentBlockState(0)

            self.index_comment_start = str_text.find('/*')
            if self.index_comment_start !=-1:
                self.index_comment_end = -1
                #print 'found /*',self.comment_started
                if '*/' in str_text:
                    #print 'found */ and /*',self.comment_started
                    self.index_comment_end = str_text.index('*/')                    
                    self.setFormat(self.index_comment_start,self.index_comment_end-self.index_comment_start+2,STYLES['comment'])                    
                else:
                    #print 'found /* and not */',self.comment_started
                    self.comment_started = True
                    self.setFormat(self.index_comment_start,len(str_text)-self.index_comment_start,STYLES['comment'])
            else:                
                if '*/' in str_text:
                    #print 'found not /* and */',self.comment_started
                    self.index_comment_end = str_text.index('*/')
                    self.setFormat(0,self.index_comment_end+2,STYLES['comment'])
        else:
            if '*/' in str_text and '/*' in str_text:
                #print 'found /* and */',self.comment_started
                self.index_comment_end = str_text.index('*/')
                self.index_comment_start = -1
                self.setFormat(self.index_comment_start,len(str_text)-self.index_comment_end-self.index_comment_start,STYLES['comment'])
                self.comment_started = False
            else:
                if '*/' in str_text:
                    #print 'found not /* and */',self.comment_started
                    self.comment_started = False
                    self.index_comment_end = str_text.index('*/')
                    self.setFormat(0,self.index_comment_end+2,STYLES['comment'])
                else:
                    if '/*' in str_text:
                        #print 'found /* and not */',self.comment_started
                        self.setFormat(self.index_comment_start,len(str_text)-self.index_comment_start,STYLES['comment'])
                    else:
                        #print 'found not/* and not */',self.comment_started
                        self.setFormat(0,len(str_text),STYLES['comment'])        
        
        #self.comment_start = QRegExp("/\*")
        #self.comment_end = QRegExp("\*/")
        #self.match_multiline(text, self.comment_start,self.comment_end,1, STYLES['comment'])
        
    def match_multiline(self, text, delimiter_start,delimiter_end, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        """# If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter_start.indexIn(text)
            # Move past this match
            add = delimiter_start.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter_end.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter_start.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = text.length() - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter_end.indexIn(text, start + length)"""        
