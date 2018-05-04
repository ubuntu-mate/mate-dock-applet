#!/usr/bin/env python3

"""
    Window control library

    Provide function to minimise, restore, activate etc. Bamf.Windows

"""
# Copyright (C) 1997-2003 Free Software Foundation, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# Author:
#     Robin Thompson

# do not change the value of this variable - it will be set during build
# according to the value of the --with-gtk3 option used with .configure
import gi
import config

if not config.WITH_GTK3:
    gi.require_version("Gtk", "2.0")
    gi.require_version("Wnck", "1.0")
else:
    gi.require_version("Gtk", "3.0")
    gi.require_version("Wnck", "3.0")

from gi.repository import Gtk, Wnck


def activate_win(win):
    """
    Activate the specified window

    Params:
        win : the Bamf.Window
    """
    event_time = Gtk.get_current_event_time()
    wnck_win = Wnck.Window.get(win.get_xid())
    if wnck_win is not None:
        wnck_win.activate(event_time)


def minimise_win(win):
    """
        Minimise the specified window

        Params:
            win : the Bamf.Window
        """

    wnck_win = Wnck.Window.get(win.get_xid())
    if wnck_win is not None:
        wnck_win.minimize()

def close_win(win, event_time=0):
    """
    Close the specified window

    Params:
        win : the Bamf.Window
        event_time : the event time to passed to wnck_win.close
    """

    wnck_win = Wnck.Window.get(win.get_xid())
    if wnck_win is not None:
        wnck_win.close(event_time)


# we need to know what adjustments to apply when calculating minimize positions,
# when  the dock has scrolling enabled and the variable below defines
# a callback which the dock can set in order to provide this info
# the callback should return four integers, the x and y adjustments to
# be applied to the minimise position, and the max width and height of the
# scrollable area, and a string - the panel orient

adj_minimise_pos_cb = None


def set_minimise_target(win, x, y, width, height):
    """
        Set the on-screen rectangle that a specified Bamf.Window will visibly
        minimize to

    Params:
        win     : the Bamf.Window
        x       : the x coordinate of the top left corner
        y       : the y coordinate of the top left corner
        width   : the width of the rectangle
        height  : the height of the ractangle

    """

    wnck_win = Wnck.Window.get(win.get_xid())
    if wnck_win is None:
        return

    if adj_minimise_pos_cb is not None:
        final_x, final_y = adj_minimise_pos_cb(x, y)
    else:
        final_x = x
        final_y = y

    win_type = wnck_win.get_window_type()
    if ((win_type == Wnck.WindowType.NORMAL) or
        (win_type == Wnck.WindowType.DIALOG)) and \
            (wnck_win.is_skip_tasklist() is False):
        wnck_win.set_icon_geometry(final_x, final_y, width, height)
