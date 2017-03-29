## Install

Make sure you have a [recent version of Python](https://www.python.org/downloads/) installed. Either globally or in a [virtual environment](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/) (don't worry if you don't know what that means), from a command line where you can run pip (check ``pip --version``):

``pip install pyexcel pyexcel-xls pyexcel-xlsx``

## Run

From a command line where you can run python (check ``python --version``):

``python -m frea_forms.py "some path\to some folder\with forms" -fd form_definitions.json``

Or, for more help:

``python -m frea_forms.py -h``

The ``form_definitions.json`` file has a full definition of the name and structure of supported forms. For each form definition, a .csv file will be written with the given name and all forms matching its key will be combined in this output file. 
