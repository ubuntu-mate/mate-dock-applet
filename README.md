# An application dock applet for the MATE panel

### Mate dock applet V0.80 on Solus OS, MATE edition
![V0.80 on Solus OS MATE edition](https://github.com/robint99/screenshots/blob/master/Solus%20and%20V.80.png)

The applet works with both GTK2 and GTK3 versions of MATE and allows you to:

* Place a dock on any MATE panel, of any size, on any side of the desktop you desire.
* Pin and unpin apps to the dock. Pinned apps can be shown in the dock on all workspaces or only the workspace where they were pinned (allowing the dock to be customised for each particular workspace).
* Rearrange application icons on the dock
* Launch apps by clicking on their icons in the dock
* Minimize/unminimize running app windows by clicking the app's dock icon
* Detect changes in the current icon theme and update the dock accordingly
* Use an indicator by each app to show when it is running
* Optionally, use multiple indicators for each window an app has open
* Use different styles of indicators, or turn indicators off altogether
* Change the colour of MATE panels to the dominant colour (i.e. the most common colour) of the desktop wallpaper. The colour can be applied to all panels or just the panel containing the dock.

## Installation

### Debian

The applet is available in Debian testing (currently GTK2 only):

`apt-get install mate-dock-applet`

### Ubuntu MATE 16.04 and later

The applet is included by default in Ubuntu MATE 16.04. It can be used by selecting the 'Mutiny' desktop layout in the MATE Tweak application, or by simply adding it to any panel.

Note: when upgrading from Ubuntu Mate 15.10 to 16.04 any previously installed version of the applet will be replaced with the one from the distribution's respositories.

### Linux Mint 19

The applet is not installed by default - `apt-get install mate-dock-applet` will do the trick...

### Linux Mint 18.2 and 18.3

The applet is included in the repositories but is compiled for Gtk2, rather than Gtk3. Therefore it will not work with the version of MATE desktop supplied with Linux Mint. Currently, the only solution is to manually compile and install the applet from source - instructions are further below. Note: the latest version of the applet which will work with the version of Gtk3 used in Linux Mint is V0.80 - souce code available [here](https://github.com/robint99/mate-dock-applet/archive/V0.81.tar.gz).

### Ubuntu MATE 15.10 and Linux Mint 18.1

Users of Ubuntu MATE 15.10 and earlier, or of Linux Mint 18.1 or earlier, can install the applet from the PPA kindly provided by [webupd8](http://www.webupd8.org/2015/05/dock-applet-icon-only-window-list-for.html)

Note: this is currently GTK2 only

### Arch Linux

For Arch users there are two packages available in the AUR, a [Gtk2](http://aur.archlinux.org/packages/mate-applet-dock-git) version of the applet, and a [Gtk3](http://aur.archlinux.org/packages/mate-applet-dock-gtk3-git) version.

### Gentoo based distributions

An ebuild is available via the [mate-de-gentoo](https://github.com/oz123/mate-de-gentoo)

### Other distributions

Users of other distros will need to install from source, so first install the required dependencies. Note, the package names below are for Ubuntu/Linux Mint/Debian - the name of the packages will vary on other distros.

* Python3
* Python wnck bindings (gir1.2-wnck-1.0 for Gtk2 versions of the applet, gir1.2-wnck-3.0 for Gtk3)
* Python implementation of Xlib - python-xlib (python3-xlib in Ubuntu based distributions)
* GLib development files (libglib2.0-dev)
* Python Imaging Library (python3-pil)
* Python 3 Cairo bindings (python3-cairo)
* Bamf (bamfdaemon, libbamf and gir1.2-bamf)


then cd to the directory containing all of the development files and run:

```
aclocal

automake --add-missing

autoreconf
```

To build a GTK2 version of the applet:
```
./configure --prefix=/usr
```

To build a GTK3 version:
```
./configure --prefix=/usr --with-gtk3
```

Then enter the following commands:
```
make

sudo make install
```

### Installation on Ubuntu MATE on a Pi 2

This is a little more involved. First download gir1.2-wnck-1.0 for arm architechure from [here](http://launchpadlibrarian.net/160438738/gir1.2-wnck-1.0_2.30.7-0ubuntu4_armhf.deb) and install it with sudo dpkg -i. Then install other dependencies - sudo apt-get install git autoreconf libglib2.0-dev

From this point the instructions above for compiling from source should be followed.

### Note for Compiz Users

In order for window minimizing and maximizing to work correctly under Compiz, the Focus Prevention Level setting must be set to off in CompizConfig Settings Manager (General Options, Focus and Raise Behaviour)

### Obligatory screen shots

V0.76 of the applet running on Ubuntu MATE 16.10, showing the new indicator style and active icon background. Note: the Gtk3 theme is Arc Darker (hence the blue indicators), and the icon theme is [La Capitaine](https://www.gnome-look.org/p/1148695/)

![New indicators and icon backgrounds](https://github.com/robint99/screenshots/raw/master/new%20indicators%20and%20icon%20background.png)

GTK3 version of the applet running on Ubuntu MATE 16.10 Alpha 1

![GTK3 Ubunbtu Mate](https://github.com/robint99/screenshots/raw/master/16.10%20win-list.png)

Running on Arch with a Unity style layout

![Arch screenshot](https://github.com/robint99/screenshots/raw/master/arch_V0.6_ss.png)

Running on Ubuntu with a Windows 7 style layout

![Ubuntu screenshot](https://github.com/robint99/screenshots/raw/master/Ubuntu_V0.6_ss.png)

Running on a Raspberry Pi 2 with Ubuntu MATE

![Pi2 screenshot](https://github.com/robint99/screenshots/raw/master/pi2_mate_V0.62_ss.png)
