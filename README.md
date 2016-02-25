# APDL-dcheck
A tool to check the dependencies of [ANSYS (R) APDL](http://ansys.com) APDL script files.

## What can APDL-dcheck do for you?

`APDL-dcheck` is a simple dependency checker for Macros written in [ANSYS (R) APDL](http://ansys.com) scripting language. 
The program looks for `/input` and `*use` statements in your macro file, parses them and tries to build a recursive dependency tree of your project. 
It also checks whether the files specified and mentioned are available for the program. If not, the files are listed separately at the end of the output.
Additionally you can write a [FreeMind-xml](http://freemind.sourceforge.net/wiki/index.php/Main_Page) file, allowing you to show the dependency-tree in a more convenient way than on the command-line.

![Screenshot](https://github.com/Tatwaffe23mm/APDL-dcheck/blob/master/freemind-mindmap-screenshot.png "Screenshot of a mindmap")
