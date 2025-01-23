from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config, LetterCase

# node = {
#   "data": {
#     "id": "node1",
#     "labels": [],
#     "properties": {
#       "visibility": "",
#       "simpleName": "",
#       "qualifiedName": "",
#       "kind": "",
#       "sourceText": "",
#       "docComment": "",
#       "metaSrc": ""
#     }
#   }
# }


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class NodeProperties:
    simpleName: str
    qualifiedName: str
    description: Optional[str] = field(default=None, metadata=config(exclude=lambda f: f is None))
    kind: Optional[str] = field(default=None, metadata=config(exclude=lambda f: f is None))
    visibility: Optional[str] = field(default=None, metadata=config(exclude=lambda f: f is None))
    sourceText: Optional[str] = field(default=None, metadata=config(exclude=lambda f: f is None))
    metaSrc: Optional[str] = field(default=None, metadata=config(exclude=lambda f: f is None))
    simulinkType: Optional[str] = field(default=None, metadata=config(exclude=lambda f: f is None))
    docComment: Optional[str] = field(default=None, metadata=config(exclude=lambda f: f is None))

    def __init__(self):
        self.simpleName = ""
        self.qualifiedName = ""
        self.metaSrc = 'source code'


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class NodeData:
    id: str
    properties: NodeProperties
    labels: list[str]

    def __init__(self):
        self.id = ""
        self.labels = []
        self.properties = NodeProperties()


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Node:
    data: NodeData

    def __init__(self):
        self.data = NodeData()

# edge = {
#   "data": {
#     "id": "",
#     "label": "",
#     "source": "",
#     "target": "",
#     "properties": {
#       "weight": 1,
#       "kind": "",
#       "metaSrc": ""
#     }
#   }
# }


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EdgeProperties:
    weight: int
    metaSrc: str
    kind: Optional[str] = field(default=None, metadata=config(exclude=lambda f: f is None))

    def __init__(self):
        self.weight = 1
        self.metaSrc = 'source code'


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EdgeData:
    id: str
    label: str
    source: str
    properties: EdgeProperties
    target: str

    def __init__(self):
        self.id = ""
        self.label = ""
        self.source = ""
        self.target = ""
        self.properties = EdgeProperties()


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Edge:
    data: EdgeData

    def __init__(self):
        self.data = EdgeData()

# structure = {
#   "elements": {
#     "nodes": [],
#     "edges": []
#   }
# }


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Elements:
    nodes: list[Node]
    edges: list[Edge]

    def __init__(self):
        self.nodes = []
        self.edges = []


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Graph:
    elements: Elements

    def __init__(self):
        self.elements = Elements()
