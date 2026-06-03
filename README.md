# graph-maker

Simple graph-maker based on pydot

## Requirements

- Python 3.10+
- For conversion to png GraphViz and Inkscape are required

## Installation 
```
install_venv.bat
```

## Usage

```bash
Usage: cli.py [OPTIONS]

  Run the graph_maker command line interface.

Options:
  --links TEXT   CSV file containing graph links
  --nodes TEXT   CSV file containing graph nodes
  --output TEXT  DOT file for the graph (see graphviz.org)
  --help         Show this message and exit.
```

At minimum a CSV file for the *links* is needed. It contains the columns Node1;Node2;Extra. The columns are separated by a semi-colon (;).
In the Extra column different style attributes can be added. For details see (https://graphviz.org/docs/edges/) 

A *nodes* CSV file is automatically generated. This file contains the columns Node;Extra separated by a semi-colon. The extra column can contain different style attributes (https://graphviz.org/docs/nodes/). In addition, different standard *node* types are available. 
For example see `tests/legend`

![Legend graph](tests/legend/graph.png)

## Testing 

Tests are included in the tests folder and can be run using:
```bash
python -m pytest
```
