import os
import re

import parsers.xml as xmlp
import common.datatypes as dt
import xml.etree.ElementTree as ET

from pathlib import Path
from common.helpers import *
from common.logging import *


def create_node_data(block, labels, visibility, kind=None):
    data = dt.NodeData()
    data.id = id_from_element(block)
    data.labels = labels

    # These are constant for Simulink
    data.properties.visibility = 'Public'
    data.properties.kind = kind if kind else 'method'
    data.properties.simulinkType = block.attrib["BlockType"]
    data.properties.simpleName = block.attrib["Name"]
    data.properties.qualifiedName = block.attrib["Name"]
    data.properties.sourceText += f'{ET.tostring(block, encoding='unicode')}'

    return data


def create_variable(element, parent):
    data = dt.NodeData()
    data.id = f'{parent.data.properties.qualifiedName}_{element.attrib["Name"]}'
    data.labels = ['Variable']

    data.properties.kind = 'parameter'
    data.properties.visibility = 'Public'
    data.properties.simpleName = element.attrib["Name"]
    data.properties.qualifiedName = element.attrib["Name"]
    data.properties.sourceText += f'{ET.tostring(element, encoding='unicode')}'

    node = dt.Node()
    node.data = data

    e_data = dt.EdgeData()
    e_data.id = f'{parent.data.id}_has_variable_{data.id}'
    e_data.label = 'hasVariable'
    e_data.source = parent.data.id
    e_data.target = data.id

    edge = dt.Edge()
    edge.data = e_data

    return node, edge


def find_file(filename):
    # Main directory sits above module directory
    for dirpath, dnames, fnames in os.walk(get_root_dir()):

        # Ignore the virtual environment and the temporary paths
        if 'env' in dirpath or 'tmp' in dirpath:
            continue

        for f in fnames:
            if filename == Path(f).stem:
                return Path(os.path.join(dirpath, f))

    return None


def create_contains_edge(parent_id, child_id, label='contains'):
    e_data = dt.EdgeData()
    e_data.id = f'{parent_id}_{child_id}'
    e_data.label = label
    e_data.source = parent_id
    e_data.target = child_id

    edge = dt.Edge()
    edge.data = e_data

    return edge


def create_port_node(parent_id, uid, port_type, name=None, graph=None):
    n_data = dt.NodeData()
    n_data.id = f'{parent_id}_{port_type}_{uid}'
    n_data.labels = ['Operation']

    qualified_name = name if name else f'{parent_id}_{port_type}_{uid}'
    n_data.properties.kind = 'method'
    n_data.properties.visibility = 'Public'
    n_data.properties.simpleName = qualified_name
    n_data.properties.qualifiedName = qualified_name
    n_data.properties.sourceText = f'port_label(\'{port_type}\', {uid}, \'{qualified_name}\')'

    node = dt.Node()
    node.data = n_data

    e_data = dt.EdgeData()
    e_data.id = f'{parent_id}_has_script_{node.data.id}'
    e_data.label = 'hasScript'
    e_data.source = parent_id
    e_data.target = node.data.id

    edge = dt.Edge()
    edge.data = e_data

    # Add return type
    if graph is not None:
        return_data = dt.EdgeData()
        return_data.id = f'return_{node.data.id}'
        return_data.label = 'returnType'
        return_data.source = n_data.id
        return_data.target = MATLAB_TYPE
        return_data.properties.kind = 'type'

        return_edge = dt.Edge()
        return_edge.data = return_data

        graph.elements.edges.append(return_edge)

    return node, edge


def parse_new_named_ports(port_info, parent_id, graph):
    for match, port_type, uid, name in re.findall(r"(port_label\('(input|output)',\s*(\d{1,3}),\s*'(.*)'\))", port_info.text):
        node, edge = create_port_node(parent_id, uid, port_type, name, graph)
        graph.elements.nodes.append(node)
        graph.elements.edges.append(edge)


def parse_old_style_ports(port, parent_id, graph):
    match = re.search(r'\[((\d{1,4}),\s*(\d{1,4}))?', port.text)
    if not match or None in match.groups():
        LOG_DEBUG(f'Block {port.attrib['Name']} has no ports')
        return

    n_in = int(match.group(2))
    n_out = int(match.group(3))

    for inp in range(n_in):
        node, edge = create_port_node(parent_id, inp + 1, 'input')
        graph.elements.nodes.append(node)
        graph.elements.edges.append(edge)

    for out in range(n_out):
        node, edge = create_port_node(parent_id, out + 1, 'output')
        graph.elements.nodes.append(node)
        graph.elements.edges.append(edge)


def parse_new_style_ports(port, parent_id, graph):
    n_in = 0 if 'in' not in port.attrib else int(port.attrib['in'])
    n_out = 0 if 'out' not in port.attrib else int(port.attrib['out'])

    for inp in range(n_in):
        node, edge = create_port_node(parent_id, inp + 1, 'input')
        graph.elements.nodes.append(node)
        graph.elements.edges.append(edge)

    for out in range(n_out):
        node, edge = create_port_node(parent_id, out + 1, 'output')
        graph.elements.nodes.append(node)
        graph.elements.edges.append(edge)


def parse_block_port(port, port_type, parent_id, graph):
    node, edge = create_port_node(parent_id, 1, 'input' if port_type == 'Inport' else 'output')
    graph.elements.nodes.append(node)
    graph.elements.edges.append(edge)


