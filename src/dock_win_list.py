#!/usr/bin/env python3
"""
    Provide a window showing a list of an app's open windows
    and also allow the user to select a window from the list and
    switch to it.

    Each item in the list will an indicator to show if the window
    is currently active, the window's title, and a close icon allowing
    the window to be closed.

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
gi.require_version("Bamf", "3")

from gi.repository import Gtk
from gi.repository import Wnck
from gi.repository import GdkPixbuf
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import Bamf

import os
import cairo
import tempfile
from time import sleep

from dock_popup import DockPopup
import window_control

from log_it import log_it as log_it

CONST_CLOSE_ICON_SIZE = 16
CONST_SEP = "--------------------"  # text which denotes tree view item is a separator
CONST_MAX_TITLE_WIDTH = 400         # max width of the title column in pixels
CONST__ACTIVE_TEXT = "•"


class DockWinList(DockPopup):

    """ Descendant of Dockup to provide a list of a running app's
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

        self.menu = None

        self.__bg_str = ""
        self.__fg_str = ""

        # we use a treeview to list each window, so initialise it and its
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

        # the list consists of open windows (click to select the window)
        # the liststore therefore needs to contain an active indictor,
        # window title/item text, a Bamf window, a GdxPixbuf
        # (an icon for the user to click to close the window,

        self.__list_store = Gtk.ListStore(str, str, GdkPixbuf.Pixbuf,
                                          Bamf.Window,
                                          GdkPixbuf.Pixbuf)

        self.__active_renderer = Gtk.CellRendererText()
        self.__icon_renderer = Gtk.CellRendererPixbuf()
        self.__title_renderer = Gtk.CellRendererText()
        self.__close_renderer = Gtk.CellRendererPixbuf()
        self.__close_renderer.set_alignment(1, 0.0)   # align to to topright of the cell

        # set default cell colours and padding
        self.__title_renderer.set_padding(2, 6)
        self.set_bg_col(32, 32, 32)

        # create columns for the treeview
        self.__col_icon = Gtk.TreeViewColumn("",
                                             self.__icon_renderer,
                                             pixbuf=4)

        self.__col_active = Gtk.TreeViewColumn("",
                                               self.__active_renderer,
                                               text=0)

        self.__col_active.set_sizing(Gtk.TreeViewColumnSizing.GROW_ONLY)
        self.__col_active.set_min_width(0)

        self.__col_title = Gtk.TreeViewColumn("",
                                              self.__title_renderer,
                                              text=1)
        self.__col_title.set_sizing(Gtk.TreeViewColumnSizing.GROW_ONLY)
        self.__col_title.set_expand(True)

        self.__col_title.set_max_width(CONST_MAX_TITLE_WIDTH)
        # assign an event handler to the title column so that we can use it
        # to display the active window title in bold text
        self.__col_title.set_cell_data_func(self.__title_renderer,
                                            self.draw_title)

        self.__col_title.set_sizing(Gtk.TreeViewColumnSizing.GROW_ONLY)

        self.__col_close = Gtk.TreeViewColumn("",
                                              self.__close_renderer,
                                              pixbuf=2)
        self.__col_close.set_sizing(Gtk.TreeViewColumnSizing.GROW_ONLY)
        self.__col_close.set_max_width(32)

        # add the columns
        self.__tree_view.set_model(self.__list_store)
        self.__tree_view.append_column(self.__col_icon)
        self.__tree_view.append_column(self.__col_title)
        self.__tree_view.append_column(self.__col_close)

        self.__tree_view.set_row_separator_func(self.check_sep)

        # add the treeview to the window
        self.set_main_widget(self.__tree_view)

        self.__tree_view.set_has_tooltip(True)
        self.__tree_view.connect("query-tooltip", self.query_tooltip)
        self.__tree_view.connect("button-release-event", self.button_release)
        self.__tree_view.connect("size-allocate", self.treeview_allocate)

        self.__pb_close = None
        self.__pb_active = None

    def create_close_pixbuf(self):
        """ Create a 'close' icon (based on the stock close icon) for use
            in the treeview
        """

        # create a pixbuf for holding the 'close' icon
        pb_close = self.render_icon(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU, None)

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                     CONST_CLOSE_ICON_SIZE,
                                     CONST_CLOSE_ICON_SIZE)
        ctx = cairo.Context(surface)
        Gdk.cairo_set_source_pixbuf(ctx, pb_close, 0, 0)
        ctx.paint()

        # we now need to copy the cairo surface to a pixbuf. The best way to do
        # this would be by calling GdkPixbuf.Pixbuf.new_from_data as in these
        #                                                 64)
        # comments. Unfortunately this function does not seem to be
        # introspectable (Gtk2) or not implemented yet (Gtk3) and therefore
        # doesn't work.
        #
        # self.__pb_close = GdkPixbuf.Pixbuf.new_from_data(surface.get_data(),
        #                                                 GdkPixbuf.Colorspace.RGB,
        #                                                 True, 8, pb_close.get_width(),
        #                                                 pb_close.get_height(),

        # Therefore we have to resort to writing the surface to a temporary
        # .png file and then loading it into our pixbuf ...

        handle, tempfn = tempfile.mkstemp()
        surface.write_to_png(tempfn)
        self.__pb_close = GdkPixbuf.Pixbuf.new_from_file(tempfn)
        os.remove(tempfn)

    def create_active_pixbuf(self):
        """ Create an active window icon (based on the stock forward icon) for
            use in the treeview

            See the comments in create-close-pixbuf
        """

        # create a pixbuf for holding the icon
        pb_active = self.render_icon(Gtk.STOCK_GO_FORWARD, Gtk.IconSize.MENU, None)

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                     CONST_CLOSE_ICON_SIZE,
                                     CONST_CLOSE_ICON_SIZE)
        ctx = cairo.Context(surface)
        Gdk.cairo_set_source_pixbuf(ctx, pb_active, 0, 0)
        ctx.paint()

        handle, tempfn = tempfile.mkstemp()
        surface.write_to_png(tempfn)
        self.__pb_active = GdkPixbuf.Pixbuf.new_from_file(tempfn)
        os.remove(tempfn)

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
        self.__bg_str = "#%.2x%.2x%.2x" % (r, g, b)
        r, g, b = self.fg_col
        self.__fg_str = "#%.2x%.2x%.2x" % (r, g, b)

        # now set the treeview colours
        self.__title_renderer.set_property("cell-background", self.__bg_str)
        self.__title_renderer.set_property("foreground", self.__fg_str)

        self.__active_renderer.set_property("cell-background", self.__bg_str)
        self.__active_renderer.set_property("foreground", self.__fg_str)

        self.__close_renderer.set_property("cell-background", self.__bg_str)
        self.__icon_renderer.set_property("cell-background", self.__bg_str)

    def query_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        """ Handler for the query-tooltip event to determine whether or not
            to show the 'Close window' tooltip

            If the tooltip was triggered by the keyboard, don't do anything

            Get the mouse coords, and if the mouse if located over the close
            icon show the tooltip

        Args:
            widget - the widget that received the event i.e. our treeview
            x - mouse x coord
            y - mouse y coord
            keyboard_mode - was the tooltip triggered by the keyboard?
            tooltip - the tooltip object that will be displayed

        Returns:
            True to display the tooltip, False otherwise
        """

        if keyboard_mode:
            return False

        return False
