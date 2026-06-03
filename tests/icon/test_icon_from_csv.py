from pathlib import Path

import pandas as pd

from graph_maker.graph import Graph


def test_icon_from_csv_applies_node_and_link_extras() -> None:
    fixture_dir = Path(__file__).parent
    links_csv = fixture_dir / "links.csv"
    nodes_csv = fixture_dir / "nodes.csv"

    links_df = pd.read_csv(links_csv, sep=";", header=0, comment="#")

    graph = Graph()
    graph.from_csv(str(links_csv), str(nodes_csv))

    assert len(graph.get_edges()) == len(links_df)

    dot_text = graph.to_string()

    assert "Start -> End" in dot_text
    assert "style=dashed" in dot_text
    assert "Start" in dot_text
    assert "shape=parallelogram" in dot_text
    assert "fillcolor=orange" in dot_text
    assert "End" in dot_text
    assert "fillcolor=lightgreen" in dot_text
    assert "color=red" in dot_text