# Pubchem Lookup
A simple GUI utility for retrieving basic stats of compounds or molecules on the PubChem database. 

## Getting Started
The program requires a few dependencies be installed in order to properly run for development/testing/use, which will be discussed here.

### Prerequisites
This program was developed in Python 3.7.1 and requires a version of Python 3 to be installed in some form in order to run. Python downloads are available [here](https://www.python.org/downloads/).

### Python Dependencies
A few various Python libraries are used in the program, which also must be installed. Pip can be used to install these modules, and is included with Python version 3.4 or newer. The following libraries are used in this program:
 * [tkinter](https://docs.python.org/3/library/tkinter.html) - used for developing the GUI
 * [pillow](https://pillow.readthedocs.io/en/stable/) - used for displaying the .png image retrieved from PubChem
 * [requests](https://2.python-requests.org/en/master/) - used to retreive data from the PUG REST API
 * [json](https://docs.python.org/3/library/json.html) - used to parse data retreived from the API
 * [traceback](https://docs.python.org/3.7/library/traceback.html) - used to display errors that may arise from improper input
 * [os](https://docs.python.org/3/library/os.html) - used to remove a temporary image file created in program runtime

The following libraries can be installed with pip using the following syntax (using tkinter as an example):
```
pip3 install tkinter
```

## Use
Once all dependencies are accounted for, the program can then be ran. The program can be opened from the command line using the following command, which assumes the terminal is currently in the directory/folder in which the file resides and than python has been added to the global path variable.
```
python PubchemLookup.py
```