def parse_ports(block, parent, graph):
    # We must recover the parent info first
    parent_id = parent.data.id
    parent_name = parent.data.properties.qualifiedName

    # If block has names for the ports, use those, otherwise just use their numbers
    # The id is always <block id>_<input|output>_<port id>
    port_info = block.find('.//Mask/Display')
    if port_info is not None and port_info.text is not None:
        parse_new_named_ports(port_info, parent_id, graph)
        return

    LOG_DEBUG(f'{parent_name}: Ports with no names, using their number instead')

    old_ports = block.findall('.//P[@Name="Ports"]')
    if len(old_ports) == 1:
        parse_old_style_ports(old_ports[0], parent_id, graph)
        return

    new_ports = block.findall('.//PortCounts')
    if len(new_ports) == 1:
        parse_new_style_ports(new_ports[0], parent_id, graph)
        return

    block_ports = block.findall('.//Port')
    if len(new_ports) == 1 and 'BlockType' in block.attrib:
        parse_block_port(block_ports[0], block.attrib["BlockType"], parent_id, graph)
        return

    # We assume a single default port
    LOG_DEBUG(f'Block {block.attrib["Name"]} has not explicit ports, they will be derived later')

    # raise Exception(f'Invalid block, unknown file format:\n{print_xml(block)}')


# TODO: Implement c side parsing
def parse_c_file(function_name, graph):
    c_file = find_file(function_name)
    if c_file is None:
        LOG_WARNING(f'Could not find {function_name} in the current path')
        return

    in_file = f'{c_file.absolute()}'
    out_file = f'{get_root_dir()}/{TMP_DIR}/{c_file.stem}.xml'

    LOG_INFO(f'Found C function in: {c_file}, writing to {out_file}')

    if not run_command(f'/home/felaze/Documents/PhD/Programs/SimulinkParser/srcML/build/bin/srcml {in_file} -o {out_file}'):
        raise Exception(f'Failed to parse C function: {in_file}')


def parse_s_function(block, parent_id, graph):
    LOG_DEBUG(f'Parsing s-function: {block.attrib["Name"]}')

    # Create node and define its unique id
    node = dt.Node()
    node.data = create_node_data(block, ['Structure'], 'Public', 'class')

    names = block.findall('.//P[@Name="FunctionName"]')
    if len(names) != 1:
        raise Exception(f'Invalid s-function, none or too many names provided {print_xml(block)}')

    node.data.properties.qualifiedName = names[0].text

    # We now must define the ports, i.e., functions
    parse_ports(block, node, graph)

    graph.elements.nodes.append(node)

    # Make sure this block is contained in the parent node
    graph.elements.edges.append(create_contains_edge(parent_id, node.data.id))

    for prop in block.findall('./P'):
        if prop.attrib['Name'] == 'FunctionName':
            continue

        param, edge = create_variable(prop, node)
        graph.elements.nodes.append(param)
        graph.elements.edges.append(edge)

    # Once the properties and the edges were created,
    # we can move on to parsing the C side
    parse_c_file(names[0].text, graph)


def parse_subsystem(block, parent_id, graph, systems):
    LOG_DEBUG(f'Parsing subsystem: {block.attrib["Name"]}')

    # Create node and define its unique id
    node = dt.Node()
    node.data = create_node_data(block, ['Container'], 'Public', 'package')

    # We now must define the ports, i.e., functions
    parse_ports(block, node, graph)

    graph.elements.nodes.append(node)

    # Make sure this block is contained in the parent node
    graph.elements.edges.append(create_contains_edge(parent_id, node.data.id))

    # Once we are done with the block itself, proceed with the sub-system
    reference = f'system_{block.attrib["SID"]}'
    for system in systems:
        if reference in system.name:
            xmlp.parse_XML(system, node.data.id, graph, systems)
            return


def parse_reference(block, parent_id, graph):
    LOG_DEBUG(f'Parsing reference: {block.attrib["Name"]} inside {parent_id}')

    # Create node and define its unique id
    node = dt.Node()
    node.data = create_node_data(block, ['Structure'], 'Public', 'class')

    names = block.findall('.//P[@Name="SourceBlock"]')
    if len(names) != 1:
        raise Exception(f'Invalid reference, none or too many names provided {print_xml(block)}')

    node.data.properties.qualifiedName = names[0].text

    # We now must define the ports, i.e., functions
    parse_ports(block, node, graph)

    graph.elements.nodes.append(node)

    # Make sure this block is contained in the parent node
    graph.elements.edges.append(create_contains_edge(parent_id, node.data.id, 'contains'))


def parse_constant(block, parent_id, graph):
    LOG_DEBUG(f'Parsing Terminator: {block.attrib["Name"]}')

    # Create node and define its unique id
    node = dt.Node()
    node.data = create_node_data(block, ['Variable'], 'Public', 'field')

    graph.elements.nodes.append(node)

    # Make sure this block is contained in the parent node
    graph.elements.edges.append(create_contains_edge(parent_id, node.data.id, 'hasVariable'))


def parse_enable_port(block, parent_id, graph):
    # This is essentially a port that Matlab treats as a block
    LOG_DEBUG(f'Parsing EnablePort: {block.attrib["Name"]}')

    # Since it is a port, it is created in by its owner and there it no need to recreate it here
    return


def parse_primitive(block, parent_id, graph):
    LOG_DEBUG(f'Parsing {block.attrib["BlockType"]}: {block.attrib["Name"]}')

    # Create node and define its unique id
    node = dt.Node()
    node.data = create_node_data(block, ['Structure'], 'Public', 'class')

    graph.elements.nodes.append(node)

    # Primitives are blocks, so they must also have ports
    parse_ports(block, node, graph)

    # Make sure this block is contained in the parent node
    graph.elements.edges.append(create_contains_edge(parent_id, node.data.id))
