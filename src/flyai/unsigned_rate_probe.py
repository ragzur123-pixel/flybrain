"""Exploratory unsigned response probe; no physiology, learning, or motor action."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Mapping

from flyai.selected_graph import SelectedGraph


CHANNELS = ("left", "center", "right")


class UnsignedRateProbe:
    """Two-stage sparse software response to side-matched unit-interval cues.

    This is a candidate calculation for interface inspection, not the selected
    P4 model. Pair counts become positive incoming-normalized coefficients.
    """

    def __init__(self, graph: SelectedGraph, config: dict):
        if (config["nodes_csv_sha256"] != graph.nodes_sha256 or
                config["edges_csv_sha256"] != graph.edges_sha256):
            raise ValueError("Probe graph checksum differs from selected graph")
        if config["input_channels"] != list(CHANNELS) or config["input_range"] != [0.0, 1.0]:
            raise ValueError("Probe input channel contract changed")
        self.dt_s = float(config["dt_s"])
        self.alpha = float(config["relaxation_fraction_per_step"])
        if not math.isfinite(self.dt_s) or self.dt_s <= 0:
            raise ValueError("Probe time step must be positive and finite")
        if not math.isfinite(self.alpha) or not 0 < self.alpha <= 1:
            raise ValueError("Probe relaxation must be in (0, 1]")
        self.graph = graph
        self._photos = tuple(i for i, node in enumerate(graph.nodes)
                             if node.role == "photoreceptor")
        self._relays = tuple(i for i, node in enumerate(graph.nodes)
                             if node.role == "OCG01")
        self._outputs = graph.output_indices
        if len(self._outputs) != 4 or any(graph.nodes[i].role not in {"DNp20", "DNp22"}
                                         for i in self._outputs):
            raise ValueError("Probe requires four named descending outputs")
        incoming: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for edge in graph.edges:
            if edge.pair_synapses <= 0:
                raise ValueError("Probe requires positive anatomical pair counts")
            pre, post = graph.nodes[edge.pre_index], graph.nodes[edge.post_index]
            if not ((pre.role == "photoreceptor" and post.role == "OCG01") or
                    (pre.role == "OCG01" and post.role in {"DNp20", "DNp22"})):
                raise ValueError("Probe edge violates selected two-stage direction")
            incoming[edge.post_index].append((edge.pre_index, edge.pair_synapses))
        self._incoming: dict[int, tuple[tuple[int, float], ...]] = {}
        for index in (*self._relays, *self._outputs):
            parents = incoming[index]
            if not parents:
                raise ValueError("Probe relay or output is disconnected")
            total = sum(count for _, count in parents)
            self._incoming[index] = tuple((pre, count / total) for pre, count in parents)
        self.reset()

    def reset(self) -> None:
        self._rates = [0.0] * len(self.graph.nodes)

    def rates_snapshot(self) -> tuple[float, ...]:
        return tuple(self._rates)

    def step(self, observation: Mapping[str, float]) -> tuple[float, float, float, float]:
        if set(observation) != set(CHANNELS):
            raise ValueError("Probe requires exactly left, center, right inputs")
        values = {}
        for side in CHANNELS:
            raw = observation[side]
            if isinstance(raw, bool) or not isinstance(raw, (int, float)):
                raise ValueError("Probe input must be numeric")
            value = float(raw)
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError("Probe input must be finite in [0, 1]")
            values[side] = value
        old = self._rates
        new = list(old)
        for index in self._photos:
            new[index] = values[self.graph.nodes[index].side]
        for index in self._relays:
            drive = sum(weight * new[pre] for pre, weight in self._incoming[index])
            new[index] = (1 - self.alpha) * old[index] + self.alpha * drive
        for index in self._outputs:
            drive = sum(weight * old[pre] for pre, weight in self._incoming[index])
            new[index] = (1 - self.alpha) * old[index] + self.alpha * drive
        if not all(math.isfinite(value) and 0 <= value <= 1 for value in new):
            raise ValueError("Probe state became non-finite or out of range")
        self._rates = new
        return tuple(new[index] for index in self._outputs)
