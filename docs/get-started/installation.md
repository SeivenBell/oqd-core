# Installation

To install via `pip`,

```bash
pip install git+https://github.com/OpenQuantumDesign/midstack.git
```

To clone the repository locally:

```bash
git clone https://github.com/OpenQuantumDesign/midstack
```

Install the folder locally with `pip` and add to the

```bash
pip install .
export PYTHONPATH=$PYTHONPATH:PATH-TO-PACKAGE
```

### Documentation

Documentation is implemented with [MkDocs](https://www.mkdocs.org/) and can be read from the [docs](https://github.com/OpenQuantumDesign/midstack/tree/main/docs) folder.

To install the dependencies for documentation, run:

```
pip install -e ".[docs]"
```

To deploy the documentation server locally:

```
mkdocs serve
```

After deployment, the documentation can be accessed from [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Testing <a name="test"></a>

For testing first install with pip:

```bash
pip install -e ".[test]"
```

Then you can run the bash script below to run all unit tests:

```bash
bash tests/test.sh
```
