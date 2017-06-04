#!/usr/bin/env python3

""" Helper classes for apps in the dock

    Provide a base class and descendants which will allow various types
    of indicators to be drawn onto a Cairo canvas provided by an app
    in the dock

    Provide a base class and descendants which will allow various types
    of backgrounds (e.g. gradient fill) to be drawn onto a Cairo canvas
    provided by an app in the dock

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
build_gtk2 = False

import gi

if build_gtk2:
    gi.require_version("Gtk", "2.0")
    gi.require_version("Wnck", "1.0")
else:
    gi.require_version("Gtk", "3.0")

gi.require_version("MatePanelApplet", "4.0")

from gi.repository import Gtk
from gi.repository import MatePanelApplet
import cairo
import math


class IndicatorType:
    """Class to define the indicator types"""
    LIGHT = 0    # Light Circle
    DARK = 1     # Dark Circle
    NONE = 2
    TBAR = 3     # Theme Bar
    TCIRC = 4    # Circle drawn in theme colour
    TSQUARE = 5  # Square drawn in theme colour
    TTRI = 6     # Triangle drawn in theme colour
    TDIA = 7     # Diamond drawn in theme colour
    SUBWAY = 8   # Metro type


class ActiveBgType:
    """Class to define the active icon background types"""
    GRADIENT = 0
    ALPHAFILL = 1

# static list to hold the rgb colour elements to use when drawing
# and indicator and we can't get the theme highlight colour i.e. when
# using gtk2
fallback_ind_col = [0.9, 0.9, 0.9]


def get_theme_highlight_col(applet):
    """
        get the current theme's highlight colour (Gtk3) or the fallback colour 
        (Gtk2)
        
    Args:
        applet : the dock applet 
    :return:
        a tuple containing the r,g,b values (0-1.0) of the colors
         
    """

    if build_gtk2:
        return fallback_ind_col
    else:

        context = applet.get_style_context()

        sel_bg = context.lookup_color("theme_selected_bg_color")
        if sel_bg[0]:
            hcol = sel_bg[1]
            return [hcol.red, hcol.green, hcol.blue]
        else:
            # assume what is hopefully a decent looking highlight
            # colour - something a bit brighter (or maybe a lot darker)
            # than the background
            c_info = context.lookup_color("dark_bg_color")
            if c_info[0]:
                bgcol = c_info[1]
                return [(bgcol.red + 0.25) % 1,
                        (bgcol.green + 0.25) % 1,
                        (bgcol.blue + 0.25) % 1]
            else:
                # we don't even have a background colour, so....
                return fallback_ind_col


class IndicatorDrawer(object):
    """ Base class for drawing indicators

     Provide a base class which can be used for drawing various type of
     app indicators onto Cairo surfaces

     This class must not be instantiated and it will be an error to try
     and use this to draw indicators. Descendant classes will be implement
     their own drawing functions

     Attributes:
        _context : the cairo context to draw onto
        _size    : the size (width and height - assumes is square...) of the docked app
        _orient  : the orientation of the dock applet e.g. MatePanelApplet.AppletOrient.RIGHT
        _num_ind : the number of indicators to draw, may not be applicable to all indicators
        extra_s  : (static) amount of extra size (in pixels) the indicator requires of the docked_app

    Descendant classes can implement their own properties as necessary if they need more control
    over the drawing process (e.g. to set a specific indicator colour)

    """

    extra_s = 0  # default value for most indicators - those which require more
                 # must override this

    def __init__(self, context, size, orient, num_ind=0):
        """ Constructor

        Set attributes according to the constructor parameters

        """

        super().__init__()

        self._context = context
        self._size = size
        self._orient = orient
        self._num_ind = num_ind

    def draw(self):
        """
            Abstract method - descendants will implement this as required and return
                              _surface when drawing is completed
        """

        raise NotImplementedError("Must be implemented by Indicator subclasses")


class DefaultInd(IndicatorDrawer):
    """
        Base class for the two variants (light and dark) of the default indicator
    """

    def __init__(self, context, size, orient, num_ind):
        """
            Constructor - call the inherited constructor and do additional
            bits of setup
        """
        super().__init__(context, size, orient, num_ind)

        # set the cairo colour values of the inner and outer areas of the indicator
        self._col1 = [0.0, 0.0, 0.0]
        self._col2 = [0.0, 0.0, 0.0]

    def draw(self):
        """
                  Draw up to 4 indicators

              """

        if self._orient == MatePanelApplet.AppletOrient.RIGHT:
            ind_x = 2
            ind_y = (self._size - 4) / (self._num_ind + 1) + 2

        elif self._orient == MatePanelApplet.AppletOrient.LEFT:
            ind_x = self._size - 1
            ind_y = (self._size - 4) / (self._num_ind + 1) + 2

        elif self._orient == MatePanelApplet.AppletOrient.DOWN:
            ind_x = (self._size - 4) / (self._num_ind + 1) + 2
            ind_y = 2
        else:
            ind_x = (self._size - 4) / (self._num_ind + 1) + 2
            ind_y = self._size - 1

        this_ind = 1
        while this_ind <= self._num_ind:
            rad_patt = cairo.RadialGradient(ind_x, ind_y, 2,
                                            ind_x, ind_y, 4)

            rad_patt.add_color_stop_rgba(0, self._col1[0], self._col1[1],
                                         self._col1[2], 1)
            rad_patt.add_color_stop_rgba(1, self._col2[0], self._col2[1],
                                         self._col2[2], 0)

            self._context.set_source(rad_patt)
            self._context.arc(ind_x, ind_y, 6, 0, 2 * math.pi)

            if self._num_ind > 1:
                if (self._orient == MatePanelApplet.AppletOrient.RIGHT) or \
                        (self._orient == MatePanelApplet.AppletOrient.LEFT):
                    ind_y += (self._size - 6) / (self._num_ind + 1)
                else:
                    ind_x += (self._size - 6) / (self._num_ind + 1)

            this_ind += 1

            self._context.fill()


class DefaultLightInd(DefaultInd):
    """
        Class to draw the dock applet's default light indicator

    """

    def __init__(self, context, size, orient, num_ind):
        """
                 Constructor - call the inherited constructor and do additional
                 bits of setup
        """

        super().__init__(context, size, orient, num_ind)

        # cairo colour values of the inner and outer areas of the indicator
        self._col1 = [0.9, 0.9, 0.9]
        self._col2 = [0.0, 0.0, 0.0]


class DefaultDarkInd(DefaultInd):
    """
        Class to draw the dock applet's default dark indicator
    """

    def __init__(self, context, size, orient, num_ind):
        """
                 Constructor - call the inherited constructor and do additional
                 bits of setup
        """

        super().__init__(context, size, orient, num_ind)

        # cairo colour values of the inner and outer areas of the indicator
        self._col1 = [0.0, 0.0, 0.0]
        self._col2 = [0.9, 0.9, 0.9]


class BarInd(IndicatorDrawer):
    """
        Base class for the bar indicator, a filled rectangle

        Multiple indicators are not supported - the bar runs the full width
        (or height, depending on the applet orientation) of the context
        and merely indicates that an app is running, not how many windows
        it has open...

    """

    def __init__(self, context, size, orient):
        """

        """
        super().__init__(context, size, orient)

        # cairo colour values of the bar, will be overridden by descendant classes
        self._barcol = [0.0, 0.0, 0.0]

    def draw(self):
        """
            Draw the bar along the edge of the panel adjoining the screen

        """

        line_size = 1
        self._context.set_line_cap(cairo.LINE_CAP_SQUARE)
        self._context.set_line_width(line_size)

        self._context.set_source_rgb(self._barcol[0], self._barcol[1], self._barcol[2])
        if self._orient == MatePanelApplet.AppletOrient.RIGHT:
            rect = [[0.5, 0.5], [2.5, 0.5],
                    [2.5, self._size - 0.5], [0.5, self._size - 0.5]]

        elif self._orient == MatePanelApplet.AppletOrient.LEFT:
            rect = [[self._size - 2.5, 0.5], [self._size - 0.5, 0, 5],
                    [self._size - 0.5, self._size - 0.5], [self._size - 2.5, self._size - 0.5]]

        elif self._orient == MatePanelApplet.AppletOrient.DOWN:
            rect = [[0.5, 0.5], [self._size-0.5, 0.5],
                    [self._size-0.5, 2.5], [0.5, 2.5]]

        else:
            rect = [[0.5, self._size - 2.5], [self._size - 0.5, self._size - 2.5],
                    [self._size - 0.5, self._size - 0.5], [0.5, self._size - 0.5]]

        self._context.set_line_width(1)
        self._context.move_to(rect[0][0], rect[0][1])

        for point in rect:
            self._context.line_to(point[0], point[1])

        self._context.line_to(rect[0][0], rect[0][1])

        self._context.stroke_preserve()
        self._context.fill()


class ThemeBarInd(BarInd):
    """
        A bar indicator in which the bar is drawn in the current theme's
        highlight colour (Gtk3) or using a fallback colour (Gtk2)
    """

    def __init__(self, context, size, orient, applet):
        """
            Constructor - call the inherited constructor and do additional
            bits of setup

        Args (in addition to those specified in the base class)
            applet : the applet

        """
        super().__init__(context, size, orient)

        # set the bar color
        self._barcol = get_theme_highlight_col(applet)


class ThemeCircleInd(IndicatorDrawer):
    """
        Draws round indicators (up to 4) with the current theme's highlight colour
    """

    def __init__(self, context, size, orient, applet, num_ind=0):
        """
            Constructor - call the inherited constructor and do additional
            bits of setup

        Args (in addition to those specified in the base class)
            applet : the applet

        """
        super().__init__(context, size, orient, num_ind)

        # set the indicator color
        self._indcol = get_theme_highlight_col(applet)

    def draw(self):
        """
                  Draw up to 4 indicators

              """

        if self._orient == MatePanelApplet.AppletOrient.RIGHT:
            ind_x = 2
            ind_y = (self._size - 4) / (self._num_ind + 1) + 2

        elif self._orient == MatePanelApplet.AppletOrient.LEFT:
            ind_x = self._size - 2
            ind_y = (self._size - 4) / (self._num_ind + 1) + 2

        elif self._orient == MatePanelApplet.AppletOrient.DOWN:
            ind_x = (self._size - 4) / (self._num_ind + 1) + 2
            ind_y = 2
        else:
            ind_x = (self._size - 4) / (self._num_ind + 1) + 2
            ind_y = self._size - 2

        this_ind = 1
        while this_ind <= self._num_ind:

            self._context.set_source_rgb(self._indcol[0], self._indcol[1], self._indcol[2])
            self._context.set_line_width(1)
            self._context.arc(ind_x, ind_y, 2, 0, 2 * math.pi)
            self._context.close_path()
            self._context.fill()

            if self._num_ind > 1:
                if (self._orient == MatePanelApplet.AppletOrient.RIGHT) or \
                        (self._orient == MatePanelApplet.AppletOrient.LEFT):
                    ind_y += (self._size - 6) / (self._num_ind + 1)
                else:
                    ind_x += (self._size - 6) / (self._num_ind + 1)

            this_ind += 1


class ThemeSquareInd(IndicatorDrawer):
    """
        Draws square indicators (up to 4) with the current theme's highlight colour
    """

    def __init__(self, context, size, orient, applet, num_ind=0):
        """
            Constructor - call the inherited constructor and do additional
            bits of setup

        Args (in addition to those specified in the base class)
            applet : the applet

        """
        super().__init__(context, size, orient, num_ind)

        # set the indicator color
        self._indcol = get_theme_highlight_col(applet)

    def draw(self):
        """
                  Draw up to 4 indicators

              """

        line_size = 1
        ind_size = 3

        self._context.set_line_width(line_size)

        # work out the x&y coords of the top left of the first indicator
        if self._orient == MatePanelApplet.AppletOrient.RIGHT:
            ind_x = 1.5
            ind_y = (self._size - ind_size) / (self._num_ind + 1) + 0.5

        elif self._orient == MatePanelApplet.AppletOrient.LEFT:
            ind_x = self._size - ind_size - 0.5
            ind_y = (self._size - ind_size) / (self._num_ind + 1) + 0.5

        elif self._orient == MatePanelApplet.AppletOrient.DOWN:
            ind_x = (self._size - ind_size) / (self._num_ind + 1) + 0.5
            ind_y = 1.5
        else:
            ind_x = (self._size - ind_size) / (self._num_ind + 1) + 0.5
            ind_y = self._size - ind_size - 0.5

        self._context.set_line_width(line_size)

        this_ind = 1
        while this_ind <= self._num_ind:

            self._context.set_source_rgb(self._indcol[0], self._indcol[1], self._indcol[2])

            self._context.rectangle(ind_x, ind_y, ind_size, ind_size)
            self._context.stroke_preserve()
            self._context.fill()

            if self._num_ind > 1:
                if (self._orient == MatePanelApplet.AppletOrient.RIGHT) or \
                        (self._orient == MatePanelApplet.AppletOrient.LEFT):
                    ind_y += (self._size - 6) / (self._num_ind + 1)
                else:
                    ind_x += (self._size - 6) / (self._num_ind + 1)

            this_ind += 1


class ThemeDiaInd(IndicatorDrawer):
    """
        Draws diamond indicators (up to 4) with the current theme's highlight colour
    """

    def __init__(self, context, size, orient, applet, num_ind=0):
        """
            Constructor - call the inherited constructor and do additional
            bits of setup

        Args (in addition to those specified in the base class)
            applet : the applet

        """
        super().__init__(context, size, orient, num_ind)

        # set the indicator color
        self._indcol = get_theme_highlight_col(applet)

    def draw(self):
        """
                  Draw up to 4 indicators

              """

        line_size = 1
        ind_size = 4.0

        # self._context.set_line_cap(cairo.LINE_CAP_ROUND)
        self._context.set_line_width(line_size)

        # work out the x&y coords of the top centre of the first indicator
        if self._orient == MatePanelApplet.AppletOrient.RIGHT:
            ind_x = (ind_size / 2) + 0.5
            ind_y = (self._size - ind_size) / (self._num_ind + 1) + 0.5

        elif self._orient == MatePanelApplet.AppletOrient.LEFT:
            ind_x = self._size - (ind_size / 2) - 0.5
            ind_y = (self._size - ind_size) / (self._num_ind + 1)

        elif self._orient == MatePanelApplet.AppletOrient.DOWN:
            ind_x = (self._size - ind_size) / (self._num_ind + 1) + (ind_size / 2) + 0.5
            ind_y = 1.5
        else:
            ind_x = (self._size - ind_size) / (self._num_ind + 1) + (ind_size / 2) + 0.5
            ind_y = self._size - ind_size - 0.5

        this_ind = 1
        while this_ind <= self._num_ind:

            self._context.set_source_rgb(self._indcol[0], self._indcol[1], self._indcol[2])
            self._context.move_to(ind_x, ind_y)
            self._context.line_to(ind_x + (ind_size / 2), ind_y + (ind_size / 2))
            self._context.line_to(ind_x, ind_y + ind_size)
            self._context.line_to(ind_x - (ind_size / 2), ind_y + (ind_size / 2))
            self._context.line_to(ind_x, ind_y)
            self._context.stroke_preserve()
            self._context.fill()

            if self._num_ind > 1:
                if (self._orient == MatePanelApplet.AppletOrient.RIGHT) or \
                        (self._orient == MatePanelApplet.AppletOrient.LEFT):
                    ind_y += (self._size - 6) / (self._num_ind + 1)
                else:
                    ind_x += (self._size - 6) / (self._num_ind + 1)

            this_ind += 1


class ThemeTriInd(IndicatorDrawer):
    """
        Draws triangle indicators (up to 4) with the current theme's highlight colour
    """

    def __init__(self, context, size, orient, applet, num_ind=0):
        """
            Constructor - call the inherited constructor and do additional
            bits of setup

        Args (in addition to those specified in the base class)
            applet : the applet

        """
        super().__init__(context, size, orient, num_ind)

        # set the bar color
        self._indcol = get_theme_highlight_col(applet)

    def draw(self):
        """
                  Draw up to 4 indicators

              """

        line_size = 1
        ind_width = 4
        ind_height = 3

        self._context.set_line_width(line_size)
        self._context.set_source_rgb(self._indcol[0], self._indcol[1], self._indcol[2])

        # for each panel orientation we need to make sure the triangle is drawn with its
        # point facing the icon...
        if self._orient == MatePanelApplet.AppletOrient.RIGHT:
            ind_x = 0.5
            ind_y = (self._size - ind_width) / (self._num_ind + 1) + 0.5
            point1 = [ind_x, ind_y]
            point2 = [ind_x + ind_height, ind_y + ind_width / 2]
            point3 = [ind_x, ind_y + ind_width]

        elif self._orient == MatePanelApplet.AppletOrient.LEFT:
            ind_x = self._size - 0.5
            ind_y = (self._size - ind_width) / (self._num_ind + 1) + 0.5
            point1 = [ind_x, ind_y]
            point2 = [ind_x - ind_height, ind_y + ind_height / 2]
            point3 = [ind_x, ind_y + ind_width]

        elif self._orient == MatePanelApplet.AppletOrient.DOWN:
            ind_x = (self._size - ind_width) / (self._num_ind + 1) + 0.5
            ind_y = 0.5
            point1 = [ind_x, ind_y]
            point2 = [ind_x + ind_width / 2, ind_y + ind_height]
            point3 = [ind_x + ind_width, ind_y]
        else:

            ind_x = (self._size - ind_width) / (self._num_ind + 1) + 0.5
            ind_y = self._size - 0.5
            point1 = [ind_x, ind_y]
            point2 = [ind_x + ind_width / 2, ind_y - ind_height]
            point3 = [ind_x + ind_width, ind_y]

        this_ind = 1

        while this_ind <= self._num_ind:

            self._context.move_to(point1[0], point1[1])
            self._context.line_to(point2[0], point2[1])
            self._context.line_to(point3[0], point3[1])
            self._context.line_to(point1[0], point1[1])
            self._context.stroke_preserve()
            self._context.fill()

            if self._num_ind > 1:
                if (self._orient == MatePanelApplet.AppletOrient.RIGHT) or \
                        (self._orient == MatePanelApplet.AppletOrient.LEFT):
                    point1[1] += (self._size - 6) / (self._num_ind + 1)
                    point2[1] += (self._size - 6) / (self._num_ind + 1)
                    point3[1] += (self._size - 6) / (self._num_ind + 1)

                else:
                    point1[0] += (self._size - 6) / (self._num_ind + 1)
                    point2[0] += (self._size - 6) / (self._num_ind + 1)
                    point3[0] += (self._size - 6) / (self._num_ind + 1)

            this_ind += 1


class SubwayInd(IndicatorDrawer):
    """
        Indicator which mimics the Metro look
                   
    """

    extra_s = 4  # this type of indicator requires extra space

    def __init__(self, context, size, orient, applet, num_ind, surface, active):
        """
        Args (additional):
            surface : the cairo surface the indicators are being drawn on
            active  : bool - whether or not the app is active
            
        """
        super().__init__(context, size, orient, num_ind)

        # set the color of the bar indicator for the first indicator
        self._barcol = get_theme_highlight_col(applet)
        self._surface = surface
        self._active = active

    def draw(self):
        """
        The first open window of an app is drawn as for ThemeBarInd.
        
        If more than one indicator is required, the way it is drawn depends
        on whether or not the app active. If so, the last three columns (or
        rows, depending on the applet orientation) of the cairo surface
        are copied and drawn to the right (or below) the app icon. If not
        active, the rightmost part of the bar is drawn in a darker colour
        
        """

        b_o = 0.5  # orgin of the bar in cairo units
        b_w = 2.0  # width of the bar in cairo units

        # draw the bar
        line_size = 1
        self._context.set_line_cap(cairo.LINE_CAP_SQUARE)
        self._context.set_line_width(line_size)

        self._context.set_source_rgb(self._barcol[0], self._barcol[1], self._barcol[2])

        # define the four points to the bar - the order of the points is
        # top left, top right, bottom right, bottom left
        if self._orient == MatePanelApplet.AppletOrient.RIGHT:
            rect = [[b_o, b_o], [b_w, b_o],
                    [b_w, self._size - b_o], [b_o, self._size - b_o]]

        elif self._orient == MatePanelApplet.AppletOrient.LEFT:
            rect = [[self._size - b_w, b_o], [self._size - b_o, b_o],
                    [self._size - b_o, self._size - b_o], [self._size - b_w, self._size - b_o]]

        elif self._orient == MatePanelApplet.AppletOrient.DOWN:
            rect = [[b_o, b_o], [self._size - b_o, b_o],
                    [self._size - b_o, b_w], [b_o, b_w]]

        else:
            rect = [[b_o, self._size - b_w], [self._size-b_o, self._size - b_w],
                    [self._size - b_o, self._size - b_o], [b_o, self._size - b_o]]

        self._context.move_to(rect[0][0], rect[0][1])
        for point in rect:
            self._context.line_to(point[0], point[1])

        self._context.line_to(rect[0][0], rect[0][1])

        self._context.stroke_preserve()
        self._context.fill()

        if self._num_ind > 1:

            if self._active:
                # copy the required area from the surface to other parts of the surface...
                if self._orient == MatePanelApplet.AppletOrient.DOWN or \
                   self._orient == MatePanelApplet.AppletOrient.UP:
                    sx = self._size - 4

                    dx = self._size + 1
                    dy = 0
                    dw = 3
                    dh = self._size + 1

                else:
                    sx = 0

                    dx = 0
                    dy = self._size + 1
                    dw = self._size + 1
                    dh = 3

                # copy the relevant part of the source surface to a new surface
                copy_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, dw, dh)
                copy_ctx = cairo.Context(copy_surf)
                copy_ctx.set_source_surface(self._surface, -sx, 0)
                copy_ctx.rectangle(0, 0, dw, dh)
                copy_ctx.fill()

                # now draw onto the main surface
                if self._orient == MatePanelApplet.AppletOrient.DOWN or \
                   self._orient == MatePanelApplet.AppletOrient.UP:
                    self._context.set_source_surface(copy_surf, dx, 0)
                else:
                    self._context.set_source_surface(copy_surf, 0, dy)

                self._context.rectangle(dx, dy, dw, dh)
                self._context.fill()
            else:
                # darken part of the bar and draw a seperator between both parts

                darken_size = 5
                self._context.set_operator(cairo.OPERATOR_CLEAR)
                self._context.set_source_rgba(0, 0, 0, 1)
                if self._orient == MatePanelApplet.AppletOrient.DOWN or \
                   self._orient == MatePanelApplet.AppletOrient.UP:
                    self._context.move_to(rect[1][0]-darken_size, rect[1][1])
                    self._context.line_to(rect[1][0]-darken_size, rect[2][1])
                else:
                    self._context.move_to(rect[2][0], rect[2][1]-darken_size)
                    self._context.line_to(rect[3][0], rect[2][1]-darken_size)

                self._context.stroke()
                self._context.set_operator(cairo.OPERATOR_OVER)

                # darken with semi transparent black rectangle
                self._context.set_source_rgba(0, 0, 0, 0.20)
                if self._orient == MatePanelApplet.AppletOrient.DOWN or \
                   self._orient == MatePanelApplet.AppletOrient.UP:
                    self._context.move_to(rect[1][0] - darken_size - 1, rect[0][1])
                    self._context.line_to(rect[1][0], rect[1][1])
                    self._context.line_to(rect[2][0], rect[2][1])
                    self._context.line_to(rect[1][0] - darken_size - 1, rect[3][1])
                    self._context.line_to(rect[1][0] - darken_size - 1, rect[0][1])
                else:
                    self._context.move_to(rect[2][0], rect[2][1] - darken_size - 1)
                    self._context.line_to(rect[2][0], rect[2][1])
                    self._context.line_to(rect[3][0], rect[2][1])
                    self._context.line_to(rect[3][0], rect[2][1] - darken_size - 1)
                    self._context.line_to(rect[2][0], rect[2][1] - darken_size - 1)

                self._context.stroke_preserve()
                self._context.fill()


def ind_extra_s(indtype):
    """ Convenience function for returning the extra space required by an indicator 
    
    Args: IndicatorType : The type of indicator e.g. ThemeTriInd
    
    Returns : int
    
    """

    if indtype == IndicatorType.LIGHT:
        return DefaultLightInd.extra_s
    elif indtype == IndicatorType.DARK:
        return DefaultDarkInd.extra_s
    elif indtype == IndicatorType.TBAR:
        return ThemeBarInd.extra_s
    elif indtype == IndicatorType.TCIRC:
        return ThemeCircleInd.extra_s
    elif indtype == IndicatorType.TSQUARE:
        return ThemeSquareInd.extra_s
    elif indtype == IndicatorType.TTRI:
        return ThemeTriInd.extra_s
    elif indtype == IndicatorType.TDIA:
        return ThemeDiaInd.extra_s
    elif indtype == IndicatorType.SUBWAY:
        return SubwayInd.extra_s
    else:
        return 0


###########################################################################################


class ActiveBackgroundDrawer(object):
    """ Base class for drawing the background of active dock apps

     Provide a base class which can be used for drawing various type of
     backgrounds onto Cairo surfaces

     This class must not be instantiated and it will be an error to try
     and use this to draw backgrounds. Descendant classes will implement
     their own drawing functions

     Attributes:
        _context : the cairo context to draw onto
        _size    : the size (width and height - assumes is square...) of the size
        _orient  : the orientation of the dock applet e.g. MatePanelApplet.AppletOrient.RIGHT


    Descendant classes can implement their own properties as necessary if they need more control
    over the drawing process (e.g. to set a specific indicator colour)

    """

    def __init__(self, context, size, orient):
        """ Constructor

        Set attributes according to the constructor parameters

        """

        super().__init__()

        self._context = context
        self._size = size
        self._orient = orient

    def draw(self):
        """
            Abstract method - descendants will implement this as required and return
                              _surface when drawing is completed
        """

        raise NotImplementedError("Must be implemented by ActiveBackgroundDrawer descendents")


class DefaultBackgroundDrawer(ActiveBackgroundDrawer):
    """
        Class to draw the default active background, a colour gradient based on the
        the average colour of the app's icon
    """
    def __init__(self, context, size, orient, r, g, b):
        """ Constructor ...

        Args (in addition to those of the base class):
            r : the red component of the average colour
            g : the green component of the average colour
            b : the blue component of the average colour

        """
        super().__init__(context, size, orient)

        self._red = r
        self._green = g
        self._blue = b

    def draw(self):
        """
            Do the actual drawing, based on the panel orientation
        """

        # draw a background gradient according to the applet orientation
        if self._orient == MatePanelApplet.AppletOrient.RIGHT:
            pattern = cairo.LinearGradient(0, 0, self._size, 0)
            pattern.add_color_stop_rgba(0.0, self._red, self._green, self._blue, 1)
            pattern.add_color_stop_rgba(1.0, self._red, self._green, self._blue, 0)
        elif self._orient == MatePanelApplet.AppletOrient.LEFT:
            pattern = cairo.LinearGradient(self._size, 0, 0, 0)
            pattern.add_color_stop_rgba(0.0, self._red, self._green, self._blue, 1)
            pattern.add_color_stop_rgba(1.0, self._red, self._green, self._blue, 0)
        elif self._orient == MatePanelApplet.AppletOrient.DOWN:
            pattern = cairo.LinearGradient(0, 0, 0, self._size)
            pattern.add_color_stop_rgba(0.0, self._red, self._green, self._blue, 1)
            pattern.add_color_stop_rgba(1.0, self._red, self._green, self._blue, 0)
        else:
            pattern = cairo.LinearGradient(0, self._size, 0, 0)
            pattern.add_color_stop_rgba(0.0, self._red, self._green, self._blue, 1)
            pattern.add_color_stop_rgba(1.0, self._red, self._green, self._blue, 0)

        self._context.rectangle(0, 0, self._size, self._size)
        self._context.set_source(pattern)
        self._context.fill()


class AlphaFillBackgroundDrawer(ActiveBackgroundDrawer):
    """
        Fills the background with a specified colour and opacity
    """

    def __init__(self, context, size, orient, r, g, b, a):
        """ Constructor ...

        Args (in addition to those of the base class):
            r : the red component of the bg colour
            g : the green component of the bg colour
            b : the blue component of the bg colour
            a : the alpha component

        """
        super().__init__(context, size, orient)

        self._red = r
        self._green = g
        self._blue = b
        self.alpha = a

    def draw(self):
        """
            Do the actual drawing
        """

        self._context.rectangle(0, 0, self._size, self._size)
        self._context.set_source_rgba(self._red, self._green, self._blue, self.alpha)
        self._context.fill()
