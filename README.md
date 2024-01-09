# NetSquid P4

[![pipeline
status](https://gitlab.tudelft.nl/qp4/netsquid-p4/badges/main/pipeline.svg)](https://gitlab.tudelft.nl/qp4/netsquid-p4/commits/main)
[![coverage
report](https://gitlab.tudelft.nl/qp4/netsquid-p4/badges/main/coverage.svg)](https://gitlab.tudelft.nl/qp4/netsquid-p4/commits/main)

## Introduction

This package provides NetSquid components for simulating networks that execute P4 pipelines.

## Pre-requisites

### NetSquid

This package requires [NetSquid](https://netsquid.org/) which requires a user account on its
[community forum](https://forum.netsquid.org/ucp.php?mode=register).

### PyP4

This package relies on [PyP4](https://github.com/QuTech-Delft/pyp4) to handle the core P4
processing.

### P4C

All P4 examples and test programs have been pre-compiled using the BMv2 backend and checked into the
repository. If you wish to compile your own programs, please use a suitable P4 compiler. The
[p4lang/p4c](https://github.com/p4lang/p4c) can compile the classical architectures, such as
V1model, provided by [PyP4](https://github.com/QuTech-Delft/pyp4). To compile custom architectures,
such as [V1Quantum](https://github.com/QuTech-Delft/v1quantum), you will need a suitable compiler
fork. Please refer to the documentation of the relevant architecture.

## Documentation

To view the documentation, run `make html` in the [docs](docs) directory and open
`docs/build/html/index.html`.

## Examples

This repository contains basic usage examples in the [examples](examples) directory.
