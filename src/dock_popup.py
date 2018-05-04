#!/usr/bin/env python3
"""
    Provide a base class for the dock's popup windows.

    Such a window will function in a similar way to a tooltip i.e.
    it will appear when the mouse hovers over a dock icon and
    will disappear if the mouse moves away from the window or
    the dock applet.

    The window's foreground/background colours will be set from the current
    theme or if the dock applet is setting the panel colour, the panel colours

    The will use a grid/table to display a border around the window contents,
    and descendant classes will need to create and set the window's
    main widget/container

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

build_gtk2 = False

import gi
if build_gtk2:
    gi.require_version("Gtk", "2.0")
    gi.require_version("Wnck", "1.0")
else:
    gi.require_version("Gtk", "3.0")
    gi.require_version("Wnck", "3.0")

gi.require_version("MatePanelApplet", "4.0")

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Gio
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import MatePanelApplet

import cairo
from time import sleep

import docked_app
from math import pi


CONST_TIMER_DELAY = 1000
CONST_ICON_SIZE = 16


class DockPopup(Gtk.Window):
    """

        Attributes : __mouse_areas : a list containing Gdk.Rectangle objects -
                     used when the window has been shown and defines the on
                     screen areas in which the mouse pointer must stay,
                     otherwise the window list will be hidden. The rectangles
                     should therefore include the applet, the area between
                     the window and the applet, and the window itself with a
                     suitable buffer area around it
            __timer_id : a ref to a timer used for periodically checking the
                         mouse cursor position to see if it is within the areas
                         specified in __mouse_areas
            __the_app : the docked_app to which the window list relates
            __icontheme : used for drawing app icons in the popup. This
                          is set from the Gtk.Icon used by the dock, and
                          will therefore track changes to the icon theme whilst
                          the dock is running
            __icon_size : the size in pixels at which app icons will be drawn

            __win_w : the width of the window
            __win_h : the height of the window
            __bgr, __bgg, __bgb : the r,g,b panel colour components (0-255)
            __fgr, __fgg, __fgb : the r,g,b foreground colour components
            __hlr, __hlg, __hlb : the r,g,b highlight colour components

            The attributes below are used for positioning this window relative
            to the applet and it's panel:
            __app_x : the x position of the docked app in root coordinates
            __app_y : the y position of the docked app in root coordinates
            __applet_x : the x position of the applet in root coordinates
            __applet_y : the y position of the applet in root coordinates
            __applet_w : the width of the applet in pixels
            __applet_h : the height of the applet in pixels
            __panel_orient : the orienation of the MATE panel the applet is on

            __do_window_shaping : whether or not the window can be shaped,
                                  e.g. have rounded corners. Depends on 
                                  Gtk3 and gi module >= 3.26.0
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

        def create_drawing_area(width, height, draw_event):
            # convenience func to create a drawing area with a specified
            # width, height and draw event
            da = Gtk.DrawingArea()
            da.set_size_request(width, height)
            if build_gtk2:
                da.connect("expose-event", draw_event)
            else:
                da.connect("draw", draw_event)

            return da

        super().__init__(title="")
        self.wnck_screen = wnck_screen
        self.set_decorated(False)  # we don't want a titlebar..
        self.set_skip_taskbar_hint(True)  # we don't want to be in the taskbar
        self.set_accept_focus(False)

        self.set_keep_above(True)

        self.__scroll_adj = scroll_adj
        self.__icontheme = None
        self.__icon_size = 16  # small default icon size
        self.__timer_id = None
        self.__dismissed = False

        self.__the_app = None
        self.__app_pb = None

        self.__win_w = 0
        self.__win_h = 0

        self.__app_x = 0
        self.__app_y = 0
        self.__panel_orient = panel_orient

        self.__bgr = 0
        self.__bgg = 0
        self.__bgb = 0
        self.__fgr = 0
        self.__fgg = 0
        self.__fgb = 0
        self.__hlr = 0
        self.__hlg = 0
        self.__hlb = 0
        self.__applet_x = 0
        self.__applet_y = 0
        self.__applet_w = 0
        self.__applet_y = 0
        self.__applet_h = 0

        # create ui
        if build_gtk2:
            self.__grid = Gtk.VBox()
            self.__grid.set_spacing(0)
            self.__grid = Gtk.Table(rows=3, columns=3)
            self.__grid.set_row_spacings(0)
            self.__grid.set_col_spacings(0)
        else:
            self.__grid = Gtk.Grid()
            self.__grid.set_orientation(Gtk.Orientation.VERTICAL)
            self.__grid.hexpand = True
            self.__grid.vexpand = True
            self.hexpand = True
            self.vexpand = True

        # set vars used when drawing the window border
        self.__border_width = 15
        self.__border_line = 4
        self.__line_width = 2
        self.__line_curve = 5.0
        self.__pointer_size = 16

        # add drawing areas to all outsides of the 3x3 grid
        # if we're showing shaped windows then the drawing area nearest the panel
        # needs to be expanded so that that portion of the window it can be shaped
        #  into a pointer to the app icon

        if build_gtk2:
            self.__do_window_shaping = False
        else:
            gi_ver = GObject.pygobject_version
            self.__do_window_shaping = gi_ver[0] > 3 or \
                                       ((gi_ver[0] == 3) and (gi_ver[1] >= 26))

        da_height = self.__border_width
        if self.__do_window_shaping and self.__panel_orient == MatePanelApplet.AppletOrient.DOWN:
            da_height += self.__pointer_size
        self.__da_top = create_drawing_area(self.__border_width,
                                            da_height,
                                            self.draw_top_border)

        da_width = self.__border_width
        if self.__do_window_shaping and self.__panel_orient == MatePanelApplet.AppletOrient.RIGHT:
            da_width += self.__pointer_size
        self.__da_left = create_drawing_area(da_width,
                                             self.__border_width,
                                             self.draw_left_border)

        da_width = self.__border_width
        if self.__do_window_shaping and self.__panel_orient == MatePanelApplet.AppletOrient.LEFT:
            da_width += self.__pointer_size
        self.__da_right = create_drawing_area(da_width,
                                              self.__border_width,
                                              self.draw_right_border)

        da_height = self.__border_width
        if self.__do_window_shaping and self.__panel_orient == MatePanelApplet.AppletOrient.UP:
            da_height += self.__pointer_size
        self.__da_bottom = create_drawing_area(self.__border_width,
                                               da_height,
                                               self.draw_bottom_border)

        if build_gtk2:
            self.__grid.attach(self.__da_top, 0, 3, 0, 1, xpadding=0,
                               ypadding=0)
            self.__grid.attach(self.__da_left, 0, 1, 1, 2)
            self.__grid.attach(self.__da_right, 2, 3, 1, 2)
            self.__grid.attach(self.__da_bottom, 0, 3, 2, 3)
        else:
            self.__grid.attach(self.__da_top, 0, 0, 3, 1)
            self.__grid.attach(self.__da_left, 0, 1, 1, 1)
            self.__grid.attach(self.__da_right, 2, 1, 1, 1)
            self.__grid.attach(self.__da_bottom, 0, 2, 3, 1)

        self.add(self.__grid)

        self.__mouse_areas = []

        # connect handlers for the show and hide events
        self.connect("show", self.win_shown)
        self.connect("hide", self.win_hidden)

        self.connect("configure-event", self.win_configure)
        self.connect("size-allocate", self.size_allocate)

    def set_main_widget(self, widget):
        """ Attaches the main component (a widget or container) to the center
            position of the grid

        Args:
            widget : the widget or container to add

        """
        if build_gtk2:
            self.__grid.attach(widget, 1, 2, 1, 2)
        else:
            self.__grid.attach(widget, 1, 1, 1, 1)

    def set_colours(self, panel_colour):
        """ Sets the window background, foreground and highlight colours
            to default values

        The background colour will match the panel containing the applet.

        If a custom colour is set for the panel, use that for the background
        and set the foreground colour to be either full white or black
        (depending on the background colour). The highlight colour will Also
        be set depending on the background colour.

        For Gtk3, if the panel is set to use the theme's colours, the
        background, foreground and  highilight colours will all be set from
        the current theme

        For Gtk2, where we can't access the styles associated with the current
        theme because of introspection errors, set the background to black,
        foreground to white and the highlight colour to a dark grey


        Args:
            panel_colour : If a custom panel colour has been set, this will
                           be a tuple of 3 x int - the r, g, b colour
                           components. Otherwise it will be None

        """

        if panel_colour is None:
            if build_gtk2:
                self.__bgr = self.__bgg = self.__bgb = 0
                self.__fgr = self.__fgg = self.__fgb = 255
                self.__hlr = self.__hlg = self.__hlb = 64
            else:

                context = self.get_style_context()
                state = Gtk.StateType.NORMAL
                # we want the colors for the MATE panel (preferably), or the
                # Gnome menu bar
                # context.add_class("gnome-panel-menu-bar")
                # context.add_class("mate-panel-menu-bar")

                # background
                c_info = context.lookup_color("dark_bg_color")
                if c_info[0]:
                    bgcol = c_info[1]
                    self.__bgr = int(bgcol.red * 255)
                    self.__bgg = int(bgcol.green * 255)
                    self.__bgb = int(bgcol.blue * 255)

                c_info = context.lookup_color("dark_fg_color")
                if c_info[0]:
                    fcol = c_info[1]
                    self.__fgr = int(fcol.red * 255)
                    self.__fgg = int(fcol.green * 255)
                    self.__fgb = int(fcol.blue * 255)

                sel_bg = context.lookup_color("theme_selected_bg_color")
                if sel_bg[0]:
                    hcol = sel_bg[1]
                    self.__hlr = int(hcol.red * 255)
                    self.__hlg = int(hcol.green * 255)
                    self.__hlb = int(hcol.blue * 255)
                else:
                    # assume what is hopefully a decent looking highlight
                    # colour
                    self.__hlr = (self.__bgr + 64) % 256
                    self.__hlg = (self.__bgg + 64) % 256
                    self.__hlb = (self.__bgb + 64) % 256
        else:
            # custom panel colour...
            self.__bgr = panel_colour[0]
            self.__bgg = panel_colour[1]
            self.__bgb = panel_colour[2]

            # set foreground colour according to the background colour
            # 384 equates to average rgb values of 128 per colour component and
            # therefore represents a mid value
            if (self.__bgr + self.__bgg + self.__bgb) > 384:

                self.__fgr = self.__fgg = self.__fgb = 0  # dark fg colour
            else:
                self.__fgr = self.__fgg = self.__fgb = 255  # light fg color

            # highlight colour
            self.__hlr = (self.__bgr + 64) % 256
            self.__hlg = (self.__bgg + 64) % 256
            self.__hlb = (self.__bgb + 64) % 256

    def set_bg_col(self, bgr, bgg, bgb):
        """ Sets the background colour of the window

        Also, set a foreground colour that will contrast with the background
        colour (so we can read text etc...)

        Args:
            bgr, bgg, bgb : the background rgb colour components

        """

        self.__bgr = bgr
        self.__bgg = bgg
        self.__bgb = bgb

        # set foreground colour according to the background colour
        if (bgr + bgg + bgb) > 384:     # 384 equates to average rgb values of 128
                                        # per colour component and therefore
                                        # represents a mid value
            self.__fgr = self.__fgg = self.__fgb = 0  # dark fg colour
        else:
            self.__fgr = self.__fgg = self.__fgb = 255  # light fg color

    def set_fg_col(self, fgr, fgg, fgb):
        """
        Put some stuff here...
        """

        self.__fgr = fgr
        self.__fgg = fgg
        self.__fgb = fgb

    def win_shown(self, widget):
        """ Event handler for the window's show event

            Get the window's size so that its position can be set and mouse
            areas created
        """

        if build_gtk2:
            self.set_win_position()
        else:
            if (self.__win_w == 0) or (self.__win_h == 0):
                self.__win_w, self.__win_h = self.get_size()

        self.start_mouse_area_timer()

    def set_win_position(self):
        """
            Move the window so that it appears near the panel and centered on
            the app (has to be done here for Gtk3 reasons)

            Create mouse areas as required so we can check when the mouse
            leaves the window

            Instantiate a timer to periodically check the mouse cursor position

        """

        def create_rect(x, y, w, h):
            """ Convenience function to create and return a Gdk.Rectangle
                (needed with Gtk3)
            """

            if build_gtk2:
                rect = Gdk.Rectangle(0, 0, 0, 0)
            else:
                rect = Gdk.Rectangle()

            rect.x = x
            rect.y = y
            rect.width = w
            rect.height = h

            return rect

        # set how many pixels away from the panel the window list will appear
        if self.__do_window_shaping:
            panel_space = 5
        else:
            panel_space = 10

        win_border = 15     # size of the border (in pixels) around the window
                            # list where the mouse must remain, outside of which
                            # the window list will hide

        screen = self.get_screen()

        # get the monitor that the applet is on
        # Note: we can't rely on the panel's dconf settings for this
        # as the monitor setting there doesn't seem to work reliably
        monitor = screen.get_monitor_at_point(self.__applet_x, self.__applet_y)
        if build_gtk2:
            mon_geom = create_rect(0, 0, 0, 0)
            screen.get_monitor_geometry(monitor, mon_geom)
        else:
            mon_geom = screen.get_monitor_geometry(monitor)

        # if the size of the window hasnt been set (because the configure-event
        # doesn't always fire if the window list is empty) use an alternative
        # method to get the window width and height
        # work out where to place the window - adjacent to the panel and
        #  centered on the highlighted dock app and add appropriate mouse areas

        # first, a mouse area to cover the entire applet
        self.add_mouse_area(create_rect(self.__applet_x, self.__applet_y,
                                        self.__applet_w, self.__applet_h))

        app_alloc = self.__the_app.drawing_area.get_allocation()

        if self.__panel_orient == MatePanelApplet.AppletOrient.RIGHT:
            centre_pos = self.__app_y + (app_alloc.height / 2) - self.__scroll_adj
            win_x = self.__applet_x + self.__applet_w + panel_space
            win_y = centre_pos - (self.__win_h/2)

            # adjust win_y in case we're off the top the screen, or the
            # monitor ...
            if win_y < mon_geom.y + panel_space:
                win_y = panel_space

            # adjust win_y if case the window list extends beyound the end of
            # the panel ..
            if (win_y + self.__win_h) > mon_geom.y + mon_geom.height:
                win_y = mon_geom.y + mon_geom.height - self.__win_h - panel_space

            # setup a new mouse area covering the window (minus a border) and
            # extending to the panel
            self.add_mouse_area(create_rect(self.__applet_x,
                                            win_y - win_border,
                                            win_x + self.__win_w + win_border,
                                            self.__win_h + (2*win_border)))

        elif self.__panel_orient == MatePanelApplet.AppletOrient.LEFT:
            centre_pos = self.__app_y + (app_alloc.height / 2) - self.__scroll_adj
            win_x = self.__applet_x - panel_space - self.__win_w
            win_y = centre_pos - (self.__win_h/2)

            # adjust win_y in case we're off the top the screen...
            if win_y < mon_geom.y + panel_space:
                win_y = mon_geom.y + panel_space

            # adjust win_y if case the window list extends beyound the end of
            # the panel ..
            if (win_y + self.__win_h) > mon_geom.y + mon_geom.height:
                win_y = mon_geom.y + mon_geom.height - self.__win_h - panel_space

            # setup a new mouse area covering the window (minus a border) and
            # extending to the panel
            self.add_mouse_area(create_rect(win_x - win_border,
                                            win_y - win_border,
                                            (self.__win_w + win_border +
                                             panel_space + app_alloc.width),
                                            self.__win_h + (2 * win_border)))

        elif self.__panel_orient == MatePanelApplet.AppletOrient.DOWN:
            centre_pos = (self.__app_x + app_alloc.width / 2) - self.__scroll_adj
            win_x = centre_pos - (self.__win_w / 2)
            win_y = self.__applet_y + self.__applet_h + panel_space

            # adjust win_x in case we're off the left of the screen...
            if win_x < mon_geom.x + panel_space:
                win_x = mon_geom.x + panel_space

            # adjust win_x if case the window list extends beyond the end of
            # the panel ..
            if (win_x + self.__win_w) > mon_geom.x + mon_geom.width:
                win_x = mon_geom.x + mon_geom.width - self.__win_w - panel_space

            # setup a new mouse area covering the window (minus a border) and
            # extending to the panel
            self.add_mouse_area(create_rect(win_x - win_border,
                                            self.__applet_y,
                                            self.__win_w + (2*win_border),
                                            win_y + self.__win_h + win_border))
        else:
            centre_pos = (self.__app_x + app_alloc.width / 2) - self.__scroll_adj
            win_x = centre_pos - (self.__win_w / 2)
            win_y = self.__applet_y - panel_space - self.__win_h

            # adjust win_x in case we're off the left of the screen...
            if win_x < mon_geom.x + panel_space:
                win_x = mon_geom.x + panel_space

            # adjust win_x if case the window list extends beyond the end of
            # the panel ..
            if (win_x + self.__win_w) > mon_geom.x + mon_geom.width:
                win_x = mon_geom.x + mon_geom.width - self.__win_w - panel_space

            # setup a new mouse area covering the window (minus a border) and
            # extendingto the panel
            self.add_mouse_area(create_rect(win_x - win_border,
                                            win_y - win_border,
                                            self.__win_w + (2*win_border),
                                            self.__win_h + win_border +
                                            panel_space + app_alloc.height))

        self.move(win_x, win_y)

    def start_mouse_area_timer(self):
        """ Start the timer that that monitors the mouse position
        """

        # remove any old timer...
        self.stop_mouse_area_timer()

        self.__timer_id = GObject.timeout_add(CONST_TIMER_DELAY, self.do_timer)

    def stop_mouse_area_timer(self):
        """ Stop the timer that monitors the mouse position
        """
        #
        if self.__timer_id is not None:
            GObject.source_remove(self.__timer_id)
            self.__timer_id = None

    def win_configure(self, widget, event):
        """ Event handler for the window's configure event

        Stores the new width and height of the window

        Args:
            widget : the widget that caused the event (i.e. self)
            event  : the event parameters
        """

        # if the new size of the window isn't the same as the old one, we need
        # to recaclulate the window position and mouse areas

        return

    def size_allocate(self, widget, event):

        def draw_rounded(cr, area, radius):
            """ draws rectangles with rounded (circular arc) corners """
            # Attribution: https://gist.github.com/kamiller/3013605

            a, b, c, d = area
            cr.arc(a + radius, c + radius, radius, 2 * (pi / 2), 3 * (pi / 2))
            cr.arc(b - radius, c + radius, radius, 3 * (pi / 2), 4 * (pi / 2))
            cr.arc(b - radius, d - radius, radius, 0 * (pi / 2), 1 * (pi / 2))  # ;o)
            cr.arc(a + radius, d - radius, radius, 1 * (pi / 2), 2 * (pi / 2))
            cr.close_path()

            cr.stroke_preserve()

        if (event.width != self.__win_w) or (event.height != self.__win_h):
            self.__win_w = event.width
            self.__win_h = event.height

            self.set_win_position()

        if not self.__do_window_shaping:
            return

        # round the corners of the portion of the window containing the widget and border
        allocation = self.get_allocation()

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                     allocation.width,
                                     allocation.height)

        ctx = cairo.Context(surface)

        if self.__panel_orient == MatePanelApplet.AppletOrient.UP:
            draw_rounded(ctx, [allocation.x, allocation.width,
                               allocation.y, allocation.height - self.__pointer_size], 10)
        elif self.__panel_orient == MatePanelApplet.AppletOrient.DOWN:
            draw_rounded(ctx, [allocation.x, allocation.width,
                               allocation.y + self.__pointer_size,
                               allocation.height], 10)
        elif self.__panel_orient == MatePanelApplet.AppletOrient.RIGHT:
            draw_rounded(ctx, [self.__pointer_size + 1, allocation.width,
                               allocation.y, allocation.height], 10)
        else:
            draw_rounded(ctx, [allocation.x, allocation.width - self.__pointer_size,
                               allocation.y, allocation.height], 10)

        ctx.set_source_rgba(1, 1, 1, 1)

        ctx.fill()

        # now create a pointer to the app's icon in the dock
        if self.__panel_orient == MatePanelApplet.AppletOrient.UP:
            ctx.move_to(allocation.width / 2 - self.__pointer_size,
                        allocation.height - self.__pointer_size)
            ctx.line_to(allocation.width / 2, allocation.height)
            ctx.line_to(allocation.width / 2 + self.__pointer_size,
                        allocation.height - self.__pointer_size)
        elif self.__panel_orient == MatePanelApplet.AppletOrient.DOWN:
            ctx.move_to(allocation.width / 2 - self.__pointer_size,
                        self.__pointer_size)
            ctx.line_to(allocation.width / 2, 0)
            ctx.line_to(allocation.width / 2 + self.__pointer_size,
                        self.__pointer_size)
        elif self.__panel_orient == MatePanelApplet.AppletOrient.RIGHT:
            ctx.move_to(self.__pointer_size,
                        allocation.height / 2 - self.__pointer_size)
            ctx.line_to(0, allocation.height / 2)
            ctx.line_to(self.__pointer_size,
                        allocation.height / 2 + self.__pointer_size)
        else:
            ctx.move_to(allocation.width - self.__pointer_size,
                        allocation.height / 2 - self.__pointer_size)
            ctx.line_to(allocation.width, allocation.height / 2)
            ctx.line_to(allocation.width - self.__pointer_size,
                        allocation.height / 2 + self.__pointer_size)

        ctx.stroke_preserve()
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.fill()

        region = Gdk.cairo_region_create_from_surface(surface)
        self.shape_combine_region(region)

    def draw_top_border(self, drawing_area, event):
        """
            Draw the top of a rectangle with rounded corners to provide
            a border for the window
        """
        # in gtk3 the last param is a cairo context, in gtk2 we need to
        # create one
        if build_gtk2:
            ctx = drawing_area.window.cairo_create()
            ctx.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
            ctx.clip()
        else:
            ctx = event

        alloc = drawing_area.get_allocation()

        # fill with background the background colour first
        ctx.rectangle(0, 0, alloc.width, alloc.height)
        ctx.set_source_rgb(self.__bgr / 255, self.__bgg / 255,
                           self.__bgb / 255)
        ctx.fill()

        # do the actual drawing
        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_line_width(self.__line_width)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgb(self.__fgr / 255, self.__fgg / 255,
                           self.__fgb / 255)

        # the position of the top, left and right border lines depend on whether or not we need to
        # shape the window into a pointer to the app icon
        top_extent = left_extent = self.__border_line
        right_extent = alloc.width - self.__border_line
        if self.__do_window_shaping:
            if self.__panel_orient == MatePanelApplet.AppletOrient.DOWN:
                top_extent += self.__pointer_size
            elif self.__panel_orient == MatePanelApplet.AppletOrient.RIGHT:
                left_extent += self.__pointer_size
            elif self.__panel_orient == MatePanelApplet.AppletOrient.LEFT:
                right_extent -= self.__pointer_size

        ctx.move_to(left_extent, alloc.height)

        ctx.line_to(left_extent, top_extent + self.__line_curve)

        ctx.curve_to(left_extent,
                     top_extent + self.__line_curve,
                     left_extent, top_extent,
                     left_extent + self.__line_curve,
                     top_extent)

        if self.__do_window_shaping and self.__panel_orient == MatePanelApplet.AppletOrient.DOWN:
            # extend the border line into the pointer
            ctx.line_to(alloc.width / 2 - self.__pointer_size + 1,
                        top_extent)
            ctx.line_to(alloc.width / 2, top_extent - self.__pointer_size + 1)
            ctx.line_to(alloc.width / 2 + self.__pointer_size - 1,
                        top_extent)

        ctx.line_to(right_extent - self.__line_curve, top_extent)
        ctx.curve_to(right_extent - self.__line_curve,
                     top_extent,
                     right_extent, top_extent,
                     right_extent,
                     top_extent + self.__line_curve)
        ctx.line_to(right_extent, alloc.height)
        ctx.stroke()

    def draw_left_border(self, drawing_area, event):
        """
            Draw the left hand side of the window border
        """

        if build_gtk2:
            ctx = drawing_area.window.cairo_create()
            ctx.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
            ctx.clip()
        else:
            ctx = event

        alloc = drawing_area.get_allocation()

        # fill with background colour
        ctx.rectangle(0, 0, alloc.width, alloc.height)
        ctx.set_source_rgb(self.__bgr / 255, self.__bgg / 255,
                           self.__bgb / 255)
        ctx.fill()

        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_line_width(self.__line_width)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgb(self.__fgr / 255, self.__fgg / 255,
                           self.__fgb / 255)

        left_extent = self.__border_line
        # the position of the left border depends on whether or not we're doing window shaping
        if self.__do_window_shaping and self.__panel_orient == MatePanelApplet.AppletOrient.RIGHT:
            left_extent += self.__pointer_size

        ctx.move_to(left_extent, 0)

        if self.__do_window_shaping and self.__panel_orient == MatePanelApplet.AppletOrient.RIGHT:
            # extend the border line into the pointer
            ctx.line_to(left_extent,
                        alloc.height / 2 - self.__pointer_size + 1)
            ctx.line_to(self.__border_line, alloc.height / 2)

            ctx.line_to(left_extent, alloc.height / 2 + self.__pointer_size - 1)

        ctx.line_to(left_extent, alloc.height)
        ctx.stroke()

    def draw_right_border(self, drawing_area, event):
        """
            Draw the right hand side of the window border
        """

        if build_gtk2:
            ctx = drawing_area.window.cairo_create()
            ctx.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
            ctx.clip()
        else:
            ctx = event
        alloc = drawing_area.get_allocation()

        ctx.rectangle(0, 0, alloc.width, alloc.height)
        ctx.set_source_rgb(self.__bgr / 255, self.__bgg / 255,
                           self.__bgb / 255)
        ctx.fill()
        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_line_width(self.__line_width)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgb(self.__fgr / 255, self.__fgg / 255,
                           self.__fgb / 255)

        right_extent = alloc.width - self.__border_line
        if self.__do_window_shaping and self.__panel_orient == MatePanelApplet.AppletOrient.LEFT:
            right_extent -= self.__pointer_size

        ctx.move_to(right_extent, 0)

        if self.__do_window_shaping and self.__panel_orient == MatePanelApplet.AppletOrient.LEFT:
            # extend the border line into the pointer
            ctx.line_to(right_extent,
                        alloc.height / 2 - self.__pointer_size + 1)
            ctx.line_to(alloc.width - self.__border_line, alloc.height / 2)
            ctx.line_to(right_extent, alloc.height / 2 + self.__pointer_size - 1)

        ctx.line_to(right_extent, alloc.height)
        ctx.stroke()

    def draw_bottom_border(self, drawing_area, event):
        """
            Draw the bottom of the window border with rounded corners
        
        """

        if build_gtk2:
            ctx = drawing_area.window.cairo_create()
            ctx.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
            ctx.clip()
        else:
            ctx = event

        alloc = drawing_area.get_allocation()
        ctx.rectangle(0, 0, alloc.width, alloc.height)
        ctx.set_source_rgb(self.__bgr / 255, self.__bgg / 255,
                           self.__bgb / 255)
        ctx.fill()

        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_line_width(self.__line_width)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgb(self.__fgr / 255, self.__fgg / 255,
                           self.__fgb / 255)

        # the lower, right and left extents of the border depend on whether or not we need to
        # shape the window into a pointer to the app icon
        left_extent = self.__border_line
        right_extent = alloc.width - self.__border_line
        lower_extent = alloc.height - self.__border_line
        if self.__do_window_shaping:
            if self.__panel_orient == MatePanelApplet.AppletOrient.UP:
                lower_extent -= self.__pointer_size
            elif self.__panel_orient == MatePanelApplet.AppletOrient.RIGHT:
                left_extent += self.__pointer_size
            elif self.__panel_orient == MatePanelApplet.AppletOrient.LEFT:
                right_extent -= self.__pointer_size

        ctx.move_to(left_extent, 0)
        ctx.line_to(left_extent,
                    lower_extent - self.__line_curve)
        ctx.curve_to(left_extent,
                     lower_extent - self.__line_curve,
                     left_extent, lower_extent,
                     left_extent + self.__line_curve,
                     lower_extent)

        if self.__do_window_shaping and self.__panel_orient == MatePanelApplet.AppletOrient.UP:
            # draw a pointer
            ctx.line_to(alloc.width / 2 - self.__pointer_size + 1,
                        lower_extent)
            ctx.line_to(alloc.width / 2, lower_extent + self.__pointer_size - 1)
            ctx.line_to(alloc.width/2 + self.__pointer_size - 1,
                        lower_extent)

        ctx.line_to(right_extent - self.__line_curve, lower_extent)

        ctx.curve_to(right_extent - self.__line_curve,
                     lower_extent,
                     right_extent,
                     lower_extent,
                     right_extent,
                     lower_extent - self.__line_curve)
        ctx.line_to(right_extent, 0)
        ctx.stroke()

    def win_hidden(self, widget):
        """ Event handler for the window's hide event

            Delete the timer object

        """

        self.stop_mouse_area_timer()

    def do_timer(self):
        """
            Check the current mouse position and if it is not within any of the
            rectangles in self.__mouse_area hide the window
        """

        # get the mouse x y
        root_win, x, y, mask = self.get_screen().get_root_window().get_pointer()
        if not self.point_is_in_mouse_areas(x, y):
            self.hide()
            self.__timer_id = None
            return False

        return True

    def clear_mouse_areas(self):
        """ Clear the mouse areas list """
        self.__mouse_areas = []

    def add_mouse_area(self, rect):
        """ Add a rectangle to the __mouse_area_list

            Args: rect - a Gdk.Rectangle
        """
        self.__mouse_areas.append(rect)

    def point_is_in_mouse_areas(self, x, y):
        """ Checks to see if a specified position on the screen is within any of
            the self.__mouse_areas rectangle list

            Args:
                x : the x position
                y : the y position

            Returns:
                True if the position is within one of the rectangles in
                self.__mouse_areas, False otherwise
        """

        for rect in self.__mouse_areas:
            if ((x >= rect.x) and (x <= rect.x + rect.width)) and \
               ((y >= rect.y) and (y <= rect.y + rect.height)):
                return True

        return False

    def get_app(self):
        """ Return the docked app the window list refers to

            Returns:
                A docked_app
        """

        return self.__the_app

    def set_app(self, app):
        """ Set the docked app the window list refers to

            Draw the app icon at an appropriate size for the list

            Args : app - a docked_app
        """

        self.__the_app = app
        if self.__icontheme is not None:
            self.get_app_icon()

    the_app = property(get_app, set_app)

    def get_app_icon(self):
        """ Draws the app icon and stores it in self.__app_pb for
            later use

        self.__the_app and the icon theme and size must have been set before
        this is called....
        """
        if self.__icontheme.has_icon(self.__the_app.icon_name):

            # draw the app icon at the size we want
            icon_info = self.__icontheme.choose_icon([self.__the_app.icon_name,
                                                     None],
                                                     self.__icon_size, 0)

            try:
                pixbuf = icon_info.load_icon()
            except GLib.GError:
                # default to a stock icon if we couldn't load the app
                # icon
                pixbuf = self.render_icon(Gtk.STOCK_EXECUTE,
                                          Gtk.IconSize.DND, None)
        else:
            pixbuf = self.the_app.app_pb.scale_simple(self.__icon_size,
                                                      self.__icon_size,
                                                      GdkPixbuf.InterpType.BILINEAR)

        self.__app_pb = pixbuf

    @property
    def bg_col(self):
        return self.__bgr, self.__bgg, self.__bgb

    @property
    def fg_col(self):
        return self.__fgr, self.__fgg, self.__fgb

    @property
    def hl_col(self):
        return self.__hlr, self.__hlg, self.__hlb

    @property
    def icon_size(self):
        return self.__icon_size

    @icon_size.setter
    def icon_size(self, size_in_pixels):
        self.__icon_size = size_in_pixels
        if (self.__the_app is not None) and \
           (self.__icontheme is not None):
            self.__get_app_icon()

    @property
    def app_pb(self):
        return self.__app_pb

    def get_icontheme(self):
        """ Return the icontheme

            Returns:
                A Gtk.Icontheme
        """

        return self.__icontheme

    def set_icontheme(self, the_icontheme):
        """ Sets the icontheme currently being used

            Args : the_icontheme
        """

        self.__icontheme = the_icontheme

    icontheme = property(get_icontheme, set_icontheme)

    def da_pointer_draw(self, drawing_area, event):

        ctx = event
        alloc = drawing_area.get_allocation()

        ctx.rectangle(0, 0, alloc.width, alloc.height)
        ctx.set_source_rgb(self.__bgr / 255, self.__bgg / 255,
                           self.__bgb / 255)
        ctx.fill()

    def set_app_root_coords(self, x, y):
        """ Sets the x and y root coords of the app
        """

        self.__app_x = x
        self.__app_y = y

    def set_applet_details(self, applet_x, applet_y, applet_w, applet_h):
        """ Sets the variables which record the root coords and size of the
            applet

            Args:
                applet_x : the x position of the top left of the applet
                           (root coords)
                applet_y : the y position of the top left of the applet
                           (root coords)
                applet_w : the width of the applet
                applet_h : the height of the applet

        """

        self.__applet_x = applet_x
        self.__applet_y = applet_y
        self.__applet_w = applet_w
        self.__applet_h = applet_h
