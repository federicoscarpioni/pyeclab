# pyeclab
 A Python wrapper around the EC-Lab SDK for the controll of BioLogic potentiostats

## Install

For usage in your project you can install this package with 

`pip install "pyeclab @ git+https://github.com/federicoscarpioni/pyeclab.git"` (Stable)

`pip install "pyeclab @ git+https://github.com/federicoscarpioni/pyeclab.git@refactoring"` (Development version)

You can add the project to your dependencies by using:
```toml
dependencies = [
    "pyeclab @ git+https://github.com/federicoscarpioni/pyeclab.git", 
]
```

### Notes

Don't use python version 3.13.0, as it has a bug with the location of the TCL-library. Python versions earlier/later are fine.

### np-rw-Buffer

Attention: np-rw-buffer will be removed in the future and replaced with a custom solution, as the package isn't maintained anymore.

The optional np-rw-ringbuffer dependency can be installed using the `[buffer]` dependency group, e.g. like this:


`pip install "pyeclab[buffer] @ git+https://github.com/federicoscarpioni/pyeclab.git"` 

You might need to add the following lines to you pyproject.toml when using hatchling:

```toml
[tool.hatch.metadata]
allow-direct-references = true
```

### TCL library

Matplotlib sometimes doesn't find the needed TCL-library, then it might be necessary to specify the path as env-variable, e.g.:

`$env:TCL_LIBRARY="C:\Users\*USERNAME*\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"`


## Caveats

### External Control for essential devices

The xctr-parameters are not available for essential devices through the Developers package, even though they are available through EC-Lab.