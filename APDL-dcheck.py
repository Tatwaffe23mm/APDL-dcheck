#!/usr/bin/python
import os
import sys
import re
import ntpath
import xml.dom.minidom
import argparse

def makeVariableDict(fn, d):
    fn = os.path.abspath(fn)
    fs = open(fn, 'r')
    if verbose and check == False:
        print('Make dict for: ' + fn)
    rx = re.compile(r'\w=[\'\w]+', re.IGNORECASE)
    lc = 0
    for l in fs:
        lc =lc+1
        l = l.rstrip('\n') #Remove newlines
        l = l.strip() #Remove trailing whitespaces
        l = l.split('!') #Remove comments at the end of the line
        l = l[0]
        l = l.replace(' ','') #Remove internal whitespaces
        #parse command
        matches = rx.search(l)
        if matches != None:
            pline = l.split('=')
            key = pline[0]
            value = pline[1]
            if d.get(key) == None:
                d[key] = value.replace('\'','')
            else:
                if key == 'sector':
                    d[key] = value.replace('\'','')                                        
    return d

def parseBatchFile(wd, fi, d, ds):
    fp = os.path.join(wd, fi.replace(' ', ''))
    fp = os.path.normpath(fp)
    fo = open(fp, 'r')
    r = re.compile('-i')
    fl = []
    for line in fo:
        match = r.search(line)
        if match != None:
            line = line.split('-i')[1]
            line = line.strip()
            fn = line.split(' ')[0]
            if ds.get(fi) == None:
                ds[fi] = dict()
            
            fl.append(fn)
            ds[fi] = unique(fl)
    return ds

def parseMacFile(wd, fi, d, ds):
    fc = []
    try:
        fp = os.path.abspath(os.path.join(wd, fi.strip()))
        fo = open(fp, 'r')
        d = makeVariableDict(fp, d)
        regex = re.compile(r'(/input|\*use)', re.IGNORECASE) #search term for file calls, looks for /input and *use commands
        if verbose and check == False:
            print('\tMatching lines in file:')        
        #for each line in the file
        for line in fo:
            #check whether it contains a file call
            line = line.strip() #Remove trailing whitespaces from line
            rmatches = regex.match(line)
            #for each found match

            if rmatches != None:
                if verbose and check == False:
                    print('\t%s' % (line))
                line = line.split('!')  # Clean line from comments at the end
                line = line[0]
                line = line.replace(' ', '')  # Remove spaces
                line = line.split(',')  # split command line into command block and arguments
                cmd  = line[0]
                if cmd.lower() == '/input':
                    if line[2].strip() != '':
                        fn = line[1] + '.' +  line[2].strip()
                    else:
                        fn = line[1]
                else:
                    fn = line[1]
                rp = re.compile(r'%\w*%')   #check for substitutions
                o = rp.findall(fn)
                
                #in case there are substitutions in the command, try to replace them by known variables in the variable dictionary
                if o != None:           
                    for e in o:
                        rs = re.compile(r'\w+')
                        subs = rs.findall(e)
                        if d.get(subs[0]) == None:
                            if verbose and check == False:
                                print('Look for substitution of ' + subs[0])
                            #try to find the substitution in files already listed
                            for af in fc:
                                afp = os.path.join(wd, af.replace(' ', ''))
                                afp = os.path.normpath(afp)
                                d = makeVariableDict(afp, d) #Extend the substitution dictionary by searching the files called by the file
                            d[subs[0]] = sv
                    
                    ff = fn
                    for e in o:
                        rr = re.compile(r'' + e + '')
                        e  = e.strip('%')
                        sv = d[e] 
                        ff = rr.sub(sv, ff)     
                        if ds.get(fi) == None:
                            ds[fi] = dict()
                            
                fc.append( ff)
                
            ds[fi] = unique(fc)
            
        #Recursively search the files found 
        if len(fc)>0:
            fc = unique(fc)
            if check==False:
                print('\tFound file calls (unified list):')
            for e in fc:
                fp = os.path.join(wd, e.strip())
                fp = os.path.normpath(fp)
                if check==False:
                    print('\t' + fp )
            #Recursively search the files found 
            out = searchFileForFileCalls(wd, fc, d, ds)
        else:
            if check==False:
                print('No file calls found in file ' + fp)
        
    except FileNotFoundError:
        if check==False:
            print('ERROR: File Not found, check file name of ' + fp )
        if ds.get('fnf') == None:
            ds['fnf'] = []
        ds['fnf'].append(fp)
    
    return ds

