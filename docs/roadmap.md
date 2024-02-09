## Technical milestones for top-layer stack components
1. Spec and source Sinara system for testbench (clone of QuantumION control stack).
2. Cloud provider with authentication, queueing, and multiple classical emulators.
3. Fix analog and atomic IR specifications at version 0.1.
4. Develop initial compiler infrastructure to lower analog -> atomic, atomic -> DAX/ARTIQ.
5. Express monitored quantum circuit in IRs, run with classical emulation.
6. Evaluate prototype programs on testbench Sinara hardware.
7. Good documentation and unit tests.

```mermaid
gantt
    dateFormat  YYYY-MM
    title       Open Quantum Design: Technical roadmap, top stack layers
    %% (`excludes` accepts specific dates in YYYY-MM-DD format, days of the week ("sunday") or "weekends", but not the word "weekdays".)

    section Testbench installation
    Spec. Sinara                        :spec, 2024-02-01, 2w
    Lead time                           :leadtime, after spec, 6w
    Installation                        :install, after leadtime, 4w
    Testing and development             :after install, 32w
    
    section Cloud provider
    User authorization, tokens                              :auth, 2024-03-01, 4w
    Install in Perimeter Institute                          :installcloud, after auth, 8w
    Beta-testing of install cloud infrastructure            :testcloud, after installcloud, 12w
    
    section Intermediate representations
    Time-dependence                                         :timedep, 2024-02-01, 3w
    Analog layer, dissipation rep.                          :diss, after timedep, 8w
    Analog layer, register addressing functionality         :addr, after timedep, 12w
    
    section Compilers
    Learn and sandbox visitor pattern  :visitor, 2024-02-01, 2w
    Canonical, verify, and transform visitors for analog -> atomic lowering (version 0.0.1)      :canon, after visitor, 12w
    Use visitors in backend classical analog emulators             :em_visit, after canon, 12w 
    
    section Use-case development
    Bang-bang protocols    :qaoa, 2024-02-01, 8w
    Annealing experiments  :anneal, after qaoa, 8w
    AMO and MB problems    :amomb, after anneal, 16w
    Mid-circuit measurements   :mcm, after amomb, 24w
    
    section Documentation
    Maintain, add docstrings                       :2024-02-01, 52w
    Develop tutorials and examples                 :2024-06-01, 8w
    Unit tests                                     :2024-02-01, 52w
```