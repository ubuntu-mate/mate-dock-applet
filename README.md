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

Ubuntu and Mint users can install from the PPA kindly provided by [webupd8](http://www.webupd8.org/2015/05/dock-applet-icon-only-window-list-for.html)

For Arch users, there's a [package](http://aur.archlinux.org/packages/mate-applet-dock-git) in the AUR. 

Users of other distros will need to install from source, so cd to the directory containing all of the development files and run:

automake --add-missing

autoreconf	

./configure --prefix=/usr

make

sudo make install

### Installation on Ubuntu Mate on a Pi 2

This is a little more involved. First download gir1.2-wnck-1.0 for arm architechure from [here](http://launchpadlibrarian.net/160438738/gir1.2-wnck-1.0_2.30.7-0ubuntu4_armhf.deb) and install it with sudo dpkg -i. Then install other dependencies - sudo apt-get install git autoreconf libglib2.0-dev

From this point the instructions above for compiling from source should be followed.

### Dependencies

Depends on: 

Python3

gir1.2-wnck-1.0

### Obligatory screen shots

Running on Arch with a Unity style layout

![Arch screenshot](https://github.com/robint99/screenshots/raw/master/arch_V0.6_ss.png)

Running on Ubuntu with a Windows 7 style layout

![Ubuntu screenshot](https://github.com/robint99/screenshots/raw/master/Ubuntu_V0.6_ss.png)

Running on a Raspberry Pi 2 with Ubuntu MATE

![Pi2 screenshot](https://github.com/robint99/screenshots/raw/master/pi2_mate_V0.62_ss.png)

