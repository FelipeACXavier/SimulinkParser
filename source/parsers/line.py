import re
import common.datatypes as dt

from common.logging import *
from common.helpers import *


def is_dst_port(tree, sid):
    element = tree.find(f'.//Block[@SID="{sid}"]')
    return element and (element.attrib["BlockType"] == "Outport")


def is_src_port(tree, sid):
    element = tree.find(f'.//Block[@SID="{sid}"]')
    return element and (element.attrib["BlockType"] == "Inport")


def create_edges(parent_id, line, src_element, destinations, graph, tree):
    source = re.search(r'(.*)#(\w+):?(.*)', src_element.text)
    if source is None or len(source.groups()) != 3:
        raise Exception(f'Invalid source, unrecognized format {src_element}')

    # match.group(0) is the full text
    src = source.group(1)
    src_port = source.group(3) if len(source.group(3)) > 0 else source.group(2)

    # Only create edge if we are not dealing with a port block
    # Those are created before in block.py
    src_name = None
    if is_src_port(tree, src):
        LOG_INFO(f'Not parsing input port: {src}:{src_port} from {parent_id}')
        src_name = f'{parent_id}_input_{system_level()}_{src_port}'
        # return

    # Edges can have multiple branches, for example, when one output connected with
    # multiple inputs. In that case, we need to consider each as a separate edge.
    for dest in destinations:
        # Make a copy of the data to make a new edge
        data = dt.EdgeData()
        destination = re.search(r'(.*)#(\w+):?(.*)', dest.text)

        if destination is None or len(destination.groups()) != 3:
            raise Exception(f'Invalid destination, unrecognized format {print_xml(line)}')

        dst = destination.group(1)
        dst_port = destination.group(3) if len(destination.group(3)) > 0 else destination.group(2)

        dst_name = None
        if is_dst_port(tree, dst):
            LOG_INFO(f'Not parsing output port: {dst}:{dst_port} from {parent_id}')
            dst_name = f'{parent_id}_output_{system_level()}_{dst_port}'
            continue

        data.source = src_name if src_name else define_source(src, src_port)
        data.target = dst_name if dst_name else define_target(dst, dst_port)
        data.id = f'{data.source}_invokes_{data.target}'
        data.label = 'invokes'

        # Store data to edge and save
        edge = dt.Edge()
        edge.data = data
        graph.elements.edges.append(edge)


def parse_line(line, parent_id, graph, tree):
    # Example or src and dst properties for regex
    # <P Name="Src">10#out:1</P>
    # <P Name="Dst">16#in:1</P>

    # Get the source of the edge
    sources = line.findall('.//P[@Name="Src"]')
    if len(sources) < 1:
        raise Exception(f'Invalid edge, no sources provided {print_xml(line)}')

    destinations = line.findall('.//P[@Name="Dst"]')
    if len(destinations) < 1:
        return

    for source in sources:
        create_edges(parent_id, line, source, destinations, graph, tree)
