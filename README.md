# APDL-dcheck
APDL Dependency checker

## What can APDL-dcheck do for you?

APDL-dcheck is a simple deopendency checker for Macros written in ANSYS'(R) APDL scripting language. 
The program looks for /input and *use statements, parses them and tries to build a recursive dependency tree of your project. 
It also checks, whether the file specified and mentioned are available for the program. If not, the files are listed separately at the end of the output.
Additionally you can write a FreeMind-xml file, allowing you to show the dependency-tree in a more convenient ways than on the command-line.

