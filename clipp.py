#!/usr/bin/python3
import re
import sys
debugPrint1=0

def quoteOrComment(matchobj):
    if(matchobj.group(1)):
        return ""
    elif(matchobj.group(2)):
        return matchobj.group(2)
    elif(matchobj.group(3)):
        return matchobj.group(3)
    elif(matchobj.group(4)):
        sys.stderr.write("Unterminated Comment\n")
        return ""

def removeComments(s):
    removeBlocks = re.compile(r'(/\*.*?\*/)|(\".*?\")|(\'.*?\')|(/\*.*)',flags=re.DOTALL)
    s=re.sub(removeBlocks, quoteOrComment ,s)
    return s 

#important is "DEFINE" case sensitive
#important get rid of trailing white space in group2
def define(macros,s):
    matchobj = re.match(r"#\s*define\s+([a-zA-z_][a-zA-z_0-9]*)\s*(.*)\s*",s)
    if(matchobj):
        macros[matchobj.group(1)]=matchobj.group(2).rstrip()
    else:
       sys.stderr.write("Bad define macro\n")
    return macros

def subWithMacro(reBlock,s, macros):
    matchobjs = re.finditer(reBlock, s)
    additionalIndices=0
    for matchobj in matchobjs:
        if(matchobj.group(3)): 
            string=matchobj.group(3)
            if(string in macros.keys()):
                original=string
                string= macros[string]
                if(debugPrint1):
                    print("Current Line: " + s + " being replaced by " + string  +  " at "  + str(matchobj.start() + additionalIndices) + " to " + str(matchobj.end() + additionalIndices))
                s = s[:matchobj.start()+additionalIndices] + string + s[matchobj.end()+additionalIndices:]
                additionalIndices+= len(string) - len(original)
                
    return s



def normalLine(macros, s):
    reBlock = re.compile(r'(\".*?\")|(\'.*?\')|([a-zA-z_0-9]*)')
    while(s != subWithMacro(reBlock,s,macros)):
            s = subWithMacro(reBlock, s, macros)
    if(s=='\n'):
        print('')
    else:
        print(s)


def badQuotes(s):
    if(s.count('\'')%2==1 or s.count('\"')%2==1):
        sys.stderr.write("Bad number of quotes\n")

def ifstatement(macros, curLine, lines):
    matchobj=re.match(r"^\s*#\s*ifdef\s+(.*)\s*", curLine)
    name = matchobj.group(1)
    inElse=0
    if(debugPrint1):
        print("Name in if directive: " + name)
    if(name not in macros.keys()):
        inElse=1
        while((re.match(r"^\s*#\s*else\s*",curLine)==None) and (re.match(r"^\s*#\s*endif\s*",curLine)==None)):
            if(lines):
                curLine=lines.pop(0)
            else:
                sys.stderr.write("missing #endif\n")
                return [macros, lines]
        if(re.match(r"^\s*#\s*endif\s*",curLine)):
                return [macros, lines]
    curLine=lines.pop(0)
    while((re.match(r"^\s*#\s*else\s*",curLine)==None) and (re.match(r"^\s*#\s*endif\s*",curLine)==None)):
        badQuotes(curLine)
        if(debugPrint1):
            print("IN WHILE LOOP:" + curLine)
        if(re.match(r"^\s*#\s*define\s+.*", curLine)):
            macros = define(macros, curLine)
        elif(re.match(r"^\s*#\s*ifdef\s+.*", curLine)):
            output = ifstatement(macros, curLine, lines)
            macros= output[0]
            lines = output[1]
        elif(re.match(r"^\s*#.*",curLine)):
            sys.stderr.write("Unexpected direcative\n")
        else:
            normalLine(macros, curLine)
        if(lines):
            curLine= lines.pop(0)
        else:
            sys.stderr.write("line 94missing #endif\n")
            return [macros, lines]
    #if we reached the else statment
    if(re.match(r"^\s*#\s*else\s*",curLine)):
        if(debugPrint1):
            print("AT ELSE STATEMENT")
        if(inElse):
            sys.stderr.write("extra else statement\n")
            return [macros, lines]
        else:
            if(debugPrint1):
                print("In useless else statement")
            while(re.match(r"^\s*#\s*endif\s*",curLine)==None):
                if(lines):
                    curLine= lines.pop(0)
                else:
                    sys.stderr.write("missing #endif\n")
                    return [macros, lines]
    if(debugPrint1):
        print("At end of endif function:" + str(lines))
    return [macros, lines]




def overall(macros, s):
    s=removeComments(s)
    lines=s.splitlines()
    if(debugPrint1):
        print("List of Lines:" + str(lines))
    for line in range(0, len(lines)):
        if(lines[line]=='' and line!=len(lines)-1):
            lines[line]='\n'
    macros={}
    curLine= lines.pop(0)
    while(curLine):

        badQuotes(curLine)
        if(debugPrint1):
            print("Current Line " + curLine)
        if(re.match(r"^\s*#\s*define\s+.*", curLine)):
            if(debugPrint1):
                print("We are about to define value")
            macros = define(macros, curLine)
        elif(re.match(r"^\s*#\s*ifdef\s+.*", curLine)):
            output = ifstatement(macros, curLine, lines)
            if(debugPrint1):
                print("Done with entering if statement")
            macros= output[0]
            lines = output[1]
        elif(re.match(r"^\s*#.*",curLine)):
            sys.stderr.write("Unexpected direcative\n")
        else:
            normalLine(macros, curLine)
        if(lines):
            curLine= lines.pop(0)
        else:
            curLine=None

macros = {}

inputString = sys.stdin.read()

overall(macros, inputString)


