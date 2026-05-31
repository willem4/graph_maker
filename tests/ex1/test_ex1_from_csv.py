from pathlib import Path

import pandas as pd

from graph_maker.graph import Graph


def test_from_csv_builds_graph_from_links_and_nodes() -> None:
    fixture_dir = Path(__file__).parent
    links_csv = fixture_dir / "links.csv"
    nodes_csv = fixture_dir / "nodes.csv"

    links_df = pd.read_csv(links_csv, sep=";", header=0, comment="#")

    graph = Graph()
    graph.from_csv(str(links_csv), str(nodes_csv))

    assert len(graph.get_edges()) == len(links_df)

    dot_text = graph.to_string()
    assert "Measurements" in dot_text
    assert "shape=parallelogram" in dot_text
    assert "Bed level" in dot_text
    assert "fillcolor=green" in dot_text
    assert "Calibration Step 1" in dot_text
    assert "shape=diamond" in dot_text
