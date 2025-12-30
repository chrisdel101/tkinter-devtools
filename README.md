### Notes

Packing

The packs where not making sense. Packing items inside a parent would make the parent show up. It took alot of time to fix this.
 
- So `left.pack` and `right.pack` were not being called on the window and yet were showing. 
- The right window needs to take both the entire list box and the root frame. This means the right window needs init, not listbox, then listbox init, then add the listbox to the right window.  
- For the `LeftWindowFrame` since it has the tree, and the tree was anchored to `root`, it showed when the tree was packed. I can't recall if this was required, but making it self seemed to fix that.

Dropdown

Used combobox to allow list and option for manual input. But combobox binds do not work as expected. `FosusOut` triggers when opening the combobox as well as at other unexpected times, so all focus logic has to be managed manually

- Combobox had not way to detect focus off - it first once open occured - so there was no way to close it without manually do it.
- CB would stay open on page flip. Only close was manually clicking it closed.
- CB had nice selected bind that gave the value easily, but the inability to close it on focus out made the page unusable.
- optionbox was almost just as bad. It finally allowed to detect an open on the box button, and with a bind on the window it could detect close.
- it might be enough to just use the focus out alone which would be very simple. 

### Installing package builder 

Windows

    py -m pip install --upgrade pip
    py -m pip install --upgrade build
    py -m build



Mac

    python3 -m pip install --upgrade pip
    python3 -m pip install --upgrade build
    python3 -m build

#### Building the wheel

Packaging in source

    rm -r dist && rm -r tk_devtools.egg-info && python -m build

Importing in local target

    pip uninstall /Users/chrisdielschnieder/code_work/python/tk-devtools/dist/tk_devtools-0.1.0-py3-none-any.whl && pip install /Users/chrisdielschnieder/code_work/python/tk-devtools/dist/tk_devtools-0.1.0-py3-none-any.whl