#Recursion function to read files and look for file calls
def searchFileForFileCalls(wd, fi, d, ds):
    if type(fi) == type(str()):
        fn = fi
        fi = []
        fi.append(fn)
    for f in fi:
        ext = (os.path.basename(f)).split('.')[1]
        #build a normalized path
        fp = os.path.join(wd, f.replace(' ', ''))
        fp = os.path.normpath(fp)
        if check == False:
            print('\n> Search file ' + fp )
        fc = [] #empty list
        if ext == 'bat' or ext == 'sh':
            ds = parseBatchFile(wd, f, d, ds)
            out = searchFileForFileCalls(wd, ds[f], d, ds)
        else:
            #open the file and get a file handle
           out = parseMacFile(wd, f, d, ds)
           #out = searchFileForFileCalls(wd, fc, d, ds)
    return ds

def unique(seq, idfun=None): 
   # order preserving
   # code from http://www.peterbe.com/plog/uniqifiers-benchmark
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       # in old Python versions:
       # if seen.has_key(marker)
       # but in new ones:
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result            

def printItems(fid, ds, key):
    l = ds.get(key)
    if l != None:
        for e in l:
            fid.write('<node TEXT="%s">' % (e))
            try:
                ftn = os.path.abspath(os.path.join(os.path.dirname(fid.name), e))
                open(ftn, 'r')
            except FileNotFoundError:
                fid.write('<icon BUILTIN="closed"/>')            
            
            printItems(fid, ds, e)
            fid.write( '</node>')               

def writeFreeMindXMLFile(fout, ds, fn):
    fn = os.path.basename(fn)
    with open(fout, 'wt') as fid:
        fid.write( '<map version="1.0.1">')
        fid.write('<node TEXT="' + fn + '">')     
        if check==False:       
            printItems(fid, ds, fn)
        fid.write( '</node>')                
             
        fid.write( '</map>')                   
        fid.close()
        if verbose and check == False:
            if fid.closed:
                print('File ' + fout + ' written.')
            else:
                print('Failed to write to file ' + fout)
    
    #Reformat the output
    xmlf = xml.dom.minidom.parse(fout) # or xml.dom.minidom.parseString(xml_string)
    pretty_xml_as_string = xmlf.toprettyxml()
    with open(fout, 'wt') as fid:
        fid.write(pretty_xml_as_string)
        fid.close()
    
# Main function body, starting the recursion
def main():
    
    parser = argparse.ArgumentParser(description='Check AMSYS APDL macros for it\'s dependencies and optionally create a FeeMind readable XML file of your APDL macro calls. This might be heplful for the documentation of your APDL code or checking purposes.')

    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
    parser.add_argument('file', type=argparse.FileType('r'),  help='Input file')
    parser.add_argument('-xml', action='store_true', help='write a FreeMind XML-file as output (default: file.mm)')
    parser.add_argument('outfile', nargs='?', help='Name of the output file')
    parser.add_argument('-c','--check', action='store_true', help='Check only whether all dependcies exist. Returns true (1) if all dependenies exist, otherwise the check fails (0). this option supresses all other output')
    parser.add_argument('-V','--version', action='version', version='%(prog)s 1.1')
    args = parser.parse_args()
    
 
    global verbose
    if args.verbose:
        verbose = args.verbose
    else:
        verbose = args.verbose

    if args.file:
        fn = os.path.basename(args.file.name)
        wd = os.path.dirname(args.file.name)
        np = fn.split('.')
        fout = os.path.join(wd, np[0] + '.mm')
        
        if args.xml:
            fout = os.path.join(wd, fout)
            
        if args.outfile:
            fout = os.path.join(wd, args.outfile)
        
    global check    
    check  = args.check

    status = True #Set the default return value of the script
    
    d = dict()  #Variable dictionary
    ds=  dict() #File call dictionary
    ds[fn] = dict() #First key of the dict.

    if verbose and check == False:
        print('List file dependencies for: ' + os.path.abspath(args.file.name))      

    #Call a recursion function which descends through all called files 
    d = makeVariableDict(args.file.name, d)
    ds = searchFileForFileCalls(wd, [fn], d, ds)
    if ds.get('fnf') != None:
        status = False #Overwirte the return value, if some dependencies did not exist
        if check == False:
            print('\nFiles called by other files, but not exisiting:')
            for i in ds['fnf']:
                print('\t ' + i + ' not found!')    
    if args.outfile or args.xml:    
        writeFreeMindXMLFile(fout, ds, args.file.name)
        
    if check == True:
        sys.stdout.write('%i' % (status))

#Main function call to start the program
if __name__ == "__main__":
    main()
