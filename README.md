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

Different standard node types are available. 
For example see `tests/legend`

![Legend graph](tests/legend/graph.png)

