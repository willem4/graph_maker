"""CLI entry point for graph_maker."""

import click
from graph_maker.graph import Graph
from pathlib import Path

@click.command()
@click.option('--links', default='links.csv', help='CSV file containing graph links')
@click.option('--nodes', default='nodes.csv', help='CSV file containing graph nodes')
@click.option('--output', default='graph.dot', help='Output file for the graph')
@click.option('--plan', is_flag=True, help='Calculate and display early start, early finish, late start, and late finish for each node')
# @click.option('--capacity', default=1, help='Maximum number of concurrent tasks (resource constraint)')
# TODO: add option for resources - i.e. max number of concurrent tasks, (opionally display resource allocation in the graph)
def main(links, nodes, output, plan) -> None:
    """Run the graph_maker command line interface."""

    g = Graph(bgcolor='white')
    g.from_csv(links, nodes)   

    if plan:
        if g.is_cyclic():
            click.echo("Error: Cannot compute early/late start/finish for cyclic graphs.")
            return
        g.compute_critical_path()

    g.save_as_dot(output)
    g.save_as_png(output.replace('.dot','.png'))

if __name__ == "__main__":
    main()
