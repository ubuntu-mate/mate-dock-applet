# An application dock applet for the MATE panel

The applet allows you to:

* Place a dock on any MATE panel, of any size, on any side of the desktop you desire.
* Pin and unpin apps to the dock
* Rearrange application icons on the dock
* Launch apps by clicking on their icons in the dock
* Minimize/unminimize running app windows by clicking the app's dock icon
* Detect changes in the current icon theme and update the dock
	accordingly
* Use an indicator by each app to show when it is running
* Optionally, use multiple indicators for each window an app has open	
* Use either a light or dark indicator that it can always be seen no matter what colour the panel is

### Installation

To install from source, cd to the directory containing all of the development files and run:
	
./configure --prefix=/usr

make

sudo make install

### Dependencies
Depends on: 

Python3
gir1.2-wnck-1.0

### Obligatory screen shots

Running on Arch with a Unity style layout

![Arch screenshot](https://github.com/robint99/screenshots/raw/master/arch_V0.6_ss.png)

Running on Ubuntu with a Windows 7 style layout

![Ubuntu screenshot](https://github.com/robint99/screenshots/raw/master/Ubuntu_V0.6_ss.png)




