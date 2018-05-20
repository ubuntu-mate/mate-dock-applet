#!/usr/bin/env python3

"""Provide a dialog for the dock panel applet that allows
   a custom app launcher to be added to the dock.

   Note: This is primarily intended for apps that do not create
   a .desktop file, or get installed into non-standard locations

    Mimic the layout of the standard MATE custom launcher dialog,
    allowing the user to specify the following:
        App name
        The command used to launch the app
        The icon to be displayed in the dock
        A comment

    When the Ok button is clicked, a .desktop file will be created
    in the ~/.local/share/applications and its name will be in
    the format 'mda_<app_name>.desktop' to allow the applet
    to recognise and if necessary give priority to self
    created custom launchers
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
else:
    gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GdkPixbuf

import os


class DockCLWindow(Gtk.Window):
    """Class to provide the create custom launcher functionality

    Create and display the create custom launcher dialog

    Provide properties to get and set the custom launcher name,
    command, comment and icon
    """
    def __init__(self, ok_callback):
        """ Constructor for the custom launchr window

        Create the window and its contents and display them

        set the callback for the ok button press

        Args:
            ok_callback : the method to be called when the ok button is
                          is pressed

        """

        super().__init__(title="Create Launcher")

        self.set_skip_taskbar_hint(True)
        self.__icon_filename = ""

        self.connect("delete-event", self.win_delete_event)

        # setup the window contents
        self.set_border_width(5)

        if not config.WITH_GTK3:
            self.__hbox = Gtk.HBox()
            self.__vbox = Gtk.VBox()
        else:
            self.__hbox = Gtk.Box()
            self.__hbox.set_orientation(Gtk.Orientation.HORIZONTAL)
            self.__vbox = Gtk.Box()
            self.__vbox.set_orientation(Gtk.Orientation.VERTICAL)

        self.__hbox.set_spacing(2)
        self.__vbox.set_spacing(2)

        self.__btn_help = Gtk.Button(label="Help", stock=Gtk.STOCK_HELP)
        self.__btn_help.connect("button-press-event",
                                self.help_btn_press)
        self.__btn_cancel = Gtk.Button(label="Cancel", stock=Gtk.STOCK_CANCEL)
        self.__btn_cancel.connect("button-press-event",
                                  self.win_cancel_button_press)
        self.__btn_ok = Gtk.Button(label="Ok", stock=Gtk.STOCK_OK)
        self.__btn_ok.connect("button-press-event", ok_callback)

        if not config.WITH_GTK3:
            self.__hbox_btns = Gtk.HBox()
            self.__hbbx = Gtk.HButtonBox()
        else:
            self.__hbox_btns = Gtk.Box()
            self.__hbox_btns.set_orientation(Gtk.Orientation.HORIZONTAL)
            self.__hbbx = Gtk.ButtonBox()
            self.__hbbx.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.__hbbx.set_spacing(4)
        self.__hbbx.set_layout(Gtk.ButtonBoxStyle.END)

        self.__hbbx.pack_start(self.__btn_cancel, False, False, 4)
        self.__hbbx.pack_end(self.__btn_ok, False, False, 4)

        if not config.WITH_GTK3:
            self.__hbbx1 = Gtk.HButtonBox()
        else:
            self.__hbbx1 = Gtk.ButtonBox()
            self.__hbbx1.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.__hbbx1.set_spacing(4)
        self.__hbbx1.set_layout(Gtk.ButtonBoxStyle.START)
        self.__hbbx1.pack_start(self.__btn_help, False, False, 4)

        self.__hbox_btns.pack_start(self.__hbbx1, False, False, 0)
        self.__hbox_btns.pack_end(self.__hbbx, False, False, 0)

        self.__btn_icon = Gtk.Button()
        self.__img_icon = Gtk.Image()
        self.__btn_icon.connect("button_press_event", self.img_button_press)
        self.__btn_icon.set_tooltip_text("Click to select an icon")
        self.__btn_icon.add(self.__img_icon)

        if not config.WITH_GTK3:
            self.__vbox1 = Gtk.VBox()
        else:
            self.__vbox1 = Gtk.Box()
            self.__vbox1.set_orientation(Gtk.Orientation.VERTICAL)

        self.__vbox1.set_spacing(4)
        self.__vbox1.pack_start(self.__btn_icon, False, False, 4)

        if not config.WITH_GTK3:
            self.__table_layout = Gtk.Table(rows=4, columns=2,
                                            homogeneous=False)
        else:
            self.__table_layout = Gtk.Grid()
            self.__table_layout.set_column_spacing(2)
            self.__table_layout.set_row_spacing(2)

        self.__lbl_name = Gtk.Label()
        self.__lbl_name.set_use_markup(True)
        self.__lbl_name.set_label("<b>" + "Name:" + "</b>")
        self.__lbl_name.set_alignment(1, 0.5)

        self.__entry_name = Gtk.Entry()

        if not config.WITH_GTK3:
            self.__hbox_cmd = Gtk.HBox()
        else:
            self.__hbox_cmd = Gtk.Box()
            self.__hbox_cmd.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.__hbox_cmd.set_spacing(2)

        self.__lbl_cmd = Gtk.Label()
        self.__lbl_cmd.set_use_markup(True)
        self.__lbl_cmd.set_label("<b>" + "Command:" + "</b>")
        self.__lbl_cmd.set_alignment(1, 0.5)

        self.__entry_cmd = Gtk.Entry()
        self.__entry_cmd.set_width_chars(40)
        self.__btn_cmd = Gtk.Button(label="Browse...")
        self.__btn_cmd.connect("button-press-event", self.cmd_button_press)
        self.__hbox_cmd.pack_start(self.__entry_cmd, True, True, 0)
        self.__hbox_cmd.pack_end(self.__btn_cmd, False, False, 0)

        self.__lbl_term = Gtk.Label()
        self.__lbl_term.set_use_markup(True)
        self.__lbl_term.set_label("<b>" + "Run in terminal:" + "</b>")
        self.__lbl_term.set_alignment(1, 0.5)

        self.__cbtn_term = Gtk.CheckButton()
        self.__cbtn_term.set_alignment(1, 0.5)

        self.__lbl_comment = Gtk.Label()
        self.__lbl_comment.set_use_markup(True)
        self.__lbl_comment.set_label("<b>" + "Comment:" + "</b>")

        self.__entry_comment = Gtk.Entry()

        self.__lbl_wm_class = Gtk.Label()
        self.__lbl_wm_class.set_use_markup(True)
        self.__lbl_wm_class.set_label("<b>Window Class</b>")
        self.__entry_wm_class = Gtk.Entry()
        self.__entry_wm_class.set_sensitive(False)

        if not config.WITH_GTK3:
            self.__table_layout.attach(self.__lbl_name, 0, 1, 0, 1,
                                       Gtk.AttachOptions.SHRINK,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)
            self.__table_layout.attach(self.__entry_name, 1, 2, 0, 1,
                                       Gtk.AttachOptions.FILL |
                                       Gtk.AttachOptions.EXPAND,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)

            self.__table_layout.attach(self.__lbl_cmd, 0, 1, 1, 2,
                                       Gtk.AttachOptions.SHRINK,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)
            self.__table_layout.attach(self.__hbox_cmd, 1, 2, 1, 2,
                                       Gtk.AttachOptions.FILL |
                                       Gtk.AttachOptions.EXPAND,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)

        # Code below can be uncommented if adding terminal apps to the dock
        # ever becomes a needed thing
        # self.__table_layout.attach(self.__lbl_term, 0, 1, 2, 3,
        #                           Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.SHRINK,
        #                           2, 2)
        #
        # self.__table_layout.attach(self.__cbtn_term, 1, 2, 2, 3,
        #                           Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.SHRINK,
        #                           2, 2)

            self.__table_layout.attach(self.__lbl_comment, 0, 1, 2, 3,
                                       Gtk.AttachOptions.SHRINK,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)
            self.__table_layout.attach(self.__entry_comment, 1, 2, 2, 3,
                                       Gtk.AttachOptions.FILL |
                                       Gtk.AttachOptions.EXPAND,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)

            self.__table_layout.attach(self.__lbl_wm_class, 0, 1, 3, 4,
                                       Gtk.AttachOptions.SHRINK,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)
            self.__table_layout.attach(self.__entry_wm_class, 1, 2, 3, 4,
                                       Gtk.AttachOptions.FILL |
                                       Gtk.AttachOptions.EXPAND,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)
        else:
            self.__table_layout.attach(self.__lbl_name, 0, 0, 1, 1)
            self.__table_layout.attach(self.__entry_name, 1, 0, 1, 1)
            self.__table_layout.attach(self.__lbl_cmd, 0, 1, 1, 1)
            self.__table_layout.attach(self.__hbox_cmd, 1, 1, 1, 1)
            self.__table_layout.attach(self.__lbl_comment, 0, 2, 1, 1)
            self.__table_layout.attach(self.__entry_comment, 1, 2, 1, 1)
            self.__table_layout.attach(self.__lbl_wm_class, 0, 3, 1, 1)
            self.__table_layout.attach(self.__entry_wm_class, 1, 3, 1, 1)

        self.__hbox.pack_start(self.__vbox1, False, False, 0)
        self.__hbox.pack_end(self.__table_layout, True, True, 0)

        self.__vbox.pack_start(self.__hbox, True, True, 0)
        self.__vbox.pack_start(Gtk.HSeparator(), False, False, 4)
        self.__vbox.pack_end(self.__hbox_btns, False, False, 0)

        self.add(self.__vbox)
        self.set_default_values()
        self.show_all()

    def set_default_values(self):
        """ Set the window to its default state

        Clear all text entry fields
        Set the icon to Gtk.STOCK_EXECUTE
        """

        self.__img_icon.set_from_stock(Gtk.STOCK_EXECUTE, Gtk.IconSize.DIALOG)
        self.__entry_comment.set_text("")
        self.__entry_cmd.set_text("")
        self.__entry_name.set_text("")
        self.__entry_wm_class.set_text("")

    def win_delete_event(self, widget, event, data=None):
        """Callback for the preferences window delete event

        Do not delete the window, hide it instead so that it can be shown again
        later if needed

        """

        self.hide()
        return True

    def win_cancel_button_press(self, widget, event):
        """Callback for the preferences window Cancel button press

        Hide the window
        """
        self.hide()

    def set_cmd(self, cmd):
        """ Set the command line used by the launcher

        Args:
            cmd : the command line to use
        """

        self.__entry_cmd.set_text(cmd)

    def get_cmd(self):
        """ Get the command line used by the launcher

        Returns:
            A string containing the command line
        """

        return self.__entry_cmd.get_text()

    command = property(get_cmd, set_cmd)

    def cmd_button_press(self, widget, event):
        """Callback for the browse commands button

        Show a FileChooserDialog to allow the user to select a command to
        be associated with the laucher
        """

        fdc_cmd = Gtk.FileChooserDialog(title="Choose an application...",
                                        action=Gtk.FileChooserAction.OPEN)

        # set the working directory of the dialog
        cmd = self.get_cmd()
        if cmd is not None:
            path, filename = os.path.split(cmd)
            if path is not None:
                fdc_cmd.set_current_folder(path)

        btn_cancel = fdc_cmd.add_button(Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL)
        fdc_cmd.add_button(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        btn_cancel.grab_default()
        response = fdc_cmd.run()

        if response == Gtk.ResponseType.OK:
            self.set_cmd(fdc_cmd.get_filename())

        fdc_cmd.destroy()

    def set_icon_filename(self, filename):
        """ Set the filename of the icon to be used with the launcher
            and update the image on the icon selection button

        Args: filename  - the filename
        """

        pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
        pixbuf = pixbuf.scale_simple(48, 48, GdkPixbuf.InterpType.BILINEAR)
        self.__img_icon.set_from_pixbuf(pixbuf)
        self.__icon_filename = filename

    def get_icon_filename(self):
        """ Get the filename of the icon to be used with the launcher

        Returns: A string containing the filename
        """

        return self.__icon_filename

    icon_filename = property(get_icon_filename, set_icon_filename)

    def img_button_press(self, widget, event):
        """ Callback for the icon button press

        Show a FileChooserDialog allowing the user to select an icon for the
        launcher
        """

        fdc_icon = Gtk.FileChooserDialog(title="Choose an application...",
                                         action=Gtk.FileChooserAction.OPEN)

        ff_graphic = Gtk.FileFilter()
        ff_graphic.set_name("Image files")
        ff_graphic.add_pattern("*.svg")
        ff_graphic.add_pattern("*.png")
        ff_graphic.add_pattern("*.SVG")
        ff_graphic.add_pattern("*.PNG")
        ff_graphic.add_pattern("*.xpm")
        ff_graphic.add_pattern("*.XPM")
        fdc_icon.add_filter(ff_graphic)

        # set the working directory of the dialog
        icon_fn = self.get_icon_filename()
        if icon_fn is not None:
            path, filename = os.path.split(icon_fn)
            if path is not None:
                fdc_icon.set_current_folder(path)

        btn_cancel = fdc_icon.add_button(Gtk.STOCK_CANCEL,
                                         Gtk.ResponseType.CANCEL)
        fdc_icon.add_button(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        btn_cancel.grab_default()
        response = fdc_icon.run()

        if response == Gtk.ResponseType.OK:
            self.set_icon_filename(fdc_icon.get_filename())

        fdc_icon.destroy()

    def get_comment(self):
        """ Get the comment associated with the launcher

        Returns: string
        """

        return self.__entry_comment.get_text()

    def set_comment(self, comment):
        """ Set the comment associated with the launcher

        Args: comment  - a string containing the comment
        """

        self.__entry_comment.set_text(comment)

    comment = property(get_comment, set_comment)

    def get_name(self):
        """ Get the name associated with the launcher

        Returns: a string containing the name
        """

        return self.__entry_name.get_text()

    def set_name(self, name):
        """ Set the name associated with the launcher

        Args: name - a string
        """

        self.__entry_name.set_text(name)

    name = property(get_name, set_name)

    def get_wm_class(self):
        """ Get the window wm_class_name

        Returns: A string containing the wm_class_name
        """

        return self.__entry_wm_class.get_text()

    def set_wm_class(self, wm_class):
        """ Set the text of the launcher's wm_class entry widget

        Args:
            wm_class : The wm_class name
        """

        self.__entry_wm_class.set_text(wm_class)

    wm_class = property(get_wm_class, set_wm_class)

    def get_is_term(self):
        """ Gets whether or not the app is meant to be run in a terminal

        Returns: True if the app is to be run in a terminal, False otherwise
        """

        return self.__cbtn_term.get_active()

    def set_is_term(self, is_term):
        """ Sets whether or not the app is to be run in a terminal

        Args:
            is_term: boolean
        """

        self.__cbtn_term.set_active(is_term)

    is_terminal_app = property(get_is_term, set_is_term)

    def help_btn_press(self, widget, event):
        """ Event handler for the Help button press event

        Display an explanation of the usages of custom launchers in a dialog
        box
        """

        md = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL,
                               Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                               None)
        md.set_markup('<span size="x-large"><b>Custom Launchers</b></span>')
        info_text = "Custom launchers are an advanced feature meant to be used only with apps " +\
                    "that the dock does not recognise (i.e. they display the wrong name or icon). \n\n" + \
                    "Normally, this will only happen when the apps have been installed " + \
                    "to a non standard location within the file system, so for the vast majority of " + \
                    "apps this feature is not needed.\n\n" + \
                    "Note: if an app is running when a custom launcher is created for it, the app will " + \
                    "need to be closed and restarted for the dock to recognise it."

        md.format_secondary_text(info_text)
        md.run()
        md.destroy()


def main():
    """main function - debug code can go here"""
    dclw = DockCLWindow(Gtk.main_quit)
    dclw.set_skip_taskbar_hint(False)
    dclw.name = "My test launcher"
    dclw.comment = "This is a comment"
    dclw.icon_filename = "/usr/share/pixmaps/ericWeb.png"
    dclw.command = "/usr/bin/gvim"
    dclw.wm_class = "Dock_custom_launcher.py"
    dclw.is_terminal_app = False
    Gtk.main()

if __name__ == "__main__":
    main()
