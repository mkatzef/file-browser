# file-browser

A file browser with the basic expected features, along with some less usual ones. Supported on Windows, MacOS and GNU/Linux. Written in Python, with a Tkinter GUI.

## Getting Started

This project consists of a single module.
* `FileBrowser.py` - The collection of classes providing file browser functionality along with the class which combines them.

### Prerequisites

To run file-browser, the host machine must have the following installed:
* `Python3` - The programming language in which file-browser was written. Available [here](https://www.python.org/).
* `Tkinter` - The Python library required for the file-browser user interface.\*

\*Included with the standard Python3 installation on Windows and MacOS, requires separate installation on Linux. For Debian-based systems, this is achieved through the following command:
`apt-get install python3-tk`

### Running

The file browser may be started by running the script as follows:
`python3 FileBrowser.py` 

### Use

For each file-browser function, the left-hand panel lists the contents of the current directory. Double clicking on an entry changes directory or opens the file.

On startup, the "General" tab is active, this may be changed by clicking on "Filenames" or "Subfolders". The functionality of each tab is described below.

#### General

The "General" tab provides the basic functionality of copy and paste, cut and paste, deletion and folder creation.

The "New Folder" button creates a new folder in the current directory. All other buttons act on the contents of the selection box (copying or moving selected items to the current directory). Items may be added to or removed from the selection by middle-mouse-clicking in either selection box.

#### Filenames

The "Filenames" tab allows files to be renamed in batches. This is achieved by searching for a given substring in all current filenames and replacing with the second substring.

#### Subfolders

The "Subfolders" tab provides a single, niche, function - it raises all items from children folders to the current directory before deleting the newly-emptied folders.

Please note, applications on MacOS are emptied like other directories.

## Authors

* **Marc Katzef** - [mkatzef](https://github.com/mkatzef)
