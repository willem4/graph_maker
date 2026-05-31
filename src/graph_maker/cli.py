"""CLI entry point for graph_maker."""

import click
from graph_maker.graph import Graph
from pathlib import Path

@click.command()
@click.option('--links', default='links.csv', help='CSV file containing graph links')
@click.option('--nodes', default='nodes.csv', help='CSV file containing graph nodes')
@click.option('--output', default='graph.dot', help='Output file for the graph')
def main(links, nodes, output) -> None:
    """Run the graph_maker command line interface."""
    g = Graph()
    g.from_csv(links, nodes)   
    g.save_as_dot(output)
    g.save_as_png(output.replace('.dot','.png'))

if __name__ == "__main__":
    main()
