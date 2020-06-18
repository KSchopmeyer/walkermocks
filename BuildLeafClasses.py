#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  BuildLeafClasses.py
#
#  Copyright 2019 FarmerMike <FarmerMike252@Yahoo.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

"""
This program builds a list of leaf classes for a specific profile
and the interop namespace profiles (both SNIA and WBEM Server). The
program lists the SMI-S profiles and asks which one you want to generate
leaf classes for.
"""
""" First we import modules we will need """
import os
import xml.etree.ElementTree as ET
import xml.dom
import xml.dom.minidom
import xml.dom.pulldom
import xml.sax
import xml.parsers.expat
from xml.dom.minidom import parse, parseString, getDOMImplementation
from xml.etree.ElementTree import Element, SubElement, tostring, XML
import collections
import pywbem
import pywbem_mock

# global CONN

# version definition of the DMTF schema.  This is the version currently
# installed by default in pywbem github.  Cloning pywbem to get the
# development components means this schema is already installed in the
# directory
#   tests/schema
schema_version = (2, 51, 0)
# print(schema_version)

# definition of the directory where the schema is installed in the
# github clone of pywbem
# You can chose any directory you want to.  If you are using pip to
# install pywbem, chose a directory off the root of your virtual environment.
# I think we will even create the directory if it does not exist.
# TESTSUITE_SCHEMA_DIR = os.path.join('tests', 'schema')
# print(TESTSUITE_SCHEMA_DIR)
# TESTSUITE_SCHEMA_DIR = os.path.join('schema')
# print(TESTSUITE_SCHEMA_DIR)

# conn = pywbem_mock.FakedWBEMConnection(default_namespace='root/cimv2')
# print(conn)

# verbose = False
# if verbose is True:
#     CONN.display_repository()
""" GET THE LIST OF AUTONOMOUS PROFILES AND ASK THE USER WHICH ONE HE WANTS """
##
profileindex = -1
namelist = []
filelist = []
aprofiles = open('ModifiedProfiles.xml', mode='r')

modprofs = ET.parse('ModifiedProfiles.xml')  # Read ModifiedProfiles.xml into dom
mproot = modprofs.getroot()

print('The valid autonomous profile names are: ')

for supp in mproot.findall('SMIS'):
    if supp.attrib['AUTONOMOUS'] == 'true':
        fullname = supp.attrib['ORGANIZATION'] + '_' + supp.attrib['NAME']
        namelist.append(fullname)
        filelist.append(supp.attrib['FILE'])
        print('A ' + fullname)

fullname = input('What autonomous Profile do you want to build?')
"""Get the name of the autonomous profile from the user
If the user does not provide a valid name an exception should be
returned. """
if fullname in namelist:
    profileindex = namelist.index(fullname)
else:
    fullname = input('Invalid name, try again. What Profile do you \
    want to build? ')
##
""" NEED TO READ SNIA_SERVERCLASSTABLE.XML TO GENERATE THE STRING OF UNIQUE
Server CLASSES """
print('Getting classes for the SNIA Server')
sclist = []
sctfile = 'SNIA_ServerClassTable.xml'
try:
    servct = ET.parse(sctfile)  # Read the ClassTable.xml into dom
except KeyError:
    print('Class Table not found')
sctroot = servct.getroot()
for scentry in sctroot.findall('ENTRY'):
    if scentry.attrib['CLASS'] == scentry.attrib['PARENT_CLASS']:
        sclist.append(scentry.attrib['CLASS'])
# print(sclist)
# Next we read the object map to get the association classes
salist = []
smapfile = 'SNIA_ServerObjectMap.xml'
try:
    servmap = ET.parse(smapfile)  # Read the ObjectMap.xml into dom
except KeyError:
    print('Object Map not found')
smaproot = servmap.getroot()
for clss in smaproot.findall('CLASS'):
    for shrb in clss.findall('SHRUB'):
        for cl in shrb.findall('CLASS'):
            salist.append(cl.attrib['NAME'])
# print(salist)

""" NEED TO READ DMTF_WBEM SERVERCLASSTABLE.XML TO GENERATE THE STRING OF UNIQUE
Server CLASSES """
print('Getting classes for the DMTF WBEM Server')
dwsclist = []
dwsctfile = 'DMTF_WBEM ServerClassTable.xml'
try:
    dwservct = ET.parse(dwsctfile)  # Read the ClassTable.xml into dom
except KeyError:
    print('Class Table not found')
dwsctroot = dwservct.getroot()
for dwscentry in dwsctroot.findall('ENTRY'):
    if dwscentry.attrib['CLASS'] == dwscentry.attrib['PARENT_CLASS']:
        dwsclist.append(dwscentry.attrib['CLASS'])
# print(dwsclist)
# Next we read the object map to get the association classes
dwsalist = []
dwsmapfile = 'DMTF_WBEM ServerObjectMap.xml'
try:
    dwservmap = ET.parse(dwsmapfile)  # Read the ObjectMap.xml into dom
except KeyError:
    print('Object Map not found')
dwsmaproot = dwservmap.getroot()
for clss in dwsmaproot.findall('CLASS'):
    for shrb in clss.findall('SHRUB'):
        for cl in shrb.findall('CLASS'):
            dwsalist.append(cl.attrib['NAME'])
# print(dwsalist)

""" NEED TO READ PROFILE_CLASSTABLE.XML TO GENERATE THE STRING OF UNIQUE
LEAF CLASSES """
# fullname = 'SNIA_Array'
print('Getting classes for ', fullname)
clist = []
ctfile = fullname + 'ClassTable.xml'
try:
    profct = ET.parse(ctfile)  # Read the ClassTable.xml into dom
except KeyError:
    print('Class Table not found')
ctroot = profct.getroot()
for centry in ctroot.findall('ENTRY'):
    if centry.attrib['CLASS'] == centry.attrib['PARENT_CLASS']:
        clist.append(centry.attrib['CLASS'])
# print(clist)

# Next we read the object map to get the association classes
palist = []
autoproffile = fullname + 'ObjectMap.xml'

try:
    aobjectmap = ET.parse(autoproffile)  # parse profile
except KeyError:
    print('Object Map not found')
root = aobjectmap.getroot()
for clss in root.findall('CLASS'):
    for shrb in clss.findall('SHRUB'):
        for cl in shrb.findall('CLASS'):
            palist.append(cl.attrib['NAME'])
# print(palist)

# create common single list from lists for various profiles
all_leaf_classes = sclist + dwsclist + clist + salist + dwsalist + palist

# remove non-unique items from list
unique_leaf_classes = set(all_leaf_classes)

dups = [item for item, count in collections.Counter(all_leaf_classes).items()
        if count > 1]

# Open Output file
leaflist = fullname + "_leaflist.mof"
dumpfile = open(leaflist, 'w')
# dumpentry = '<?xml version="1.0" encoding="UTF-8"?>'
# dumpfile.write(dumpentry)
dumpfile.write(unique_leaf_classes)
dumpfile.close()
