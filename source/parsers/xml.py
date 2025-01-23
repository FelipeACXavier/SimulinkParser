import re

import parsers.block as bp
import parsers.line as lp
import common.datatypes as dt
import xml.etree.ElementTree as ET

from common.logging import *
from common.helpers import *


def create_implicit_port_node(text, data, graph):
    try:
        match = re.match(r'(.*)_(input|output)_(.*)', text)
        return bp.create_port_node(match.group(1), match.group(3), match.group(2), graph=graph)
    except:
        LOG_ERROR(f'Failed to find match for:\n{print_json(data)}')
        raise


def get_edge_connections(data, graph):
    LOG_DEBUG(f'Looking for src: {data.source} and {data.target}')

    source = None
    target = None

    for node in graph.elements.nodes:
        if node.data.id == data.source:
            source = node.data
        elif node.data.id == data.target:
            target = node.data

        if source is not None and target is not None:
            break

    # In case no source or target are found, then these are implicit and we must define the nodes here
    if source is None:
        node, _ = create_implicit_port_node(data.source, data, graph)
        source = node.data

    if target is None:
        node, _ = create_implicit_port_node(data.target, data, graph)
        target = node.data

    return source, target


def create_connection(src, dst):
    if src == 'Script':
        if dst == 'Script':
            return 'invokes'
        elif dst == 'Operation':
            return 'invokes'
        elif dst == 'Structure':
            LOG_WARNING(f'Script -> Structure: I do not think this is allowed')
            return ''
        elif dst == 'Container':
            LOG_WARNING(f'Script -> Container: I do not think this is allowed')
            return ''
    elif src == 'Operation':
        if dst == 'Script':
            return 'invokes'
        elif dst == 'Operation':
            return 'invokes'
        elif dst == 'Structure':
            LOG_WARNING(f'Script -> Structure: I do not think this is allowed')
            return ''
        elif dst == 'Container':
            LOG_WARNING(f'Script -> Container: I do not think this is allowed')
            return ''
    elif src == 'Structure':
        if dst == 'Script':
            return 'hasScript'
        elif dst == 'Operation':
            return 'hasScript'
        elif dst == 'Structure':
            return 'contains'
        elif dst == 'Container':
            LOG_WARNING(f'Structure -> Container: I do not think this is allowed')
            return ''
    elif src == 'Container':
        if dst == 'Script':
            return 'hasScript'
        elif dst == 'Operation':
            return 'hasScript'
        elif dst == 'Structure':
            return 'contains'
        elif dst == 'Container':
            return 'contains'


def create_connections(graph):
    for edge in graph.elements.edges:
        source, target = get_edge_connections(edge.data, graph)

        # Set label in case it wasn't defined before
        if edge.data.label:
            continue

        LOG_DEBUG(f'Connecting {source.labels} to {target.labels}')
        edge.data.label = create_connection(source.labels[0], target.labels[0])


def parse_blocks(system, parent_id, graph, systems):
    # Iterate news items
    for block in system.findall('./Block'):
        # print_xml(block)
        block_type = block.attrib["BlockType"]
        if block_type == 'S-Function':
            bp.parse_s_function(block, parent_id, graph)
        elif block_type == 'SubSystem':
            bp.parse_subsystem(block, parent_id, graph, systems)
        elif block_type == 'Reference':
            bp.parse_reference(block, parent_id, graph)
        elif block_type == 'Constant':
            bp.parse_constant(block, parent_id, graph)
        elif block_type == 'EnablePort':
            bp.parse_enable_port(block, parent_id, graph)
        elif block_type == 'Inport' or block_type == 'Outport':
            bp.parse_port_block(block, parent_id, graph)
        else:
            bp.parse_primitive(block, parent_id, graph)


def parse_lines(system, parent_id, graph, tree):
    for line in system.findall('./Line'):
        lp.parse_line(line, parent_id, graph, tree)


def parse_XML(xml_file, parent_id, graph, systems):
    # create element tree object
    LOG_INFO(f'Parsing system: {xml_file.name}')
    tree = ET.parse(xml_file)

    # Get root element
    system = tree.getroot()

    # Iterate news items
    parse_blocks(system, parent_id, graph, systems)
    parse_lines(system, parent_id, graph, tree)
