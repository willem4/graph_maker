from pathlib import Path

import pandas as pd
from ortools.sat.python import cp_model

from graph_maker.graph import Graph

def test_time_indexed_resource_constraint_with_overlap() -> None:
    def _norm(name: str) -> str:
        return name.strip('"')

    fixture_dir = Path(__file__).parent
    links_csv = fixture_dir / "links.csv"
    nodes_csv = fixture_dir / "nodes.csv"

    links_df = pd.read_csv(links_csv, sep=";", header=0, comment="#")

    graph = Graph()
    graph.from_csv(str(links_csv), str(nodes_csv))
    assert len(graph.get_edges()) == len(links_df)

    activities = tuple(_norm(node.get_name()) for node in graph.get_nodes())
    durations = {
        _norm(node.get_name()): int(node.get_attributes().get("duration", "1").strip('"'))
        for node in graph.get_nodes()
    }
    precedence = tuple(
        (_norm(edge.get_source()), _norm(edge.get_destination()))
        for edge in graph.get_edges()
    )

    # Only B and C consume the shared resource.
    # resource_demand = {"A": 1, "B": 1, "C": 1, "D": 1}
    capacity = 2
    horizon = sum(durations.values())

    model = cp_model.CpModel()

    # Binary decision variables x[i, t] = 1 iff activity i starts at time t.
    x = {
        (i, t): model.new_bool_var(f"x_{i}_{t}")
        for i in activities
        for t in range(horizon + 1)
    }

    # Start-time variables s_i = sum_t t * x[i, t].
    s = {
        i: model.new_int_var(0, horizon, f"s_{i}")
        for i in activities
    }

    # Each activity starts exactly once.
    for i in activities:
        model.add(sum(x[(i, t)] for t in range(horizon + 1)) == 1)

    # Link start-time variables to the binary variables.
    for i in activities:
        model.add(s[i] == sum(t * x[(i, t)] for t in range(horizon + 1)))

    # Each activity must finish within the horizon.
    for i in activities:
        model.add(s[i] + durations[i] <= horizon)

    # Precedence: s_j >= s_i + d_i.
    for i, j in precedence:
        model.add(s[j] >= s[i] + durations[i])

    # Resource capacity at each time tau:
    # sum_i r_i * sum_{t: t <= tau < t + d_i} x[i, t] <= R.
    for tau in range(horizon):
        usage_terms = []
        for i in activities:
            active_sum = sum(
                x[(i, t)]
                for t in range(horizon + 1)
                if t <= tau < t + durations[i]
            )
            usage_terms.append(active_sum)
        model.add(sum(usage_terms) <= capacity)

    # Minimize makespan to pick the best feasible schedule.
    makespan = model.new_int_var(0, horizon, "makespan")
    for i in activities:
        model.add(makespan >= s[i] + durations[i])
    model.minimize(makespan)

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    r = sorted([(t, i) for i in activities for t in range(horizon + 1) if solver.value(x[(i, t)]) > 0])
    for t, i in r:
        print(f"Activity {i} : {t} -> {t + durations[i]}")

    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    best_makespan = int(solver.value(makespan))
    best_starts = {i: int(solver.value(s[i])) for i in activities}

if __name__ == "__main__":
    test_time_indexed_resource_constraint_with_overlap()
# [END program]
