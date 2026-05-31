from pathlib import Path

import pandas as pd

from graph_maker.graph import Graph


def test_legend_from_csv_builds_all_expected_node_types() -> None:
    fixture_dir = Path(__file__).parent
    links_csv = fixture_dir / "links.csv"
    nodes_csv = fixture_dir / "nodes.csv"

    links_df = pd.read_csv(links_csv, sep=";", header=0, comment="#")

    graph = Graph()
    graph.from_csv(str(links_csv), str(nodes_csv))

    assert len(graph.get_edges()) == len(links_df)

    dot_text = graph.to_string()

    # Input node style
    assert "Input\\n(Input)" in dot_text
    assert "shape=parallelogram" in dot_text

    # Completed node style
    assert "Apply Model1\\n(Completed)" in dot_text
    assert "fillcolor=green" in dot_text

    # Failed node style
    assert "Outcome1\\n(Failed)" in dot_text
    assert "fillcolor=red" in dot_text

    # Decision node style
    assert "Choose best outcome\\n(Decision)" in dot_text
    assert "shape=diamond" in dot_text

    # Available node style
    assert "Validation\\n(Available)" in dot_text
    assert "fillcolor=lightgreen" in dot_text

    # Research Question node style
    assert "Answer research question\\n(Research Question)" in dot_text
    assert "fillcolor=orange" in dot_text
