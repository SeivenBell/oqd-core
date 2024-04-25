
# Get started with the full stack

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
You will then need to add the package to your path using:

```bash
export PYTHONPATH=$PYTHONPATH:PATH-TO-PACKAGE
```
### Test <a name="test"></a>
For testing first install with pip:

```bash
pip install -e ".[test]"
```
The you can run the bash script below to run all unit tests:
```bash
bash tests/test.sh   
```

### Server <a name="server"></a>
The webserver is a [Uvicorn](https://www.uvicorn.org/) ASGI webserver with a [REST API](https://restfulapi.net/) defined with [Pydantic](https://docs.pydantic.dev/latest/) and [FastAPI](https://fastapi.tiangolo.com/). \
The webserver handles queuing jobs with a [Redis](https://redis.io/) cache and [Redis Queue (RQ)](https://python-rq.org/) worker.

#### Docker Compose <a name="docker-compose"></a>
Clone the repository using the following command :
```bash
git clone https://github.com/OpenQuantumDesign/quantumion
```
Deploy with docker compose:
```bash
cd docker
sudo docker compose up -d
```
By default, the webserver is deployed to:
```
http://{HOST_IP}:8000
```
Automatically generated API documentation can be found at:
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
```
http://{HOST_IP}:8000/docs
```
- [Redoc](https://redocly.com/redoc/)
```
http://{HOST_IP}:8000/redoc
```
## Getting Started <a name="Getting Started"></a>

To get started you can run one of the example scripts provided. For example, to run the 3 qubit GHz state protocol you can run:

```bash
python examples/experiments/three_qubit_ghz_state_preparation.py 
```

## Contents <a name="contents"></a>

### Frontends <a name="frontends"></a>
Python packages with [Pydantic](https://docs.pydantic.dev/latest/) support for each layer of the stack.

### Intermediate Representations <a name="intermediate-representations"></a>
The semantics defining an experiment for the different layers of the stack is defined by Backus-Naur Form (BNFs) in the following repos:
* [OpenQSIM](https://github.com/OpenQuantumDesign/openqsim)
* [OpenAPL](https://github.com/OpenQuantumDesign/openapl)

### Backends <a name="backends"></a>

#### Software <a name="software"></a>
Planned supported software backends include:

- Digital Circuit
    - [Tensor Circuit](https://github.com/tencent-quantum-lab/tensorcircuit)
    - [Yao.jl](https://yaoquantum.org/)

- Analog Circuit
    - [Qutip](https://qutip.org/)
    - [QuantumOptics.jl](https://docs.qojulia.org/search/?q=calcium)

- Trapped-ion Physics Simulator
    - [IonSim.jl](https://www.ionsim.org/)

#### Hardware <a name="hardware"></a>
Planned supported hardware backends include:

- [Quantum Information with Trapped-ions (QITI Lab)](https://qiti.iqc.uwaterloo.ca/publications/) Blade Trap $\left( ^{171}\mathrm{Yb}^+ \right)$
- [QuantumIon](https://tqt.uwaterloo.ca/project-details/quantumion-an-open-access-quantum-computing-platform/) $\left( ^{138}\mathrm{Ba}^+ \right)$


## Documentation <a name="documentation"></a>

Documentation is implemented with [MkDocs](https://www.mkdocs.org/) and can be read from the [docs](https://github.com/OpenQuantumDesign/quantumion/tree/main/docs) folder.

To install the dependencies for documentation, run:
```
pip install -e ".[docs]"
```
To deploy the documentation server locally:
```
mkdocs serve
```
After deployment, the documentation can be accessed from http://127.0.0.1:8000


## Acknowledgements <a name="acknowledgements"></a>

## References <a name="references"></a>
