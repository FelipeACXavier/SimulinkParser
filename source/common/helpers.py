import os
import json
import subprocess

# Debug
from xml.dom import minidom
import xml.etree.ElementTree as ET

from common.logging import *

# Constants
MATLAB_TYPE = 'matlab_object'
SYSTEM_ROOT = 'system_root.xml'
TMP_DIR = 'tmp'
SYSTEM_DIR = 'simulink/systems'


def set_srcml(srcml):
    global SRC_ML
    SRC_ML = srcml


def get_srcml():
    global SRC_ML
    return SRC_ML


def set_root_dir(root_dir):
    global ROOT_DIR
    ROOT_DIR = root_dir


def get_root_dir():
    global ROOT_DIR
    return ROOT_DIR


def set_system_level(level):
    global SYSTEM_LEVEL
    SYSTEM_LEVEL = level


def system_level():
    global SYSTEM_LEVEL
    return SYSTEM_LEVEL


def define_source(src, src_port):
    return f'{system_level()}_{src}_output_{system_level()}_{src_port}'


def define_target(dst, dst_port):
    global SYSTEM_LEVEL
    return f'{system_level()}_{dst}_input_{system_level()}_{dst_port}'


def id_from_element(element):
    # return f'{element.attrib["Name"].replace(" ", "_")}_{element.attrib["SID"]}'
    return f'{system_level().replace(" ", "_")}_{element.attrib["SID"]}'
    # return f'{element.attrib["SID"]}'


def print_xml(elem):
  # Nicely print XML elements during debug stage
    def prettify_and_fix_spaces(input_string):
        return '\n'.join([line for line in minidom.parseString(input_string).toprettyxml(indent=' '*2).split('\n') if line.strip()])

    rough_string = ET.tostring(elem, 'unicode')
    return prettify_and_fix_spaces(rough_string)


def print_json(elem):
    return json.dumps(json.loads(elem.to_json()), indent=2)
