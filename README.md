# Netsquid P4

[![pipeline
status](https://gitlab.tudelft.nl/qp4/netsquid-p4/badges/main/pipeline.svg)](https://gitlab.tudelft.nl/qp4/netsquid-p4/commits/main)
[![coverage
report](https://gitlab.tudelft.nl/qp4/netsquid-p4/badges/main/coverage.svg)](https://gitlab.tudelft.nl/qp4/netsquid-p4/commits/main)

## 3rd P4 Workshop in Europe (EuroP4)

This package was first presented as a demo at the 3rd P4 Workshop in Europe on 1 December 2020. The
extended abstract is available at:
- ACM DL: [A P4 Data Plane for the Quantum Internet](https://dl.acm.org/doi/10.1145/3426744.3431321)
- arXiv: [A P4 Data Plane for the Quantum Internet](https://arxiv.org/abs/2010.11263)

To explore the code and demo as it was when the demo was presented, please check out the
[`europ4-2020` in the original
repository](https://gitlab.com/softwarequtech/netsquid-snippets/netsquid-qp4/-/tree/europ4-2020) tag
and follow the `README.md` instructions therein.

## Introduction

This package provides NetSquid components for simulating networks that execute P4 pipelines.

## Pre-requisites

### NetSquid

This package requires [NetSquid](https://netsquid.org/) which requires a user account on its
[community forum](https://forum.netsquid.org/ucp.php?mode=register).

### PyP4

This package relies on [PyP4](https://gitlab.tudelft.nl/qp4/pyp4) to handle the core P4 processing.

### P4C

All P4 examples and test programs have been pre-compiled using the BMv2 backend and checked into the
repository. If you wish to compile your own programs, please use a suitable P4 compiler. The
[p4lang/p4c](https://github.com/p4lang/p4c) can compile the classical architectures, such as
V1model, provided by [PyP4](https://gitlab.tudelft.nl/qp4/pyp4). To compile custom architectures,
such as [PyP4-V1Quantum](https://gitlab.tudelft.nl/qp4/pyp4-v1quantum), you will need a suitable
compiler fork. Please refer to the documentation of the relevant architecture.

## Installation

### Normal build

To install base package dependencies (`<username>` and `<password>` are your NetSquid community
forum credentials)
```
NETSQUIDPYPI_USER=<username> NETSQUIDPYPI_PWD=<password> make python-deps
```

To install dependencies necessary for running examples
```
make example-deps
```

To install dependencies necessary for running unit tests
```
make test-deps
```

To run the tests
```
make tests
```

## Examples

This repository contains basic usage examples in the [examples](examples) directory.
