# Compilation

## Visitor

## Flow

=== "FlowNode"
    ```mermaid
    flowchart LR

    START:::hidden -- Input --> node(FlowNode) -- Output --> END:::hidden
    node -. Emission .-> MID:::hidden
    classDef hidden display: none;
    ```

=== "FlowGraph"
    ```mermaid
    flowchart LR

    
    START:::hidden -- Input --> node1(FlowNode 1) --> change1{Change} -- no --> node2(FlowNode 2) --> change2{Change} -- no --> terminal(Terminal) -- Output --> END:::hidden

    change1 -- yes --> node1
    node1 -. Emission .-> MID1:::hidden

    change2 -- yes --> node2
    node2 -. Emission .-> MID2:::hidden

    classDef hidden display: none;
    ```

### Forward Decorators
=== "Forward Once"
    ```python
    @ForwardDecorator.forward_once
    def forward_FN1(self, model):
        return dict(done="FN2")
    ```
    ```mermaid
    flowchart LR

    
    START:::hidden -- Input --> node1("FlowNode1<br/>(name: FN1)") --> node2("FlowNode2<br/>(name: FN2)") -- continue --> END:::hidden

    node1 -. Emission .-> MID1:::hidden

    classDef hidden display: none;
    ```
=== "Forward Fixed Point"
    ```python
    @ForwardDecorator.forward_fixed_point
    def forward_FN1(self, model):
        return dict(done="FN2")
    ```
    ```mermaid
    flowchart LR

    
    START:::hidden -- Input --> node1("FlowNode1<br/>(name: FN1)") --> change1{Change} -- no --> node2("FlowNode2<br/>(name: FN2)") -- continue --> END:::hidden
    
    change1 -- yes --> node1
    node1 -. Emission .-> MID1:::hidden

    classDef hidden display: none;
    ```
=== "Forward Detour"
    ```python
    @ForwardDecorator.forward_detour
    def forward_FN1(self, model):
        return dict(done="FN2", detour="FN3")
    ```
    ```mermaid
    flowchart LR

    
    START:::hidden -- Input --> node1("FlowNode1<br/>(name: FN1)") --> change1{Change} -- no --> node2("FlowNode2<br/>(name: FN2)") -- continue --> END:::hidden
    
    change1 -- yes --> node3("FlowNode3<br/>(name: FN3)") -- continue --> END2:::hidden
    node1 -. Emission .-> MID1:::hidden

    classDef hidden display: none;
    ```