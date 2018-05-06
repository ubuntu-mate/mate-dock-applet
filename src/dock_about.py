#!/usr/bin/env python3
"""
Provide an about dialog for the MATE dock applet applet

The dialog displays the following:
    applet name and version number
    licensing info (GPL3)
    hints and tips
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
import config

if not config.WITH_GTK3:
    gi.require_version("Gtk", "2.0")
else:
    gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Pango


class AboutWindow(Gtk.Window):
    """Provides the About window

    """

    def __init__(self):
        """Init for the About window class

        Create the window and its contents
        """

        super().__init__(title="About Dock Applet")

        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_skip_taskbar_hint(True)  # we don't want to be in the taskbar

        self.__btn_close = Gtk.Button(label="Close", stock=Gtk.STOCK_CLOSE)
        self.__btn_close.connect("button-press-event", self.close_button_press)
        self.__btn_hints = Gtk.ToggleButton.new_with_label("Hints & Tips")
        self.__btn_hints.connect("toggled", self.hints_button_toggled)
        self.__btn_license = Gtk.ToggleButton.new_with_label("License")
        self.__btn_license.connect("toggled", self.license_button_toggled)

        self.connect("delete-event", self.win_delete_event)
        self.set_border_width(5)

        # use a notebook widget to display the various pages of info
        self.__nb = Gtk.Notebook()
        self.__nb.set_show_tabs(False)
        self.__nb.set_show_border(False)

        # create a container for the dialog and others for the pages of the notebook
        if not config.WITH_GTK3:
            self.__vbox = Gtk.VBox()
            self.__vbox.set_spacing(2)
            self.__vbox_dflt = Gtk.VBox()
            self.__vbox_dflt.set_spacing(8)
            self.__vbox_license = Gtk.VBox()
            self.__vbox_license.set_spacing(8)
        else:
            self.__vbox = Gtk.Box()
            self.__vbox.set_orientation(Gtk.Orientation.VERTICAL)
            self.__vbox.set_spacing(4)

            self.__vbox_dflt = Gtk.Box()
            self.__vbox_dflt.set_orientation(Gtk.Orientation.VERTICAL)
            self.__vbox_dflt.set_spacing(8)

            self.__vbox_license = Gtk.Box()
            self.__vbox_license.set_orientation(Gtk.Orientation.VERTICAL)
            self.__vbox_license.set_spacing(8)

        if not config.WITH_GTK3:
            self.__hbx = Gtk.HButtonBox()
        else:
            self.__hbx = Gtk.ButtonBox()
            self.__hbx.orientation = Gtk.Orientation.HORIZONTAL

        self.__hbx.set_layout(Gtk.ButtonBoxStyle.END)
        self.__hbx.set_spacing(4)
        self.__hbx.pack_start(self.__btn_hints, False, False, 4)
        self.__hbx.pack_start(self.__btn_license, False, False, 4)
        self.__hbx.pack_start(self.__btn_close, False, False, 4)

        self.__lbl_blank1 = Gtk.Label()
        self.__image = Gtk.Image()
        self.__image.set_from_stock(Gtk.STOCK_ABOUT, Gtk.IconSize.DIALOG)
        self.__lbl_title = Gtk.Label()
        self.__lbl_title.set_use_markup(True)
        if not config.WITH_GTK3:
            gtk_ver = "GTK2"
        else:
            gtk_ver = "GTK3"

        self.__lbl_title.set_markup("<b>MATE Dock Applet</b>")
        self.__lbl_ver = Gtk.Label("V" + config.VERSION +" (" + gtk_ver+ ")")
        self.__lbl_blank2 = Gtk.Label()

        self.__tb_gpl = Gtk.TextBuffer()
        self.__tag_size = self.__tb_gpl.create_tag("size")
        self.__tag_size.set_property("size-points", 9)
        iter_start = self.__tb_gpl.get_start_iter()

        self.__tb_gpl.insert_with_tags(iter_start,
                                       "MATE Dock Applet is free software; you can redistribute it and/or modify it " +
                                       "under the terms of the GNU General Public Licence as published by the Free " +
                                       "Software Foundation; either version 3 of the Licence, or (at your option) " +
                                       "any later version. \n\nMATE Dock Applet is distributed in the hope that it " +
                                       "will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty "+
                                       "of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General " +
                                       "Public Licence for more details.\n\nYou should have received a copy of the " +
                                       "GNU General Public Licence along with the applet; if not, write to the Free " +
                                       "Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA " +
                                       "02110-1301 USA\n",
                                       self.__tag_size)

        self.__tv_gpl = Gtk.TextView.new_with_buffer(self.__tb_gpl)
        self.__tv_gpl.set_wrap_mode(Gtk.WrapMode.WORD)
        self.__scrolled_win = Gtk.ScrolledWindow()

        self.__scrolled_win.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.__scrolled_win.add(self.__tv_gpl)

        self.__lbl_blurb1 = \
            Gtk.Label("A dock applet for the MATE desktop")
        self.__lbl_blurb2 = \
            Gtk.Label("This program comes with ABSOLUTELY NO WARRENTY")
        self.__lbl_blurb3 = Gtk.Label("and is distributed under the GNU General")
        self.__lbl_blurb4 = Gtk.Label("Public License, version 3 or later")

        if not config.WITH_GTK3:
            self.__hbx_gpl = Gtk.HBox()
        else:
            self.__hbx_gpl = Gtk.Box()
            self.__hbx_gpl.set_orientation(Gtk.Orientation.HORIZONTAL)
            self.__hbx_gpl.set_spacing(0)

        self.__lbl_gpl1 = Gtk.Label("For details click")
        self.__lb_gpl = \
            Gtk.LinkButton.new_with_label("http://www.gnu.org/licenses/gpl-3.0.html",
                                          "here")

        self.__hbx_gpl.pack_start(self.__lbl_gpl1, False, False, 0)
        self.__hbx_gpl.pack_start(self.__lb_gpl, False, False, 0)

        if not config.WITH_GTK3:
            self.__vbox_hints = Gtk.VBox()
        else:
            self.__vbox_hints = Gtk.Box()
            self.__vbox_hints.set_orientation(Gtk.Orientation.VERTICAL)

        # create widgets where where the hints text can be displayed...
        self.__hints_scrolled_win = Gtk.ScrolledWindow()
        self.__hints_scrolled_win.set_policy(Gtk.PolicyType.NEVER,
                                             Gtk.PolicyType.AUTOMATIC)
        self.__tv_hints = Gtk.TextView()
        self.__tv_hints.set_wrap_mode(Gtk.WrapMode.WORD)
        self.__tv_hints.set_editable(False)
        self.__hints_text_buf = Gtk.TextBuffer()
        self.__tag_hint_bold = self.__hints_text_buf.create_tag("bold",
                                                                weight=Pango.Weight.BOLD,
                                                                scale=1.0,
                                                                justification=Gtk.Justification.CENTER)
        self.__tag_hint_normal = self.__hints_text_buf.create_tag("normal")
        self.__tag_hint_normal.set_property("size-points", 9)

        self.__tv_hints.set_buffer(self.__hints_text_buf)
        self.set_hints_text()
        self.__hints_scrolled_win.add(self.__tv_hints)

        self.__vbox_dflt.pack_start(self.__lbl_ver, False, False, 0)
        self.__vbox_dflt.pack_start(self.__lbl_blank2, False, False, 0)
        self.__vbox_license.pack_start(self.__scrolled_win, True, True, 2)

        self.__vbox_hints.pack_start(self.__hints_scrolled_win, True, True, 0)

        self.__pg_dflt = self.__nb.append_page(self.__vbox_dflt)
        self.__pg_license = self.__nb.append_page(self.__vbox_license)
        self.__pg_hints = self.__nb.append_page(self.__vbox_hints)

        self.__vbox.pack_start(self.__lbl_blank1, False, False, 2)
        self.__vbox.pack_start(self.__image, False, False, 2)
        self.__vbox.pack_start(self.__lbl_title, False, False, 2)
        self.__vbox.pack_start(self.__nb, True, True, 2)
        self.__vbox.pack_end(self.__hbx, False, False, 2)

        self.add(self.__vbox)

        self.set_size_request(-1, 300)
  
    def set_hints_text(self):
        """ Sets the text which is to be displayed
        """

        the_iter = self.__hints_text_buf.get_end_iter()

        if config.WITH_GTK3:
            self.__hints_text_buf.insert_with_tags(the_iter,
                                               "Drag and drop data between applications\n",
                                               self.__tag_hint_bold)
            self.__hints_text_buf.insert_with_tags(the_iter, "\n""To easily drag and drop data from one application " +
                                               "to another, drag the data from the first application onto the dock " +
                                               "icon of the second application. The dock will activate the second " +
                                               "application's window, allowing the data to be dragged onto it. " +
                                               "Note: the second application must already be running.\n\n",
                                               self.__tag_hint_normal)
            self.__hints_text_buf.insert_with_tags(the_iter,
                                               "Adding new applications to the dock\n",
                                               self.__tag_hint_bold)
            self.__hints_text_buf.insert_with_tags(the_iter, "\n""Applications can be dragged and dropped from any menu " +
                                               "applet (i.e. the Main Menu, Menu Bar, Advanced Menu, or Brisk Menu) " +
                                               "directly onto the dock.\n\n",
                                               self.__tag_hint_normal)

        self.__hints_text_buf.insert_with_tags(the_iter,
                                               "Activating apps with keyboard shortcuts\n",
                                               self.__tag_hint_bold)
        self.__hints_text_buf.insert_with_tags(the_iter, "\n""Holding down the <Super> (i.e. Windows) and pressing " +
                                               "a number key will activate an app in the dock. For example, "+
                                               "pressing ""1"" will activate the first app, ""2"" the second etc. "+
                                               "Pressing ""0"" will activate the tenth app. To activate apps 11 to 20, "+
                                               "hold down the <Alt> key as well as <Super>.\n\n",
                                               self.__tag_hint_normal)

        self.__hints_text_buf.insert_with_tags(the_iter,
                                              "Opening a new instance of a running application\n",
                                              self.__tag_hint_bold)
        self.__hints_text_buf.insert_with_tags(the_iter, "\nTo quickly open a new instance of a running " +
                        "application either hold down the <shift> key while clicking the " +
                        "application's dock icon, or middle click on the icon." +
                         "\n\nNote: this works for most, but not all, apps.\n\n",
                                               self.__tag_hint_normal)

        self.__hints_text_buf.insert_with_tags(the_iter,
                                              "\nWindow switching using the mouse wheel\n",
                                              self.__tag_hint_bold)
        self.__hints_text_buf.insert_with_tags(the_iter,
                        "\nTo quickly switch between an application's open windows, move " +
                        "the mouse cursor over the apps's dock icon and use the mouse " +
                        "scroll wheel. This will activate and display each window in " +
                        "turn, changing workspaces as necessary.\n\n",
                                                self.__tag_hint_normal)

        self.__hints_text_buf.insert_with_tags(the_iter,
                                              "\nPanel colour changing\n",
                                              self.__tag_hint_bold)
        self.__hints_text_buf.insert_with_tags(the_iter, "\nWhen the applet sets the panel colour for the " +
                        "first time, the result may not look exactly as expected. This is " +
                        "because the default opacity of custom coloured MATE panels is set " +
                        "extremely low, so that the panel appears almost transparent.\n\nTo remedy " +
                        "this, simply right click the panel, select Properties and adjust the " +
                        "panel opacity as required.",
                                                self.__tag_hint_normal)

    def win_delete_event(self, widget, event, data=None):
        """Callback for the about window delete event

        Note: the window is not deleted, it is hidden instead so that it can
        be shown again if required later
        """

        self.hide()
        return True

    def close_button_press(self, widget, event):
        """
        callback for the Close button on the About dialog

        The window is hidden so that it can be shown again
        """

        self.hide()

    def license_button_toggled(self, widget):
        """
        callback for when the license button is toggled

        Show the license info if the license button is active, otherwise
        restore the main or credits info as appropriate

        Params:
            widget: the togglebuton

        """

        if self.__btn_license.get_active():

            self.__nb.set_current_page(self.__pg_license)
        else:
            if self.__btn_hints.get_active():
                self.__nb.set_current_page(self.__pg_hints)
            else:
                self.__nb.set_current_page(self.__pg_dflt)

    def hints_button_toggled(self, widget):
        """
        callback for when the credits button is toggled

        Show the credits info if the credits button is active, otherwise
        restore the main or license info as appropriate

        Params:
            widget: the togglebuton

        """

        if self.__btn_hints.get_active():
            self.__nb.set_current_page(self.__pg_hints)
        else:
            if self.__btn_license.get_active():
                self.__nb.set_current_page(self.__pg_license)
            else:
                self.__nb.set_current_page(self.__pg_dflt)


def main():
    """
    main function - debugging code goes here
    """

    about_dlg = AboutDialog()
    about_dlg.show_all()
    Gtk.main()

    return

if __name__ == "__main__":
    main()
