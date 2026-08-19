from pathlib import Path

from click.testing import CliRunner

from graph_maker.cli import main
from graph_maker.graph import Graph


def test_plan_option_computes_critical_path(tmp_path, monkeypatch) -> None:
    fixture_dir = Path(__file__).parent
    nodes_path = fixture_dir / "nodes.csv"
    output_path = tmp_path / "graph.dot"

    monkeypatch.setattr(Graph, "save_as_png", lambda self, filename: None)
    nodes_path.unlink(missing_ok=True)

    try:
        result = CliRunner().invoke(
            main,
            [
                "--links",
                str(fixture_dir / "links.csv"),
                "--nodes",
                str(fixture_dir / "nodes.csv"),
                "--output",
                str(output_path),
                "--plan",
            ],
        )

        assert result.exit_code == 0
        dot_text = output_path.read_text()
        assert '"A\\n1" [duration=1, shape=record' in dot_text
        assert 'label="B\\n|1|{1|2}|{{1}|{2}}"' in dot_text
        assert 'C -> F [color=red]' in dot_text
    finally:
        nodes_path.unlink(missing_ok=True)