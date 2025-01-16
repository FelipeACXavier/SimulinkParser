# Simulink parser

This parser reads a folder which contains one or multiple Simulink models and outputs a JSON file using the knowledge representation outlined in [Enabling Analysis and Reasoning on Software Systems through Knowledge Graph Representation (MSR'23)](https://doi.org/10.1109/MSR59073.2023.00029)

To use the parser follow the steps below:

```bash
# Create and activate a virtual environment
python -m venv env
source env/bin/activate

# Install the dependencies
pip install -r requirements.txt

# Run the help menu for further instructions
python simulink_parser.py
```

## Structure

Since Simulink doesn't follow a common object oriented approach, some insights were necessary to make the representation work with it.

The mapping is shown below:

| Matlab              | Representation  |
| ------------------- | --------------- |
| *Ports*             | *Methods*       |
| *Blocks*            | *Classes*       |
| *Folders*           | *Packages*      |
| *Block parameters*  | *Members*       |

Since the Simulink descriptor does not provide the data type of the ports, each method, i.e., port, 
assumes a "matlab object" data type.

Based on the selected representation, when there is a signal between two blocks in Simulink, the communicating ports are connected through an "*invokes*" edge type.

## To Do

While a lot is already done, this is an ongoing project.
The parser was tested with Simulink 2018b until 2024b.

- [ ] Parse C functions embedded as S-Functions
- [ ] Create link between S-Functions and the called C functions
