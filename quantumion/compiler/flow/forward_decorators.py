from typing import List, Dict, Any

import functools

########################################################################################

from quantumion.interface.base import TypeReflectBaseModel
from quantumion.compiler.flow.flowout import FlowOut

########################################################################################

__all__ = [
    "ForwardError",
    "ForwardRule",
    "ForwardRules",
    "ForwardDecorators",
]

########################################################################################


class ForwardError(Exception):
    pass


########################################################################################


class ForwardRule(TypeReflectBaseModel):
    name: str
    decorators: List[str]
    destinations: Dict[str, str]

    class Config:
        validate_assignment = True


class ForwardRules(TypeReflectBaseModel):
    rules: List[ForwardRule] = []

    class Config:
        validate_assignment = True


########################################################################################


class ForwardDecorators:
    def __init__(self):
        self._rules = ForwardRules()

    @property
    def rules(self):
        return self._rules

    def update_rule(self, forward_rule):
        rules = self._rules.rules

        rule = next((rule for rule in rules if rule.name == forward_rule.name), None)
        if rule:
            decorators = rule.decorators
            destinations = rule.destinations

            decorators += forward_rule.decorators
            destinations.update(forward_rule.destinations)

            rule.decorators = decorators
            rule.destinations = destinations
        else:
            rule = forward_rule
            rules.append(rule)

        self._rules.rules = rules

    def forward_once(self, done):
        def _forward_once(method):
            self.update_rule(
                ForwardRule(
                    name=method.__name__,
                    decorators=[
                        "forward_once",
                    ],
                    destinations=dict(done=done),
                )
            )

            @functools.wraps(method)
            def _method(self, model: Any) -> FlowOut:
                flowout = self.namespace[self.current_node](model, self.traversal)

                self.next_node = done

                return flowout

            return _method

        return _forward_once

    def forward_fixed_point(self, done):
        def _forward_fixed_point(method):
            self.update_rule(
                ForwardRule(
                    name=method.__name__,
                    decorators=[
                        "forward_fixed_point",
                    ],
                    destinations=dict(done=done),
                )
            )

            @functools.wraps(method)
            def _method(self, model: Any) -> FlowOut:
                flowout = self.namespace[self.current_node](model, self.traversal)

                if model == flowout.model:
                    self.next_node = done
                else:
                    self.next_node = self.current_node

                return flowout

            return _method

        return _forward_fixed_point

    def forward_detour(self, done, detour):
        def _forward_detour(method):
            self.update_rule(
                ForwardRule(
                    name=method.__name__,
                    decorators=[
                        "forward_detour",
                    ],
                    destinations=dict(done=done, detour=detour),
                ),
            )

            @functools.wraps(method)
            def _method(self, model: Any) -> FlowOut:
                flowout = self.namespace[self.current_node](model, self.traversal)

                if model == flowout.model:
                    self.next_node = done
                else:
                    self.next_node = detour

                return flowout

            return _method

        return _forward_detour

    def forward_return(self):
        def _forward_return(method):
            self.update_rule(
                ForwardRule(
                    name=method.__name__,
                    decorators=[
                        "forward_return",
                    ],
                    destinations={},
                )
            )

            @functools.wraps(method)
            def _method(self, model: Any) -> FlowOut:
                try:
                    self.next_node = self.traversal.sites[-1].node
                except:
                    raise ForwardError(
                        "Previous site does not exist for forward_return."
                    )

                flowout = self.namespace[self.current_node](model, self.traversal)

                return flowout

            return _method

        return _forward_return

    def forward_branch_from_emission(self, key, branch):
        def _forward_branch_from_emission(method):
            self.update_rule(
                ForwardRule(
                    name=method.__name__,
                    decorators=[
                        "forward_branch_from_emission",
                    ],
                    destinations={
                        f"emission.{key}=={k}_branch": v for k, v in branch.items()
                    },
                )
            )

            @functools.wraps(method)
            def _method(self, model: Any) -> FlowOut:
                flowout = self.namespace[self.current_node](model, self.traversal)

                if isinstance(flowout.emission, dict):
                    emission_dict = flowout.emission
                else:
                    emission_dict = vars(flowout.emission)

                self.next_node = branch[emission_dict[key]]

                return flowout

            return _method

        return _forward_branch_from_emission

    def forward_branch_from_subgraph_exit(self, branch):
        def _forward_branch_from_subgraph_exit(method):
            self.update_rule(
                ForwardRule(
                    name=method.__name__,
                    decorators=[
                        "forward_branch_from_subgraph_exit",
                    ],
                    destinations={f"{k}_branch": v for k, v in branch.items()},
                )
            )

            @functools.wraps(method)
            def _method(self, model: Any) -> FlowOut:
                flowout = self.namespace[self.current_node](model, self.traversal)

                self.next_node = branch[
                    self.namespace[self.current_node].traversal.sites[-1].node
                ]

                return flowout

            return _method

        return _forward_branch_from_subgraph_exit

    def catch_error(self, redirect):
        def _catch_error(method):
            self.update_rule(
                ForwardRule(
                    name=method.__name__,
                    decorators=[
                        "catch_error",
                    ],
                    destinations=dict(redirect=redirect),
                )
            )

            @functools.wraps(method)
            def _method(self, model: Any) -> FlowOut:
                try:
                    flowout = method(self, model)
                    return flowout
                except Exception as e:
                    self.next_node = redirect
                    return FlowOut(model=model, emission=dict(error=e))

            return _method

        return _catch_error

    def catch_errors_and_branch(self, branch):
        def _catch_errors_and_branch(method):
            self.update_rule(
                ForwardRule(
                    name=method.__name__,
                    decorators=[
                        "catch_error_and_branch",
                    ],
                    destinations={f"{k.__name__}_branch": v for k, v in branch.items()},
                )
            )

            @functools.wraps(method)
            def _method(self, model: Any) -> FlowOut:
                try:
                    flowout = method(self, model)
                    return flowout
                except tuple(branch.keys()) as e:
                    self.next_node = branch[e.__class__]
                    return FlowOut(model=model, emission=dict(error=e))

            return _method

        return _catch_errors_and_branch
