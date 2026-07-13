from pathlib import Path

from graph_maker.graph import Graph


def _norm(node_name: str) -> str:
    # pydot may quote node names in some cases.
    return node_name.strip('"')


def test_cyclic_from_csv_preserves_arrow_direction() -> None:
    fixture_dir = Path(__file__).parent
    links_csv = fixture_dir / "links.csv"
    nodes_csv = fixture_dir / "nodes.csv"

    graph = Graph()
    graph.from_csv(str(links_csv), str(nodes_csv))

    actual_edges = {
        (_norm(edge.get_source()), _norm(edge.get_destination()))
        for edge in graph.get_edges()
    }
    expected_edges = {
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("C", "A"),
    }

    assert actual_edges == expected_edges

    # Explicitly verify important reverse directions are not present.
    assert ("B", "A") not in actual_edges
    assert ("C", "B") not in actual_edges
    assert ("D", "C") not in actual_edges
    assert ("A", "C") not in actual_edges

    assert graph.is_cyclic() is True
