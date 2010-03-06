Lectori Salutem,

Venster is a small template library to build GUI windows applications
using only pure python and the win32 API.
The windows API is called trough the use of Thomas Hellers's
excelent ctypes module (http://ctypes.sourceforge.net).

The spirit of these components is about the same as that
of the Microsoft ATL and WTL libraries for C++. (e.g. low runtime
requirements, toolkit style, no doc/view paradigms etc).

It is still my believe that the best Windows Apps are build
using the RAW windows API using only small wrapper libraries such
as ATL or WTL.

The goals of this work are:

- make it possible to make good-looking (at least on par with what is possible with C++/WTL/Win32)
  python based windows applications

- with the least amount of run-time needed. What I mean by this is that a distribution version of
  such a python windows application would only need the PythonXX.dll and the ctypes dll + the 
  pyc sources of the app itself.
  If this is not the case than it would not make sense to build this gui lib 
  (just use .NET then, and distribute the 20mb runtime with it (or Java with its 10mb runtime))
  So small is really the key here


read INSTALL.TXT for installation instructions,
then go to the test folder and
 try any of the 

test_*.py files to see the results sofar.

Grtz,

Henk Punt (henk@entree.nl)


Venster is also made possible by the contributions and suggestions from:

Thomas Heller (theller@python.net)
Wim Vree (wim@vree.be)
Andrew MacIntyre (andrew.macintyre@aba.gov.au)
Brad Clements (bkc@murkworks.com)
Dave Brueck (dave@solussoftware.com)


