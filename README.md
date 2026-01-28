
# Tk-DevTools 

## Currently still _IN DEVELOPMENT_ 

## Puprose
Use for getting and setting tkinter widget options and geometry while the app is running. Inspired by browser developer tools.

### Installing package builder
Windows

    py -m pip install --upgrade pip
    py -m pip install --upgrade build
    py -m build

Mac

    python3 -m pip install --upgrade pip
    python3 -m pip install --upgrade build
    python3 -m build

### Building the wheel

Packaging in source

    rm -rf build && rm -rf dist && rm -rf tk_devtools.egg-info && python -m build

Importing in local target

    pip uninstall /Users/chrisdielschnieder/code_work/python/tk-devtools/dist/tk_devtools-0.1.0-py3-none-any.whl && pip install /Users/chrisdielschnieder/code_work/python/tk-devtools/dist/tk_devtools-0.1.0-py3-none-any.whl