#!/usr/bin/python

"""
Copyright (c) 2012 Janne Blomqvist

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Fix SSI include paths to not include a .., which is forbidden.
"""

import os

def fix_ssi_include(fname, doc_root):
    """
    fname: File name of file to fix.
    doc_root: Document root for the file.
    """
    import tempfile, re, stat
    file_dir = os.path.dirname(os.path.abspath(fname))
    droot = os.path.abspath(doc_root)
    # File dir, relative to doc root
    cp = os.path.commonprefix([file_dir, droot])
    if cp != droot:
        raise Exception('File %s not under document root %s' 
                        % (os.path.abspath(fname), droot))
    file_dir_rel = file_dir[len(cp):]
    f = open(fname)
    ft = tempfile.NamedTemporaryFile(dir=file_dir, delete=False)
    modified = False
    incre = re.compile('<!--#\s*include\s*(?:virtual|file)\s*=\s*"(.*?)"', 
                       re.DOTALL)
    fdat = f.read()
    sstart = 0
    for m in re.finditer(incre, fdat):
        ft.write(fdat[sstart:m.start()])
        sstart = m.end()
        # Full path to include file
        if m.group(1)[0] == '/':
            fip = os.path.join(droot, m.group(1)[1:])
        else:
            fip = os.path.join(file_dir, m.group(1))
        fip = os.path.abspath(fip)
        # Remove docroot
        cp = os.path.commonprefix([fip, droot])
        if cp != droot:
            os.remove(ft.name)
            raise Exception('File %s included from %s not under document \
root %s' % (fip, os.path.abspath(fname), droot))
        fip = fip[len(cp):]
        # Is the path relative to the dir of the file?
        cp = os.path.commonprefix([file_dir_rel, fip])
        if cp == file_dir_rel:
            fip = fip[(len(cp)+1):]
        modified = True
        ft.write('<!--#include virtual="%s"' % fip)
    if modified:
        ft.write(fdat[sstart:])
        oldstat = os.fstat(f.fileno())
        f.close()
        os.fchmod(ft.fileno(), oldstat.st_mode)
        os.fchown(ft.fileno(), oldstat.st_uid, oldstat.st_gid)
        os.rename(ft.name, fname)
    else:
        os.remove(ft.name)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 3:
        droot = sys.argv[2]
    elif len(sys.argv) == 2:
        print "WARNING: Document root not specified, using current working\
 directory: ", os.getcwd()
        droot = os.getcwd()
    else:
        print "Usage: fixssiinclude.py FILENAME DOC_ROOT_PATH"
        sys.exit(1)
    fix_ssi_include(sys.argv[1], droot)
