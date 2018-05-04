#!/usr/bin/env python3
"""
    Provide a window showing a list of an app's actions and allow the
    user to select one

    In addition to the actions defined in the app's .desktop file, a
    Pin/Unpin action will also be added as appropriate

    The window will function in a similar way to a tooltip i.e.
    it will appear when the mouse hovers over a dock icon and
    will disappear if the mouse moves away from the window or
    the dock applet.
"""

#
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

gi.require_version("MatePanelApplet", "4.0")

from gi.repository import Gtk
from gi.repository import Wnck
from gi.repository import GdkPixbuf
from gi.repository import Gio
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import MatePanelApplet
from gi.repository import Pango

from dock_popup import DockPopup

from log_it import log_it as log_it

CONST_MAX_TITLE_WIDTH = 300         # Max width of the action text
CONST_SEP = "--------------------"  # text which denotes tree view item is a separator


class DockActionList(DockPopup):

    """ Descendent of Dockup to provide a list of a running app's
        open windows

    """

    def __init__(self, wnck_screen, panel_orient, scroll_adj):
        """
        create the window and its contents

        Args:
            wnck_screen: the wnck_screen of the applet
            panel_orient : the orientation of the panel
            scroll_adj   : an adjustment to be applied to the window position
                           because the dock has scrolling enabled
        """

        # call the base classes constructor
        DockPopup.__init__(self, wnck_screen, panel_orient, scroll_adj)

        # we use a treeview to list each action, so initialise it and its
        # liststore
        self.__tree_view = Gtk.TreeView()

        if config.WITH_GTK3:
            self.__tree_view.set_valign(Gtk.Align.START)
            self.__tree_view.set_halign(Gtk.Align.START)
            self.__tree_view.hexpand = True
            self.__tree_view.vexpand = True

        self.__tree_view.set_headers_visible(False)

        # turn grid lines off, although they still seem to appear in some
        # themes e.g. Menta
        self.__tree_view.set_grid_lines(Gtk.TreeViewGridLines.NONE)

        self.__tree_view.set_hover_selection(True)

        # the liststore needs to contain an icon, the action text, and the
        # action itself
        self.__list_store = Gtk.ListStore(str, Gtk.Action, GdkPixbuf.Pixbuf)

        self.__icon_renderer = Gtk.CellRendererPixbuf()
        self.__title_renderer = Gtk.CellRendererText()

        # set default cell colours and padding
        self.__title_renderer.set_padding(2, 6)
        self.set_bg_col(32, 32, 32)

        # create columns for the treeview
        self.__col_icon = Gtk.TreeViewColumn("",
                                             self.__icon_renderer,
                                             pixbuf=2)

        self.__col_title = Gtk.TreeViewColumn("",
                                              self.__title_renderer,
                                              text=0)

        self.__col_title.set_sizing(Gtk.TreeViewColumnSizing.GROW_ONLY)
        self.__col_title.set_expand(True)

        self.__col_title.set_max_width(CONST_MAX_TITLE_WIDTH)
        self.__col_title.set_sizing(Gtk.TreeViewColumnSizing.GROW_ONLY)

        # add the columns
        self.__tree_view.set_model(self.__list_store)
        self.__tree_view.append_column(self.__col_icon)
        self.__tree_view.append_column(self.__col_title)
        self.__tree_view.set_row_separator_func(self.check_sep)

        # add the treeview to the window
        self.set_main_widget(self.__tree_view)

        self.__tree_view.connect("button-release-event", self.button_release)
        self.__tree_view.connect("size-allocate", self.treeview_allocate)

    def treeview_allocate(self, widget, allocation):
        """ Event handler for the tree view size-allocate event

        If the title column has expanded to its maximum width, ellipsize the
        title text...
        """

        if self.__col_title.get_width() == CONST_MAX_TITLE_WIDTH:
            self.__col_title.set_min_width(CONST_MAX_TITLE_WIDTH)
            self.__title_renderer.set_property("ellipsize",
                                               Pango.EllipsizeMode.END)

        self.__tree_view.get_selection().unselect_all()

    def set_colours(self, panel_colour):
        """ Sets the treeview colours (background, foreground and
            highlight) to match the window colours.

        Note : set_colours must have been called first so that
        the window colours are set correctly
        """

        DockPopup.set_colours(self, panel_colour)

        # set strings used to set widget colours - we can't change
        # the highlight colour, only foreground and background
        r, g, b = self.bg_col
        bg_str = "#%.2x%.2x%.2x" % (r, g, b)
        r, g, b = self.fg_col
        fg_str = "#%.2x%.2x%.2x" % (r, g, b)

        # now set the treeview colours
        self.__title_renderer.set_property("cell-background", bg_str)
        self.__title_renderer.set_property("foreground", fg_str)

        self.__icon_renderer.set_property("cell-background", bg_str)

    def get_num_rows(self):
        """ Returns the number of rows of data in the list store
        """

        return (self.__list_store.iter_n_children(None))

    def button_release(self, widget, event):
        """ Handler for the button release event

        If the middle or right mouse button was pressed, do nothing

        Otherwise, activate the selected item's action

        Hide the action list

        Args:

            widget : the widget the received the signal i.e. our treeview
            event  : the event parameters

        Returns:
            True: to stop any other handlers from being invoked
        """

        if event.button != 1:
            return False  # let other handlers run

        path, col, xrel, yrel = self.__tree_view.get_path_at_pos(event.x, event.y)
        sel_iter = self.__list_store.get_iter(path)

        action = self.__list_store.get_value(sel_iter, 1)
        title = self.__list_store.get_value(sel_iter, 0)
        if action is not None:
            self.hide()
            action.activate()

        return True

    def add_separator(self):
        """ Convenience method to add a separator to the list

        If there are no items currently in the list then the separator
        won't be added
        """

        if len(self.__list_store) > 0:
            self.add_to_list(CONST_SEP, None, False)

    def add_to_list(self, title, action, show_icon):
        """ Add an item to the action list

        Args:
            title - the title of the window or the action
            action - a GTK Action to be activated if the item is clicked
            show_icon - if True the app's icon will be shown alongside the
                        item in the list
        """

        if show_icon:
            app_icon = self.app_pb
        else:
            app_icon = None

        self.__list_store.append([title, action, app_icon])

    def clear_act_list(self):
        """ Clear the list of open windows """

        self.__list_store.clear()

    def win_button_press(self, widget, event):
        """ this is for debug puposes only"""
        Gtk.main_quit()

    def check_sep(self, model, iter, data=None):
        """ Check to see if the current row is to be displayed as a separator

            Args :
                model : the treeview model (will be self.__list_store)
                iter : the row in the model we're interested in
                data : user defined data

            Returns:
                Bool
        """

        title = model.get_value(iter, 0)
        return title == CONST_SEP


def main():
    """
    main function - debugging code goes here
    """

#    thewin = DockWinList()
#    thewin.set_app_name("Testing....")
#    thewin.add_to_list(None, False, "Win 1")
#    thewin.add_to_list(None, True, "Win 2 is active")
#    thewin.add_to_list(None, False, "Win 3")
#    thewin.show_all()

#    thewin.move(100, 110)
#    pos = thewin.get_position()
#    size = thewin.get_size()
#    print("pos %d %d" %(pos[0], pos[1]))
#    print("size %d %d" %(size[0], size[1]))
#    thewin.add_mouse_area(Gdk.Rectangle(pos[0]-15, pos[1]-15, size[0]+30, size[1]+30))
#    thewin.add_mouse_area(Gdk.Rectangle(0, 0, 48, 500))
#    thewin.add_mouse_area(Gdk.Rectangle(48, 110, 100, size[1]))
#    Gtk.main()
    return


if __name__ == "__main__":
    main()
