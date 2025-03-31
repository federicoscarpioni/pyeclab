# pyeclab
 A Python wrapper around the EC-Lab SDK for the controll of BioLogic potentiostats

## Install

For usage in your project you can install this package with 

`pip install "pyeclab @ git+https://github.com/federicoscarpioni/pyeclab.git"` (Stable)


You can add the project to your dependencies by using:
```toml
dependencies = [
    "pyeclab @ git+https://github.com/federicoscarpioni/pyeclab.git", 
]
```

### TCL library
Don't use python version 3.13.0, as it has a bug with the location of the TCL-library. Python versions earlier/later are fine.

When needing to use it anyway or encoutering the bug in another config, the path can be specified as a env-variable (example for Windows):

`$env:TCL_LIBRARY="C:\Users\*USERNAME*\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"`


## Usage

A variety of examples can be found in the [examples folder](examples).

## Caveats

### External Control for essential devices

The xctr-parameters are not available for essential devices through the Developers package, even though they are available through EC-Lab.

### Safety limits

Safety limits as known from EC-Lab are not available through the Developer package.