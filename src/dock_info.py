#!/usr/bin/env python3
"""
Provide hints and tips dialog for the MATE dock applet

The applet displays the following:
        useful hints, tips, and information about use of the dock that
        may not be immediately apparent to the user
        a close button
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
#

# do not change the value of this variable - it will be set during build
# according to the value of the --with-gtk3 option used with .configure
import gi
from . import config

if not config.WITH_GTK3:
    gi.require_version("Gtk", "2.0")
else:
    gi.require_version("Gtk", "3.0")

import sys

from gi.repository import Gtk, Pango


class InfoWindow(Gtk.Window):
    """Provides the Info window"""

    def __init__(self, running_from_about=False):
        """Init for the Info window class

        Create the window and its contents

        Args:
            running_from_about - boolean, if True indicates that the window was
                                 invoked from the About dialog, and therefore
                                 there is no need to show info about how to
                                 show this window from the About dialog...
                                 (needed in case the window ever has to be
                                 invoked by a different method e.g. from the
                                 applet's right click menu)
        """

        super().__init__(title="Dock Applet hints, tips, and information")

        self.__rfa = running_from_about

        self.__button = Gtk.Button(label="Close", stock=Gtk.STOCK_CLOSE)
        self.__button.connect("button-press-event", self.win_button_press)
        self.set_border_width(5)

        if not config.WITH_GTK3:
            self.__vbox = Gtk.VBox()
        else:
            self.__vbox = Gtk.Box()
            self.__vbox.set_orientation(Gtk.Orientation.VERTICAL)
        self.__vbox.set_spacing(2)

        if not config.WITH_GTK3:
            self.__hbx = Gtk.HButtonBox()
        else:
            self.__hbx = Gtk.ButtonBox()
            self.__hbx.set_orientation = Gtk.Orientation.HORIZONTAL

        self.__hbx.set_layout(Gtk.ButtonBoxStyle.END)
        self.__hbx.pack_start(self.__button, False, False, 4)

        # create widgets where where the info text can be displayed...
        self.__scrolled_win = Gtk.ScrolledWindow()
        self.__scrolled_win.set_policy(Gtk.PolicyType.NEVER,
                                       Gtk.PolicyType.AUTOMATIC)
        self.__tv_info = Gtk.TextView()
        self.__tv_info.set_wrap_mode(Gtk.WrapMode.WORD)
        self.__tv_info.set_editable(False)
        self.__info_text_buf = Gtk.TextBuffer()
        self.__tag_bold = self.__info_text_buf.create_tag("bold",
                                                          weight=Pango.Weight.BOLD,
                                                          scale=1.3,
                                                          justification=Gtk.Justification.CENTER)
        self.__tv_info.set_buffer(self.__info_text_buf)
        self.set_info_text()
        self.__scrolled_win.add(self.__tv_info)

        self.__vbox.pack_start(self.__scrolled_win, True, True, 4)
        self.__vbox.pack_start(Gtk.HSeparator(), False, False, 2)
        self.__vbox.pack_end(self.__hbx, False, False, 5)
        self.add(self.__vbox)
        self.set_size_request(500, 300)

#        self.set_skip_taskbar_hint(True)
#        self.set_urgency_hint(True)

    def set_info_text(self):
        """ Sets the text which is to be displayed
        """

        the_iter = self.__info_text_buf.get_end_iter()
        self.__info_text_buf.insert_with_tags(the_iter,
                                              "Opening a new instance of a running application\n",
                                              self.__tag_bold)
        self.__info_text_buf.insert(the_iter, "\nTo quickly open a new instance of a running " +
                        "application either hold down the <shift> key while clicking the " +
                        "application's dock icon, or middle click on the icon." +
                         "\n\nNote: this works for most, but not all, apps.\n\n")

        self.__info_text_buf.insert_with_tags(the_iter,
                                              "\nWindow switching using the mouse wheel\n",
                                              self.__tag_bold)
        self.__info_text_buf.insert(the_iter,
                        "\nTo quickly switch between an application's open windows, move " +
                        "the mouse cursor over the apps's dock icon and use the mouse " +
                        "scroll wheel. This will activate and display each window in " +
                        "turn, changing workspaces as necessary.\n\n")

        self.__info_text_buf.insert_with_tags(the_iter,
                                              "\nPanel colour changing\n",
                                              self.__tag_bold)
        self.__info_text_buf.insert(the_iter, "\nWhen the applet sets the panel colour for the " +
                        "first time, the result may not look exactly as expected. This is " +
                        "because the default opacity of custom coloured MATE panels is set " +
                        "extremely low, so that the panel appears almost transparent.\n\nTo remedy " +
                        "this, simply right click the panel, select Properties and adjust the " +
                        "panel opacity as required.")

        if not self.__rfa:
            self.__info_text_buf.insert_with_tags(the_iter,
                        "\nClick the 'Hints & Tips' button on the applet 'About' dialog box "
                        "to see this information again.",
                        self.__tag_bold)

    def win_button_press(self, widget, event):
        """
        callback for the Ok button on the Info dialog

        The window is hidden so that it can be shown again
        """

        self.destroy()


def main():
    """
    main function - debugging code goes here
    """

    info_win = InfoWindow(True)
    info_win.show_all()
    Gtk.main()

    return

if __name__ == "__main__":
    main()
