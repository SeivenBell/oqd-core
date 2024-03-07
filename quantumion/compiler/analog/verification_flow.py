from typing import Any, List, Optional, Union, Dict

from abc import ABC, abstractmethod, abstractproperty

import functools

from pydantic import field_validator

########################################################################################

from quantumion.interface.base import TypeReflectBaseModel
from quantumion.compiler.visitor import Visitor
from quantumion.compiler.analog import *
from quantumion.compiler.math import *
from quantumion.compiler.analog.canonicalize import *
from quantumion.compiler.flow import *

########################################################################################

__all__ = [
    "VerificationFlow",
]


########################################################################################

class VerificationPauliAlgebraFlow(FlowGraph):
    nodes = [
        VerificationFlowGraphCreator(verify = CanonicalizationVerificationPauliAlgebra(),
                                        transformer = PauliAlgebra())(name="paulialgebra"),
        VerificationFlowGraphCreator(verify = CanonicalizationVerificationGatherMathExpr(),
                                        transformer = GatherMathExpr())(name="gathermathexpr"),
        VisitorFlowNode(visitor = CanonicalizationVerificationPauliAlgebra(), name="paulialgebra_verifier"),
        FlowTerminal(name="terminal"),
    ]
    rootnode = "paulialgebra"
    forward_decorators = ForwardDecorators()
    #### pauli algebra and nornal order need to be done just once. so we should make subgraphs for them
    @forward_decorators.forward_once(done="gathermathexpr")
    def forward_paulialgebra(self, model):
        pass

    @forward_decorators.forward_once(done="paulialgebra_verifier")
    def forward_gathermathexpr(self, model):
        pass

    @forward_decorators.catch_error(redirect="paulialgebra")
    @forward_decorators.forward_once(done="terminal")
    def forward_paulialgebra_verifier(self, model):
        pass

class VerificationNormalOrderFlow(FlowGraph):
    nodes = [
        TransformerFlowNode(visitor = NormalOrder(),name="normalorder"),
        VerificationFlowGraphCreator(verify = CanonicalizationVerificationOperatorDistribute(),
                                        transformer = OperatorDistribute())(name="distribute"),
        VerificationFlowGraphCreator(verify = CanonicalizationVerificationGatherMathExpr(),
                                        transformer = GatherMathExpr())(name="gathermathexpr"),
        VerificationFlowGraphCreator(verify = CanonicalizationVerificationProperOrder(),
                                        transformer = ProperOrder())(name="properorder"),
        VisitorFlowNode(visitor = CanonicalizationVerificationNormalOrder(), name = "normalorder_verifier"),
        FlowTerminal(name="terminal"),
    ]
    rootnode = "normalorder"
    forward_decorators = ForwardDecorators()
    #### pauli algebra and nornal order need to be done just once. so we should make subgraphs for them
    @forward_decorators.forward_once(done="distribute")
    def forward_normalorder(self, model):
        pass

    @forward_decorators.forward_once(done="gathermathexpr")
    def forward_distribute(self, model):
        pass

    @forward_decorators.forward_once(done="properorder")
    def forward_gathermathexpr(self, model):
        pass

    @forward_decorators.forward_once(done="normalorder_verifier")
    def forward_properorder(self, model):
        pass

    @forward_decorators.catch_error(redirect="normalorder")
    @forward_decorators.forward_once(done="terminal")
    def forward_normalorder_verifier(self, model):
        pass

class VerificationDistributionFlow(FlowGraph):
    nodes = [
        VerificationFlowGraphCreator(verify = CanonicalizationVerificationOperatorDistribute(),
                                        transformer = OperatorDistribute())(name="distribute"),
        VerificationFlowGraphCreator(verify = CanonicalizationVerificationGatherMathExpr(),
                                        transformer = GatherMathExpr())(name="gathermathexpr"),
        VisitorFlowNode(visitor = CanonicalizationVerificationOperatorDistribute(), name="distribution_verifier"),
        FlowTerminal(name="terminal"),
    ]
    rootnode = "distribute"
    forward_decorators = ForwardDecorators()
    @forward_decorators.forward_once(done="gathermathexpr")
    def forward_distribute(self, model):
        pass

    @forward_decorators.forward_once(done="distribution_verifier")
    def forward_gathermathexpr(self, model):
        pass

    @forward_decorators.catch_error(redirect="distribute")
    @forward_decorators.forward_once(done="terminal")
    def forward_distribution_verifier(self, model):
        pass


class VerificationFlow(FlowGraph):
    nodes = [
        VisitorFlowNode(visitor=VerifyHilbertSpace(), name="hspace"),
        VerificationDistributionFlow(name = "DistributionFlow"),
        VerificationFlowGraphCreator(verify = CanonicalizationVerificationProperOrder(),
                                        transformer = ProperOrder())(name="properorder"),
        VerificationPauliAlgebraFlow(name = "PauliAlgebraFlow"),
        VerificationFlowGraphCreator(verify = CanonicalizationVerificationGatherPauli(),
                                        transformer = GatherPauli())(name="gatherpauli"),
        VisitorFlowNode(visitor=CanonicalizationVerificationNormalOrder(),name="NormalOrderVerifier"),
        VerificationNormalOrderFlow(name = "NormalOrderFlow"),
        VerificationFlowGraphCreator(verify = CanonicalizationVerificationPruneIdentity(),
                                        transformer = PruneIdentity())(name="pruneidentity"),
        VerificationFlowGraphCreator(verify = CanonicalizationVerificationOperatorDistribute(),
                                        transformer = OperatorDistribute())(name="distribute_subtraction"),
        VerificationFlowGraphCreator(verify = CanonicalizationVerificationSortedOrder(),
                                        transformer = SortedOrder())(name="sortedorder"),
        FlowTerminal(name="terminal"),
    ]
    rootnode = "hspace"
    forward_decorators = ForwardDecorators()
    #### pauli algebra and nornal order need to be done just once. so we should make subgraphs for them
    @forward_decorators.forward_once(done="DistributionFlow")
    def forward_hspace(self, model):
        pass

    @forward_decorators.forward_once(done="properorder")
    def forward_DistributionFlow(self, model):
        pass

    @forward_decorators.forward_once(done="PauliAlgebraFlow")
    def forward_properorder(self, model):
        pass

    @forward_decorators.forward_once(done="gatherpauli")
    def forward_PauliAlgebraFlow(self, model):
        pass

    @forward_decorators.forward_once(done="NormalOrderVerifier")
    def forward_gatherpauli(self, model):
        pass

    @forward_decorators.catch_error(redirect="NormalOrderFlow")
    @forward_decorators.forward_once(done="pruneidentity")
    def forward_NormalOrderVerifier(self, model):
        pass

    @forward_decorators.forward_once(done="NormalOrderVerifier")
    def forward_NormalOrderFlow(self, model):
        pass

    @forward_decorators.forward_once(done="distribute_subtraction")
    def forward_pruneidentity(self, model):
        pass

    @forward_decorators.forward_once(done="sortedorder")
    def forward_distribute_subtraction(self, model):
        pass

    @forward_decorators.forward_once(done="terminal")
    def forward_sortedorder(self, model):
        pass