#!/usr/bin/env python3

"""
    Provide notification when the desktop background changes to a new picture
    and, if necessary, change the color of the MATE panel(s) to the dominant
    color of the new image

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
else:
    gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gio

import cairo

import os
import threading

import dom_color
from collections import namedtuple
from time import sleep

from log_it import log_it as log_it

ChangeTup = namedtuple('ChangeTup', ['settings', 'ored', 'ogreen', 'oblue',
                                     'step_red', 'step_green', 'step_blue'])


class PanelColorChanger(object):
    """ Class to change the color of the MATE panel(s) to the dominant color of
        the wallpaper image

    Provide support for wallpaper images only - gradients, solid colours and
    slideshows will be ignored
    Change the panel color whenever the wallpaper image is changed
    Allow only a specific panel's color to be changed, rather than all panels

    """

    def __init__(self, update_callback=None):
        """ Init for the PanelColorChanger class

            Use Gio.Settings to monitor the MATE desktop wallpaper setting

            Args:
                updated_callback - a function to be called after the panel
                                   colors have been updated
        """

        super().__init__()

        self.update_cb = update_callback

        self.__red = self.__green = self.__blue = 0
        # will hold rgb of the dom color of the wallpaper

        self.__bg_settings = Gio.Settings.new("org.mate.background")

        self.__pf = self.__bg_settings.get_string("picture-filename")

        self.__panel_settings = Gio.Settings.new("org.mate.panel")

        self.__event_handler_id = 0

        self.__toplevel_id = ""

    def enable_color_change(self):
        """ Enable panel color changing

        Monitor the MATE wallpaper setting and create an event handler to be
        called whenever it changes """

        self.__event_handler_id = self.__bg_settings.connect("changed",
                                                             self.background_changed)

    def disable_color_change(self):
        """ Disable panel color changing

        Disconnect the event handler linked to wallpaper changes """

        self.__bg_settings.disconnect(self.__event_handler_id)

    def do_change_panel_color(self):
        """ Change the panel colour

        Call the event handler ourselves in order to change the panel colour
        """

        self.background_changed(None, "picture-filename")

    def set_single_panel(self, toplevel_id):
        """ Store the id of the panel which is the only one whose colour is
            to be changed

        Args:
            toplevel_id : the toplevel_id of the panel. If this is an empty
                          string all panels are to have their colour changed
        """

        self.__toplevel_id = toplevel_id

    def background_changed(self, settings, key):
        """ Callback for when the desktop wallpaper settings are changed
        """

        if key == "picture-filename":
            new_pf = self.__bg_settings.get_string("picture-filename")
            self.__pf = new_pf

            # we're only interested if the wallpaper is an image file
            if (new_pf is not None) and (new_pf != ""):
                pic_ext = os.path.splitext(new_pf)[1]
                if pic_ext.upper() != ".XML":

                    worker_thread = threading.Thread(target=self.change_panel_colors)
                    worker_thread.start()

    def get_dom_color(self):
        """ Get  the dominant color of the current desktop image
        """

        colstr = dom_color.get_dom_color(self.__pf)

        self.__red = int(colstr[0:2], 16)
        self.__green = int(colstr[2:4], 16)
        self.__blue = int(colstr[4:6], 16)

    def change_panel_colors(self):
        """ Change panel colors to the rgb of the current dominant color

            Change the colour smoothly over an interval of 0.5 seconds

        """

        self.get_dom_color()

        change_list = []  # initialise list of panels & settings we need to change

        # get the list of panels
        panel_list = self.__panel_settings.get_value("toplevel-id-list").unpack()
        for panel in panel_list:

            # do we want to change this panel?
            do_change = (self.__toplevel_id == "") or \
                        (self.__toplevel_id == panel)

            if do_change:
                # get the settings path for the current panel
                settings_path = "/org/mate/panel/toplevels/%s/background/" % panel

                # get this panel's settings
                psettings = Gio.Settings.new_with_path("org.mate.panel.toplevel.background",
                                                       settings_path)

                # get the panel's original colour rgb components
                colstr = psettings.get_string("color")

                # the color can be stored as either a set of rgba values or as
                # an rgb hex ...
                store_rgba = False
                store_rgb = False
                if colstr.startswith("rgba"):
                    store_rgba = True
                    colstrip = colstr[4:255]
                    colstrip = colstrip.strip("()")
                    cols = colstrip.split(",")
                    pr = int(cols[0])
                    pg = int(cols[1])
                    pb = int(cols[2])
                    po = float(cols[3])
                elif colstr.startswith("rgb"):
                    store_rgb = True
                    colstrip = colstr.strip("rgb()")
                    cols = colstrip.split(",")
                    pr = int(cols[0])
                    pg = int(cols[1])
                    pb = int(cols[2])
                else:
                    pr = int(colstr[1:3], 16)
                    pg = int(colstr[3:5], 16)
                    pb = int(colstr[5:7], 16)

                # we're going to change the panel's color in 25 discrete steps,
                # so get the difference we need to apply to each color
                # component each step
                if pr > self.__red:
                    rs = -(pr - self.__red)
                else:
                    rs = self.__red - pr

                if pg > self.__green:
                    gs = -(pg - self.__green)
                else:
                    gs = self.__green - pg

                if pb > self.__blue:
                    bs = -(pb - self.__blue)
                else:
                    bs = self.__blue - pb

                rs /= 25
                gs /= 25
                bs /= 25

                change_list.append(ChangeTup(settings=psettings, ored=pr,
                                             ogreen=pg, oblue=pb, step_red=rs,
                                             step_blue=bs, step_green=gs))

        # now do the colour change
        for loop in range(1, 25):
            for change_item in change_list:
                if loop == 1:
                    # make sure the panel in question is set to be a colour
                    change_item.settings.set_string("type", "color")

                # work out new rgb values for this interval
                new_red = int(change_item.ored +
                              (loop * change_item.step_red)) & 0xff
                new_blue = int(change_item.oblue +
                               (loop * change_item.step_blue)) & 0xff
                new_green = int(change_item.ogreen +
                                (loop * change_item.step_green)) & 0xff
                if store_rgba:
                    change_item.settings.set_string("color",
                                                    "rgba(%d,%d,%d,%0.6f)"
                                                    % (new_red, new_green,
                                                       new_blue, po))
                elif store_rgb:
                    change_item.settings.set_string("color",
                                                    "rgb(%d,%d,%d)"
                                                    % (new_red, new_green,
                                                       new_blue))
                else:
                    change_item.settings.set_string("color",
                                                    "#%.2x%.2x%.2x"
                                                    % (new_red, new_green,
                                                       new_blue))

            # all panels have been changed for this step, so pause for a bit
            sleep(0.02)

        # now that we've had a smooth transition, set panel colours to the
        # final value
        for change_item in change_list:
            if store_rgba:
                change_item.settings.set_string("color",
                                                "rgba(%d,%d,%d,%0.6f)"
                                                % (self.__red, self.__green,
                                                   self.__blue, po))
            else:
                change_item.settings.set_string("color",
                                                "#%.2x%.2x%.2x"
                                                % (self.__red, self.__green,
                                                   self.__blue))

        # finally, call the callback function
        if self.update_cb is not None:
            self.update_cb()

    def wallpaper_filename(self):
        """ Get the desktop wallpaper image filename
        """
        return self.__pf

    def panel_rgb(self):
        """ Get the rgb values of the colour we set the panel(s) to

            Returns:
                red, green, blue: integers

        """

        return self.__red, self.__green, self.__blue


class TestWindow(Gtk.Window):
    """Testing window for the color changer code"""

    def __init__(self):
        """Init for the Test window class

        Create the window and its contents
        """

        super().__init__(title="Dock color changer test")

        self.__button = Gtk.Button(label="Close", stock=Gtk.STOCK_CLOSE)
        self.__button.connect("button-press-event", self.win_button_press)
        self.connect("delete-event", self.win_delete_event)

        self.pcc = PanelColorChanger(self.refresh_ui)

        self.set_border_width(5)
        self.__vbox = Gtk.VBox()
        self.__vbox.set_spacing(2)
        self.__vbox1 = Gtk.VBox()
        self.__vbox1.set_spacing(2)
        self.__hbox = Gtk.HBox()
        self.__hbox.set_spacing(2)

        self.__hbx = Gtk.HButtonBox()
        self.__hbx.set_layout(Gtk.ButtonBoxStyle.END)
        self.__hbx.pack_start(self.__button, False, False, 4)

        self.__da = Gtk.DrawingArea()
        self.__da.set_size_request(128, 128)

        self.__da.connect("expose-event", self.da_expose_event)

        self.__lbl_desktop_img = Gtk.Label()
        self.__lbl_desktop_img.set_use_markup(True)

        self.__red = self.__green = self.__blue = 0
        self.__lbl_red = Gtk.Label("red:")
        self.__lbl_green = Gtk.Label("green:")
        self.__lbl_blue = Gtk.Label("blue:")

        self.__vbox1.pack_start(self.__lbl_red, False, False, 2)
        self.__vbox1.pack_start(self.__lbl_green, False, False, 2)
        self.__vbox1.pack_start(self.__lbl_blue, False, False, 2)

        self.__hbox.pack_start(self.__da, False, False, 2)
        self.__hbox.pack_start(self.__vbox1, False, False, 2)

        self.__vbox.pack_start(self.__hbox, False, False, 2)
        self.__vbox.pack_start(self.__lbl_desktop_img, False, False, 0)
        self.__vbox.pack_end(self.__hbx, False, False, 5)
        self.add(self.__vbox)

    def da_expose_event(self, widget, event):
        """ Draw a rectangle filled withe dominant color of the image
        """

        # there are lots of drawing operations to be done, so do them to an
        # offscreen surface and when all is finished copy this to the window
        offscreen_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 64, 64)
        ctx = cairo.Context(offscreen_surface)

        # convert the highlight values to their cairo equivalents
        self.__red, self.__green, self.__blue = self.pcc.panel_rgb()
        pfn = os.path.split(self.pcc.wallpaper_filename())[1]
        self.__lbl_desktop_img.set_markup("<b>%s</b>" % pfn)
        self.__lbl_red.set_text("red: %s" % self.__red)
        self.__lbl_green.set_text("red: %s" % self.__green)
        self.__lbl_blue.set_text("red: %s" % self.__blue)
        red = self.__red / 255
        green = self.__green / 255
        blue = self.__blue / 255

        ctx.rectangle(0, 0, 64, 64)
        ctx.set_source_rgb(red, green, blue)
        ctx.fill()

        screen_ctx = self.__da.window.cairo_create()
        screen_ctx.rectangle(event.area.x, event.area.y,
                             event.area.width, event.area.height)
        screen_ctx.clip()

        screen_ctx.set_source_surface(offscreen_surface, 0, 0)

        screen_ctx.paint()
        ctx = None
        screen_ctx = None

    def refresh_ui(self):
        self.__da.queue_draw()

    def win_delete_event(self, widget, event, data=None):
        """Callback for the about window delete event

        """

        Gtk.main_quit()
        return True

    def win_button_press(self, widget, event):
        """
        callback for the Ok button on the About dialog

        """

        Gtk.main_quit()


def main():
    """
    main function - debugging code goes here
    """

    test_win = TestWindow()
    test_win.show_all()
    Gtk.main()

    return

if __name__ == "__main__":
    main()
