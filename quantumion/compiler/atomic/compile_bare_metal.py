#!/usr/bin/env python3
"""
Compile from the atomic representation to a working ARTIQ script (bare metal representation).
Compilation target is defined by a configuration that describes a DAX systme of a known format.
"""

from rich import print as pprint
from pydantic import BaseModel

from quantumion.compiler.atomic.base import AtomicCircuitTransformer
from quantumion.interface.atomic import *


PLANCK_CONSTANT = 6.62607015e-34 # J * s


class SimpleBeam(BaseModel):
    frequency: float
    target: int


class SimplePulse(BaseModel):
    beam: SimpleBeam
    duration: float


class AtomicToARTIQ(AtomicCircuitTransformer):

    def __init__(self) -> None:
        super().__init__()

    def visit_AtomicCircuit(self, model: AtomicCircuit):
        return self.visit_Protocol(model.protocol)

    def visit_Protocol(self, model: Protocol):
        actions = []
        for action in model.sequence:
            if isinstance(action, Protocol):
                actions.append(self.visit_Protocol(action))
            elif isinstance(action, Pulse):
                actions.append(self.visit_Pulse(action))
            else:
                raise ValueError(f"Action of type {type(action)} in Protocol. Must be of type Protocol or Pulse.")
        return actions

    def visit_Pulse(self, model: Pulse):
        beam = self.visit_Beam(model.beam)
        return SimplePulse(beam=beam, duration=model.duration)

    def visit_Beam(self, model: Beam):
        frequency = self.visit_Transition(model.transition)
        return SimpleBeam(frequency=frequency, target=model.target)

    def visit_Transition(self, model: Transition):
        return (model.level2.energy - model.level1.energy) / PLANCK_CONSTANT

if __name__ == "__main__":
    pass