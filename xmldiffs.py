#!/usr/bin/env python
"""
File: xmldiffs.py

Copyright 2004-2017 Adaptive Insights, Inc.  
All Rights Reserved.

This work contains trade secrets and confidential material of 
Adaptive Insights, Inc., and its use or disclosure in whole or in part 
without the express written permission of Adaptive Insights, Inc., is prohibited.

Compare two folders containing matching XML file names, and diffs the files
ignoring element and attribute order. Outputs diffs in an html file.

Based on xmldiffs.py created by Johannes H. Jensen.
"""
import argparse
import sys
import os
import xml.etree.cElementTree as ET
import subprocess
import os
from os.path import join
import time

decimals = 0

def isWindows():
    return os.name == 'nt'

def round_float(s):
    try:
        f = float(s)
        return str(round(f, decimals) + 0)
    except ValueError:
        return s

def remove_file_extention(f):
    return os.path.splitext(f)[0]

def file_exists(folder, file):
    return os.path.isfile(join(folder, file))

def make_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def attr_str(k, v):
    v = round_float(v)
    return "{}=\"{}\"".format(k,v)

def node_str(n):
    attrs = sorted(n.attrib.items())
    astr = " ".join(attr_str(k, v) for k,v in attrs)
    s = n.tag
    if astr:
        s += " " + astr
    return s

def node_key(n):
    return node_str(n)

def indent(s, level):
    return "  " * level + s

def write_sorted(stream, node, level=0):
    children = node.getchildren()
    text = round_float((node.text or "").strip())
    tail = round_float((node.tail or "").strip())

    if children or text:
        children.sort(key=node_key)

        stream.write(indent("<" + node_str(node) + ">\n", level))

        if text:
            stream.write(indent(text + "\n", level))

        for child in children:
            write_sorted(stream, child, level + 1)

        stream.write(indent("</" + node.tag + ">\n", level))
    else:
        stream.write(indent("<" + node_str(node) + "/>\n", level))

    if tail:
        stream.write(indent(tail + "\n", level))

if sys.version_info < (3, 0):
    # Python 2
    import codecs
    def unicode_writer(fp):
        return codecs.getwriter('utf-8')(fp)
else:
    # Python 3
    def unicode_writer(fp):
        return fp

def open_write_file(file, folder):
    cleanfile = join(folder, file)
    make_folder(folder)
    writefile = open(cleanfile, "w")
    return writefile, cleanfile

def xmlsort(file, folder1, folder2, cleanfolder):
    file1 = join(folder1, file)
    tree = ET.parse(file1)
    write1, f1clean = open_write_file(file, join(cleanfolder, folder1))
    write_sorted(write1, tree.getroot())
    write1.close()

    file2 = join(folder2, file)
    tree = ET.parse(file2)
    write2, f2clean = open_write_file(file, join(cleanfolder, folder2))
    write_sorted(write2, tree.getroot())
    write2.close()

    return f1clean, f2clean

def xml_multiple_diffs(folder1, folder2, resultsfolder="out", cleanfolder="cleaned"):
    t_list = list()
    files = [f for f in os.listdir(folder1) if file_exists(folder1, f)]
    for f in files:
        t = time.time()
        if not file_exists(folder2, f):
            continue
        make_folder(resultsfolder)
        fname = remove_file_extention(f)
        out = join(resultsfolder, fname) + ".html"
        t1clean, t2clean = xmlsort(f, folder1, folder2, cleanfolder)

        if isWindows():
            args = ["sh", "diff_to_html.sh"]
            out = out.replace("\\", "/s")
        else: 
            args = ['./diff_to_html.sh']
        args += [ t1clean, t2clean, out ]
        subprocess.call(args, shell=isWindows())

        t_list.append(time.time() - t)

    print(t_list)

def print_usage(prog):
    print(__doc__.format(prog=prog).strip())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("folder1", help="location of the pre snap xml files")
    parser.add_argument("folder2", help="location of the post snap xml files")
    parser.add_argument("-d", default="out", metavar="DIFF_FOLDER", help="location to place diffs, default is \"out\"")
    parser.add_argument("-x", default="cleaned", metavar="XML_FOLDER", help="location to place ordered xmls, default is \"cleaned\"")
    parser.add_argument("-r", default=2, metavar="INT", type=int, help="decimal places to round numbers to, default is 2")
    args = parser.parse_args()
    decimals = args.r
    xml_multiple_diffs(args.folder1, args.folder2, args.d, args.x)