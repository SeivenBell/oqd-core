
# Open Quantum Design (OQD) Stack
This repo contains code for the frontend and backend of the OQD stack.

## Table of contents
- [Quick Start](#quickstart) <br/>
- [Installation](#installation) <br/>
  - [Client](#client) <br/>
  - [Server](#server) <br/>
     - [Docker Compose](#docker-compose) <br/>
- [Contents](#contents) <br/>
  - [Frontends](#frontends) <br/>
  - [Intermediate Representations](#intermediate-representations) <br/>
  - [Backends](#backends) <br/>
- [Documentation](#documentation) <br/>
- [Acknowledgements](#acknowledgements) <br/>
- [References](#references) <br/>



## Quick Start <a name="quickstart"></a>

## Installation <a name="installation"></a>

### Client <a name="client"></a>
Clone the repository using the following command :
```bash
git clone https://github.com/OpenQuantumDesign/quantumion
```
Install with pip :
```bash
pip install .
```

### Server <a name="server"></a>
The webserver is a [Uvicorn](https://www.uvicorn.org/) ASGI webserver with a [REST API](https://restfulapi.net/) defined with [Pydantic](https://docs.pydantic.dev/latest/) and [FastAPI](https://fastapi.tiangolo.com/). \
The webserver handles queuing jobs with a [Redis](https://redis.io/) cache and [Redis Queue (RQ)](https://python-rq.org/) worker.

#### Docker Compose <a name="docker-compose"></a>
```bash
cd docker
docker compose up -d
```

## Contents <a name="contents"></a>

### Frontends <a name="frontends"></a>

### Intermediate Representations <a name="intermediate-representations"></a>
The semantics defining an experiment for the different layers of the stack is defined by Backus-Naur Form (BNFs) in the following repos:
- [OpenQSIM](https://github.com/OpenQuantumDesign/openqsim)
- [OpenAPL](https://github.com/OpenQuantumDesign/openapl)

### Backends <a name="backends"></a>
Planned supported backends include:
- Digital Circuit
  - [Tensor Circuit](https://github.com/tencent-quantum-lab/tensorcircuit)
- Analog Circuit
  - [Qutip](https://qutip.org/)
- Trapped-ion Physics Experiment
  - [IonSim.jl](https://www.ionsim.org/)

## Documentation <a name="documentation"></a>

Currently unavaiable

## Acknowledgements <a name="acknowledgements"></a>

## References <a name="references"></a>