#        path, col, xrel, yrel = self.__tree_view.get_path_at_pos(x, y)

#        if col == self.__col_close:
#            cell_area = self.__tree_view.get_cell_area(path, col)
#            if (x >= cell_area.x + cell_area.width  - CONST_CLOSE_ICON_SIZE) and \
#               (y <= cell_area.y + CONST_CLOSE_ICON_SIZE):
#                tooltip.set_text("Close window")
#                return True
#            else:
#                return False
#        else:
#            return False

    def button_release(self, widget, event):
        """ Handler for the button release event

        If the middle or right mouse button was pressed, do nothing

        If the mouse button was released over the close icon, close the
        associated window

        If the mouse button was released over any other part of the tree view
        item, activate the associated  window

        Finally, hide the window list

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

        win = self.__list_store.get_value(sel_iter, 3)
        if (win is None) and (action is None):
            # this will allow e.g. an item to be added which just contains
            # the name of app, which can then be clicked to launch the app
            self.hide()
            self.the_app.start_app()
            return True

        if col == self.__col_close:
            cell_area = self.__tree_view.get_cell_area(path, col)
            if (event.x >= cell_area.x + cell_area.width - CONST_CLOSE_ICON_SIZE) and \
               (event.y <= cell_area.y + CONST_CLOSE_ICON_SIZE):
                window_control.close_win(win, event.time)
                self.hide()
                return True

        if win is not None:
            # if the window to be activated is not on the current workspace,
            # switchto that workspace
            wnck_win = Wnck.Window.get(win.get_xid())
            wnck_aws = self.wnck_screen.get_active_workspace()
            wnck_ws = wnck_win.get_workspace()

            # the windows's current workspace can be None if it is pinned to all
            # workspaces or it is not on any at all...
            # (fix for https://bugs.launchpad.net/ubuntu/+source/mate-dock-applet/+bug/1550392 and
            # https://bugs.launchpad.net/ubuntu-mate/+bug/1555336 (regarding software updater))
            if (wnck_aws is not None) and (wnck_ws is not None) and \
               (wnck_aws != wnck_ws):
                    wnck_ws.activate(0)
                    sleep(0.01)
            wnck_win.activate(0)

            # set the active indicator on the newly activated window
            # first, reset the current active indicator in the list store
            for list_item in self.__list_store:
                list_item[0] = ""
                list_item[4] = None

            # now set active indicator on the current item
            self.__list_store.set_value(sel_iter, 0, CONST__ACTIVE_TEXT)
            self.__list_store.set_value(sel_iter, 4, self.__pb_active)

            return True

        return True

    def add_separator(self):
        """ Convenience method to add a separator to the list

        If there are no items currently in the list then the separator
        won't be added
        """

        if len(self.__list_store) > 0:
            self.add_to_list(False, CONST_SEP, None)

    def add_to_list(self, is_active, title, window):
        """ Add an item to the window list

        Args:
            is_active - True if this is a window and it is active,
                         False otherwise
            title - the title of the window or the action
            window - the wnck window relating to the app (can be None)
        """

        # set the active indicator
        if is_active:
            active_text = CONST__ACTIVE_TEXT
        else:
            active_text = ""

        if active_text != "":
            app_icon = self.__pb_active
        else:
            app_icon = None

        if window is None:
            close_icon = None
        else:
            close_icon = self.__pb_close

        self.__list_store.append([active_text, title,
                                  close_icon, window,
                                  app_icon])

    def clear_win_list(self):
        """ Clear the list of open windows """

        self.__list_store.clear()

    def win_button_press(self, widget, event):
        """ this is for debug puposes only"""
        Gtk.main_quit()

    def setup_list(self, win_on_cur_ws_only):
        """ Setup the app list

        Set the app name

        Re-create the close icon in case the icon theme has changed

        For every window the app has open add an entry containing the app icon,
        window title, an indicator if the window is the active window, and a
        close icon

        Args:
            win_on_cur_ws_only : boolean - whether to show only windows which
                                 are on the current workspace, or show windows
                                 for all workspaces

        """

        self.create_close_pixbuf()
        self.create_active_pixbuf()

        # reduce the size of the window - it will autosize to fit the contents
        if not config.WITH_GTK3:
            self.__col_title.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
            self.__col_title.set_fixed_width(150)
            self.resize(100, 10)
            self.__col_title.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)

        win_list = self.the_app.get_windows()

        wnck_aws = self.wnck_screen.get_active_workspace()
        add_to_list = False
        for win in win_list:
            win_type = win.get_window_type()

            if (win_type == Bamf.WindowType.NORMAL) or (win_type == Bamf.WindowType.DIALOG):
                if win_on_cur_ws_only:
                    # only add if the window is on the current workspace
                    wnck_win = Wnck.Window.get(win.get_xid())
                    add_to_list = wnck_win.is_on_workspace(wnck_aws)
                else:
                    add_to_list = True

                if add_to_list:
                    is_active = (len(win_list) == 1) or \
                                (win == self.the_app.last_active_win)

                    self.add_to_list(is_active, win.get_name(), win)

    def mbutton_press(self, widget, event):
        """ this is for debug purposes only and demonstrates that menu.popup does
            not work with Gtk 2
        """

        self.menu = Gtk.Menu()
        menu_item = Gtk.MenuItem("A menu item")
        self.menu.append(menu_item)
        menu_item.show()

        self.menu.popup(None, None, None, event.button, event.time)

    def draw_title(self, column, cell_renderer, tree_model, tree_iter, data):
        title = tree_model.get_value(tree_iter, 1)
        if tree_model.get_value(tree_iter, 0) == CONST__ACTIVE_TEXT:
            cell_renderer.set_property('markup', "<b><i>%s</i></b>" % title)
        else:
            # if there is no window of action associatied with this item
            # it must be the name of a non running app. Format the title
            # differently if so...
            if (tree_model.get_value(tree_iter, 3) is None) and \
               (tree_model.get_value(tree_iter, 4) is None):
                cell_renderer.set_property('markup', "<b>%s</b>" % title)
            else:
                cell_renderer.set_property('markup', title)

    def check_sep(self, model, iter, data=None):
        """ Check to see if the current row is to be displayed as a separator

            Args :
                model : the treeview model (will be self.__list_store)
                iter : the roow in the model we're interested in
                data : user defined data

            Returns:
                Bool
        """

        title = model.get_value(iter, 1)
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
