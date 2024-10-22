# Copyright 2024 Open Quantum Design

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List

from oqd_compiler_infrastructure import TypeReflectBaseModel

########################################################################################

from .ion import Transition

########################################################################################

__all__ = [
    "Pulse",
    "Protocol",
]

########################################################################################


class Pulse(TypeReflectBaseModel):
    transition: Transition
    rabi: float
    detuning: float
    phase: float
    polarization: List[float]
    wavevector: List[float]
    targets: List[int]


class Protocol(TypeReflectBaseModel):
    pulses: List[Pulse]
