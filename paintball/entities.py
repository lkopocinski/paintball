from dataclasses import dataclass
from typing import List


@dataclass
class LemmaActivations:
    lemma: str
    nodes: List
    activation: float


@dataclass
class Params:
    micro: float
    tau_0: float
    epsilon: float
    tau_3: float
    tau_4: float
