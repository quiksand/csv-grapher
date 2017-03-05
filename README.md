# CSV-GRAPHER

## Overview
CSV-GRAPHER is a utility for quickly graphing data in the .csv format. It automatically tries to graph all csv files in the current working directory, but has the option to add files form the GUI.

## Installation
The script will run out-of-the-box so long as you have python 3.x installed with the matplotlib and numpy libraries.

1. Install latest python (optional, if you already have python 3.x installed):
https://www.python.org/
2. Install matplotlib and numpy (optional, if you already have them):
In terminal or powershell:
```
pip install matplotlib
pip install numpy
```
3. Get the repo:
```
git clone https://github.com/quiksand/csv-grapher.git
```

## Usage
1. Move the csvcomp.py file to a directory with one or more csv files in it. This isn't strictly necessary, but recommended to avoid errors (see Known Issues and Limitations).
2. Run the file:
  * On Windows, just go ahead and double-click the csvcomp.py file to run.
  * On OSX/Linux run from the termianl:
  ```python3 csvcomp.py```
3. A GUI Window will open with your data graphed and a bunch of options to modify/export. Enjoy!

## Data
As it's impossible to predict how data will be sorted, I made the following assumptions about the format of the csv file:

1. Data is ordered in two or more columns, with x data in the first column and y data separated in all other columns.
2. All data should be numeric (or able to be interpreted as such), with the exception of title row(s).
3. Title rows will be stripped and used as data series labels.

## Known Issues and Limitations
These are mostly weird edge cases that I hope to fix down the line, but if you're having issues, look here first.

1. If all series are removed, weird things can happen to the legend/cursor. It's usually fixed by adding a new series.
2. Adding or removing a subplot with no series to graph will make program unhappy and it's probably best to restart.
3. Two-finger scrolling with a magic trackpad on Macbook Pros (and probably Mac desktops) whilst the cursor is in the GUI window will crash the program outright without warning. Handy if you're too lazy to mouse to the close button. Known limitation of the matplotlib backend integration with tk.
4. Large and/or many data sets will slow things down substantially, especially adding/removing subplots.
5. Standard matplotlib toolbar home/back/forward buttons may not work as expected after plot manipulation. (But won't break anything)
6. Some GUI elements are a bit ugly on Mac, and really ugly on Windows (cross-platform library my @$$). Working on it!
7. Currently limited to four subplots maximum.

## Inspiration & Development
This is one of those "necessity is the mother of invention" sort of things. I was tasked with generating multiple very large xy data sets in csv format, then graphing them in Excel against each other on a super slow computer, then doing it all over again, for days on end. It involved much copying and pasting from multiple files, and then really repetitive graphing. Those familiar with Excel know that it's cool and powerful, but not always the most fun to work with, especially when the end result is likely to be thrown away after analysis. So what did I do? What anyone would, of course! Spend many more hours automating a tedious but ultimately short-lived task. XKCD summed it up perfectly here: https://xkcd.com/1319/.

At first all it did was combine csv files in the working directory into one for easier excel graphing. (This made the task much less annoying)

Then it graphed them for me in matplotlib. (Right around this time I stopped having to do the original task)

Then there was a GUI for adding/removing plots and data series (Now I just needed a hobby)

Now I spend my time debugging and adding features to a program only I use, and only very occasionally (who am I kidding, this *is* my hobby)

In the future, I'll make it just generate a complete Excel file (or maybe someone will finally pay me to write code for a living and I'll do something else with my free time :) )

## Future Development
I am currently looking to wrap up the larger feature set, and put this on the back burner to go work on other things. That means there's going to be some bugs left over, but mostly just weird edge-case type stuff. I may come back to it if I continue needing to work with large data sets on slow computers.

## Contributing
Feel free to fork and hack away!

## License
MIT License

Copyright (c) 2017 Cody Schindler

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
