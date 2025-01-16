import re
import common.datatypes as dt

from common.logging import *
from common.helpers import *


def parse_line(line, graph):
    # Example or src and dst properties for regex
    # <P Name="Src">10#out:1</P>
    # <P Name="Dst">16#in:1</P>

    # Get the source of the edge
    sources = line.findall('.//P[@Name="Src"]')
    if len(sources) != 1:
        raise Exception(f'Invalid edge, none or too many sources provided {print_xml(line)}')

    source = re.search(r'(.*)#out:(.*)', sources[0].text)
    if source is None or len(source.groups()) != 2:
        raise Exception(f'Invalid source, unrecognized format {print_xml(sources[0])}')

    # match.group(0) is the full text
    src = source.group(1)
    src_port = source.group(2)

    # Edges can have multiple branches, for example, when one output connected with
    # multiple inputs. In that case, we need to consider each as a separate edge.
    for dest in line.findall('.//P[@Name="Dst"]'):
        # Make a copy of the data to make a new edge
        data = dt.EdgeData()
        destination = re.search(r'(.*)#in:(.*)', dest.text)

        if destination is None or len(destination.groups()) != 2:
            raise Exception(f'Invalid destination, unrecognized format {print_xml(dest)}')

        dst = destination.group(1)
        dst_port = destination.group(2)

        data.source = define_source(src, src_port)
        data.target = define_target(dst, dst_port)
        data.id = f'{data.source}_invokes_{data.target}'
        data.label = 'invokes'

        # Store data to edge and save
        edge = dt.Edge()
        edge.data = data
        graph.elements.edges.append(edge)
