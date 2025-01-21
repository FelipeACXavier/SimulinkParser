# Simulink parser

This parser reads a folder which contains one or multiple Simulink models and outputs a JSON file using the knowledge representation outlined in [Enabling Analysis and Reasoning on Software Systems through Knowledge Graph Representation (MSR'23)](https://doi.org/10.1109/MSR59073.2023.00029)

To use the parser follow the steps below:

```bash
# Create and activate a virtual environment
python -m venv env
source env/bin/activate

# Install the dependencies
pip install -e .

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

## Parsing C/C++ 

To parse the S-Function blocks, the parser requires the [srcML](https://www.srcml.org/) tool that does a pretty good job of parsing these source codes.
However, this tool needs to be compiled before it can be used. 
The complete list of dependencies for different operating systems is available in the [official build instructions](https://github.com/lihebi/srcml/blob/master/BUILD.md).
To compile the tool, follow the instructions below:

```bash
# Clone the git repository 
git clone https://github.com/srcML/srcML.git

# cd into that directory
cd srcML

# Create build directory
mkdir build && cd build

# Download the required boost libraries
wget -qO- http://www.sdml.cs.kent.edu/build/srcML-1.0.0-Boost.tar.gz | gunzip | tar xvf -

# Prepare to build
cmake -DBOOST_INCLUDES=./ ../

# Build
make -j4
```

srcML outputs a specific flavour of XML that is much easier to parse compared to standard C/C++. 
This is the output used by our S-Function parser.

## Known limitations

MathWorks like to change their file structure from time to time what makes it hard to ensure the correct parsing for all the innumerable Matlab/Simulink versions.
Taking that in consideration, we decided to limit the scope of the parser to more recent versions.
Therefore, the parser was only tested with versions 2018b to 2024b.

## To Do

While a lot is already done, this is an ongoing project.
The parser was tested with Simulink 2018b until 2024b.

- [ ] Parse C functions embedded as S-Functions
- [ ] Create link between S-Functions and the called C functions
