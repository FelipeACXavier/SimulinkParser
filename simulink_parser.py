from pathlib import Path
from zipfile import ZipFile

import os
import json
import argparse
import common.datatypes as dt

from common.helpers import *
from common.logging import *
from parsers.xml import parse_XML, create_connections


def extract_archive(archive: str, extract_path: str):
    with ZipFile(archive, 'r') as zip:
        # If we want to see what is inside
        # zip.printdir()
        zip.extractall(path=extract_path)


def create_module_name(uid):
    return ''.join([t.title() for t in uid.replace('_', ' ').split()])


def create_module(uid):
    name = create_module_name(uid)

    data = dt.NodeData()
    data.id = uid
    data.labels = ['Container']
    data.properties.simpleName = name
    data.properties.qualifiedName = name
    data.properties.visibility = "Public"
    data.properties.kind = "package"

    node = dt.Node()
    node.data = data

    return node


def is_module_in_list(module_path, module_list):
    for m in module_list:
        if m in module_path:
            return True

    return False


def find_all_and_parse(root_dir, parent_id, graph, args):
    # Recursively look for simulink models
    for item in os.listdir(root_dir.absolute()):
        path = Path(os.path.join(f'{root_dir.absolute()}', item))
        if path.suffix == '.slx':
            # Directory is the containing package
            package = root_dir.name

            LOG_INFO(f'Found Simulink system: {path.name} in {package}')
            if args.list:
                continue

            tmp_dir = f'{root_dir.absolute()}/{TMP_DIR}/{path.stem}'
            extract_archive(path, tmp_dir)

            # Find system files
            systems = [f.resolve() for f in Path(f'{tmp_dir}/{SYSTEM_DIR}').glob('*.xml')]

            # Define the system level package
            node = create_module(path.stem)
            graph.elements.nodes.append(node)

            e_data = dt.EdgeData()
            e_data.id = f'{package}_contains_{node.data.id}'
            e_data.label = 'contains'
            e_data.source = package
            e_data.target = node.data.id

            edge = dt.Edge()
            edge.data = e_data
            graph.elements.edges.append(edge)

            set_system_level(node.data.id)

            for system in systems:
                if system.name == SYSTEM_ROOT:
                    parse_XML(system, node.data.id, graph, systems)
                    break

            # Create connection from top blocks to modules
            LOG_DEBUG(f'Creating connections for package: {package}')
            create_connections(graph)

            # At this level, we only parse the root system
            continue

        if not path.is_dir():
            continue

        package = path.name

        # Take into consideration the excluded modules5
        if is_module_in_list(package, args.exclude):
            continue

        if args.include and not is_module_in_list(package, args.include):
            continue

        package_node = create_module(package)
        graph.elements.nodes.append(package_node)

        e_data = dt.EdgeData()
        e_data.id = f'{parent_id}_contains_{package}'
        e_data.label = 'contains'
        e_data.source = parent_id
        e_data.target = package

        edge = dt.Edge()
        edge.data = e_data
        graph.elements.edges.append(edge)

        find_all_and_parse(path, package, graph, args)


def parse_xml_file(args, graph):
    file = Path(args.xml)
    set_system_level("root")

    parse_XML(file, "root", graph, [])


def parse_simulink_files(args, graph):
    current_dir = Path(args.dir)
    systems_dir = 'simulink/systems'

    # Create global graph
    graph = dt.Graph()

    # Define some type to be used as return
    n_data = dt.NodeData()
    n_data.id = MATLAB_TYPE
    n_data.labels = ['Primitive']
    n_data.properties.simpleName = MATLAB_TYPE.replace('_', ' ')
    n_data.properties.qualifiedName = MATLAB_TYPE

    t_node = dt.Node()
    t_node.data = n_data

    graph.elements.nodes.append(t_node)

    # Define the system package
    system_uid = current_dir.name
    LOG_INFO(f'Creating root level package: {system_uid}')
    graph.elements.nodes.append(create_module(system_uid))

    # With the information gathered, it is time to traverse the folder
    find_all_and_parse(current_dir.absolute(), system_uid, graph, args)


def main(args):
    start_logger(LogLevel[args.log_level])

    # Create global graph
    graph = dt.Graph()

    if args.xml is None:
        parse_simulink_files(args, graph)
    else:
        parse_xml_file(args, graph)

    with open(args.output, 'w+') as file:
        file.write(json.dumps(json.loads(graph.to_json()), indent=2 if args.formatted else None))


# ============================================================================================================
# Define command line arguments
parser = argparse.ArgumentParser()

parser.add_argument("-d", "--dir", default=".", type=str, help="Root folder of the project")
parser.add_argument("-o", "--output", default="output.json", type=str, help="Output file in json format")
parser.add_argument("-e", "--exclude", nargs='*', default=[], help="Modules to exclude from the project")
parser.add_argument("-i", "--include", nargs='*', default=[], help="Only include modules listed here")
parser.add_argument("-f", "--formatted", action='store_true', help="Whether the output file should be formatted")
parser.add_argument("-l", "--list", action='store_true', help="Just list encountered modules without parsing")
parser.add_argument("--xml", default=None, type=str, help="Parse an XML file instead")
parser.add_argument("--log-level", default='INFO', type=str,
                    help="Level of logging to output during parsing: ERROR, WARNING, INFO, DEBUG")

args = parser.parse_args()

# Start of main
if __name__ == "__main__":
    main(args)
