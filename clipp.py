#!/usr/bin/python3
import re
import sys
debugPrint1=0 

def quoteOrComment(matchobj):
    string = matchobj.group(1)
    if(string[0] == '/'):
        return ""
    else:
        return string


def removeComments(s):
    removeBlocks = re.compile(r'(/\*.*?\*/)|(\".*?\")|(\'.*?\')',flags=re.DOTALL)
    s=re.sub(removeBlocks, quoteOrComment ,s)
    return s 

#important is "DEFINE" case sensitive
#important get rid of trailing white space in group2
def define(macros,s):
    matchobj = re.match(r"#\s*define\s+([a-zA-z_][a-zA-z_0-9]*)\s*(.*)",s)
    if(matchobj):
        macros[matchobj.group(1)]=matchobj.group(2)
    else:
       sys.stderr.write("Bad define macro\n")
    return macros

def subWithMacro(reBlock,s, macros):
    outputString = ""
    matchobjs = re.findall(reBlock, s)

    for matchobj in matchobjs:
        string=""
        for match in matchobj:
            if(match!=''):
                string=match

        if(string):
            if(re.match(r"(^[a-zA-z_0-9]).*", string)):
                if(string in macros.keys()):
                    outputString+= macros[string]
                else:
                    outputString+= string
            else:
                outputString+= string
    return outputString



def normalLine(macros, s):
    reBlock = re.compile(r'(\".*?\")|(\'.*?\')|([a-zA-z_0-9\s]*)|([^a-zA-z_0-9\'\"\s]*)')
    while(s != subWithMacro(reBlock,s,macros)):
            s = subWithMacro(reBlock, s, macros)
    if(s):
        if(s[len(s)-1]!='\n'):
            s+='\n'
    return s


def ifstatement(macros, curLine, lines):
    matchobj=re.match(r"^#\s*ifdef\s+(.*)\s*", curLine)
    outputString=""
    name = matchobj.group(1)
    inElse=0
    if(debugPrint1):
        print("Name in if directive: " + name)
    if(name not in macros.keys()):
        inElse=1
        while((re.match(r"^#\s*else\s*",curLine)==None) and (re.match(r"^#\s*endif\s*",curLine)==None)):
            if(lines):
                curLine=lines.pop(0)
            else:
                sys.stderr.write("missing #endif\n")
                return [macros, lines, outputString]
        if(re.match(r"^#\s*endif\s*",curLine)):
                return [macros, lines, outputString]
    curLine=lines.pop(0)
    while((re.match(r"^#\s*else\s*",curLine)==None) and (re.match(r"^#\s*endif\s*",curLine)==None)):
        if(re.match(r"^#\s*define\s+.*", curLine)):
            macros = define(macros, curLine)
        elif(re.match(r"^#\s*ifdef\s+.*", curLine)):
            output = ifstatement(macros, curLine, lines)
            macros= output[0]
            lines = output[1]
            outputString += output[2]
        elif(re.match(r"^#.*",curLine)):
            sys.stderr.write("Unexpected direcative\n")
        else:
            outputString+= normalLine(macros, curLine)
        if(lines):
            curLine= lines.pop(0)
        else:
            sys.stderr.write("line 94missing #endif\n")
            return [macros, lines, outputString]
    #if we reached the else statment
    if(re.match(r"^\s*else\s*",curLine)):
        if(inElse):
            sys.stderr.write("extra else statement\n")
            return [macros, lines, outputString]
        else:
            if(debugPrint1):
                print("In useless else statement")
            while(re.match(r"^#\s*endif\s*",curLine)==None):
                if(lines):
                    curLine= lines.pop(0)
                else:
                    sys.stderr.write("missing #endif\n")
                    return [macros, lines, outputString]
    if(debugPrint1):
        print("At end of endif function:" + str(lines))
    return [macros, lines, outputString]




def overall(macros, s):
    outputString=""
    lines=s.splitlines()
    if(debugPrint1):
        print("List of Lines:" + str(lines))
    for line in range(0, len(lines)):
        if(lines[line]=='' and line!=len(lines)-1):
            lines[line]='\n'
    macros={}
    curLine= lines.pop(0)
    while(curLine):
        if(debugPrint1):
            print("Current Line " + curLine)
        if(re.match(r"^#\s*define\s+.*", curLine)):
            if(debugPrint1):
                print("We are about to define value")
            macros = define(macros, curLine)
        elif(re.match(r"^#\s*ifdef\s+.*", curLine)):
            output = ifstatement(macros, curLine, lines)
            if(debugPrint1):
                print("Done with entering if statement")
            macros= output[0]
            lines = output[1]
            outputString += output[2]
        elif(re.match(r"^#.*",curLine)):
            sys.stderr.write("Unexpected direcative\n")
        else:
            outputString+= normalLine(macros, curLine)
        if(lines):
            curLine= lines.pop(0)
        else:
            curLine=None
    return outputString



macros = {}

inputString = sys.stdin.read()

print(overall(macros, inputString), end='')


