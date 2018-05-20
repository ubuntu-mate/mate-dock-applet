#!/usr/bin/env python3

"""Provide a configuration dialog for the dock panel applet

    Allow the user to view and set various configuration options
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

gi.require_version("MatePanelApplet", "4.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import MatePanelApplet
from gi.repository import GdkPixbuf

from random import randint

from docked_app_helpers import *


class AttentionType:
    """Class to specify the ways in which docked apps can shoe that they need attention
    """
    BLINK = 0
    SHOW_BADGE = 1


def create_frame(caption):
    """ Convenience function to create a Gtk.Frame with a desired caption
        in bold text

    Returns:
        frame - the Gtk.Frame we created

    """

    frame = Gtk.Frame(label="aaaa")
    lbl = frame.get_label_widget()
    lbl.set_use_markup(True)
    lbl.set_label("<b>%s</b>" % caption)
    frame.set_shadow_type(Gtk.ShadowType.NONE)
    frame.set_border_width(4)
    return frame


class DockPrefsWindow(Gtk.Window):
    """Class to provide the preferences window functionality

    Create and display the preferences window

    Provide methods to get and set:
        the type of indicator to be used by the dock applet
        whether pinned/unpinned apps are to be displayed from all workspaces or
        just the current workspace
        whether the colour of the MATE panels is to be set to the dominant
         colour of the current wallpaper image

    """

    def __init__(self, ok_callback, app):
        """ Constructor for the preferences window

        Create the window and its contents and display them

        set the callback for the ok button press

        Args:
            ok_callback : the method to be called when the ok button is
                          is pressed
            app         : a docked_app from which we can generate previews of the
                          various indicator and background settings

        """

        super().__init__(title="Preferences")

        self.set_skip_taskbar_hint(True)  # we don't want to be in the taskbar
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        self.PREVIEW_SIZE = 48    # the size of the preview of indicator and background settings

        self.connect("delete-event", self.win_delete_event)

        self.__app = app

        self.__app_pb = app.app_pb.scale_simple(self.PREVIEW_SIZE - 6, self.PREVIEW_SIZE - 6,
                                                GdkPixbuf.InterpType.BILINEAR)
        # setup the window contents
        self.set_border_width(5)
        if build_gtk2:
            self.__hbox = Gtk.HBox()
        else:
            self.__hbox = Gtk.Box()
            self.__hbox.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.__hbox.set_spacing(2)

        if build_gtk2:
            self.__hbox1 = Gtk.HBox()
        else:
            self.__hbox1 = Gtk.Box()
            self.__hbox1.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.__hbox1.set_spacing(2)

        self.__vbox = self.create_vbox
        self.__vbox.set_spacing(2)

        self.__cancel_btn = Gtk.Button(label="Cancel",
                                       stock=Gtk.STOCK_CANCEL)
        self.__cancel_btn.connect("button-press-event",
                                  self.win_cancel_button_press)
        self.__ok_btn = Gtk.Button(label="Ok", stock=Gtk.STOCK_OK)
        self.__ok_btn.connect("button-press-event", ok_callback)

        if build_gtk2:
            self.__hbbx = Gtk.HButtonBox()
        else:
            self.__hbbx = Gtk.ButtonBox()
            self.__hbbx.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.__hbbx.set_spacing(4)
        self.__hbbx.set_layout(Gtk.ButtonBoxStyle.END)

        self.__hbbx.pack_start(self.__ok_btn, False, False, 4)
        self.__hbbx.pack_start(self.__cancel_btn, False, False, 4)
        self.__notebook = Gtk.Notebook()

        if build_gtk2:
            self.__appearance_tbl = Gtk.Table(rows=4, columns=1,
                                              homogeneous=False)
        else:
            self.__appearance_tbl = Gtk.Grid()
            self.__appearance_tbl.set_column_spacing(4)
            self.__appearance_tbl.set_row_spacing(4)
            self.__appearance_tbl.set_row_homogeneous(False)

        self.__frame_ind_type = create_frame("Indicator Type")
        self.__rb_light_ind = Gtk.RadioButton(label="Default light")
        self.__rb_dark_ind = Gtk.RadioButton(group=self.__rb_light_ind,
                                             label="Default Dark")
        self.__rb_bar_ind = Gtk.RadioButton(group=self.__rb_light_ind,
                                            label="Single bar")
        self.__rb_no_ind = Gtk.RadioButton(group=self.__rb_light_ind,
                                           label="None")
        self.__rb_no_ind.connect("toggled", self.rb_no_ind_toggled)
        self.__rb_circ_ind = Gtk.RadioButton(group=self.__rb_light_ind,
                                             label="Circle")
        self.__rb_square_ind = Gtk.RadioButton(group=self.__rb_light_ind,
                                               label="Square")
        self.__rb_tri_ind = Gtk.RadioButton(group=self.__rb_light_ind,
                                            label="Triangle")
        self.__rb_dia_ind = Gtk.RadioButton(group=self.__rb_light_ind,
                                            label="Diamond")
        self.__rb_subway_ind = Gtk.RadioButton(group=self.__rb_light_ind,
                                               label="Subway")

        # connect event handlers so that we can update the preview when settings
        # are changed
        self.__rb_light_ind.connect("toggled", self.setting_toggled)
        self.__rb_dark_ind.connect("toggled", self.setting_toggled)
        self.__rb_bar_ind.connect("toggled", self.rb_no_ind_toggled)
        self.__rb_circ_ind.connect("toggled", self.setting_toggled)
        self.__rb_square_ind.connect("toggled", self.setting_toggled)
        self.__rb_tri_ind.connect("toggled", self.setting_toggled)
        self.__rb_dia_ind.connect("toggled", self.setting_toggled)
        self.__rb_subway_ind.connect("toggled", self.setting_toggled)

        self.__frame_preview = create_frame("Preview")
        self.__frame_preview.set_shadow_type(Gtk.ShadowType.NONE)
        self.__hbox_preview = self.create_hbox
        self.__hbox_preview.set_spacing(0)

        self.__da_preview = Gtk.DrawingArea()
        self.__da_preview.set_size_request(self.PREVIEW_SIZE * 3, self.PREVIEW_SIZE)

        self.__frame_preview_align = Gtk.Alignment(xalign=0.5, yalign=0.5,
                                                   xscale=1.0, yscale=1.0)
        self.__frame_preview_align.set_padding(0, 0, 12, 0)
        self.__hbox_preview.pack_start(self.__da_preview, False, False, 0)
        self.__frame_preview_align.add(self.__hbox_preview)
        self.__vbox_preview = self.create_vbox
        self.__vbox.set_spacing(2)
        self.__vbox_preview.pack_start(self.__frame_preview_align, False, False, 4)
        self.__frame_preview.add(self.__vbox_preview)

        # connect an event handler to draw the dark indicator
        if build_gtk2:
            self.__da_preview.connect("expose-event", self.draw_preview)
        else:
            self.__da_preview.connect("draw", self.draw_preview)

        # create ui elements for multiple indicators for open windows
        self.__cb_multi_ind = Gtk.CheckButton(label="Display an indicator for each open window")
        self.__cb_multi_ind.set_tooltip_text("Display an indicator (max 4) for each open window")
        self.__cb_multi_ind.connect("toggled", self.setting_toggled)

        if build_gtk2:
            self.__tbl_ind_type = Gtk.Table(rows=5, columns=2,
                                            homogeneous=False)
            self.__tbl_ind_type.attach(self.__rb_light_ind,
                                       0, 1, 0, 1,
                                       Gtk.AttachOptions.FILL,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)
            self.__tbl_ind_type.attach(self.__rb_dark_ind,
                                       0, 1, 1, 2,
                                       Gtk.AttachOptions.FILL,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)
            self.__tbl_ind_type.attach(self.__rb_bar_ind,
                                       0, 1, 2, 3,
                                       Gtk.AttachOptions.FILL,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)
            self.__tbl_ind_type.attach(self.__rb_circ_ind,
                                       0, 1, 3, 4,
                                       Gtk.AttachOptions.FILL,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)
            self.__tbl_ind_type.attach(self.__rb_square_ind,
                                       0, 1, 4, 5,
                                       Gtk.AttachOptions.FILL,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)
            self.__tbl_ind_type.attach(self.__rb_tri_ind,
                                       1, 2, 0, 1,
                                       Gtk.AttachOptions.FILL,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)
            self.__tbl_ind_type.attach(self.__rb_dia_ind,
                                       1, 2, 1, 2,
                                       Gtk.AttachOptions.FILL,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)
            self.__tbl_ind_type.attach(self.__rb_subway_ind,
                                       1, 2, 2, 3,
                                       Gtk.AttachOptions.FILL,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)
            self.__tbl_ind_type.attach(self.__rb_no_ind,
                                       1, 2, 3, 4,
                                       Gtk.AttachOptions.FILL,
                                       Gtk.AttachOptions.SHRINK,
                                       2, 2)
        else:
            self.__tbl_ind_type = Gtk.Grid()
            self.__tbl_ind_type.set_row_spacing(2)
            self.__tbl_ind_type.set_column_spacing(2)
            self.__tbl_ind_type.attach(self.__rb_light_ind, 0, 0, 1, 1)
            self.__tbl_ind_type.attach(self.__rb_dark_ind, 0, 1, 1, 1)
            self.__tbl_ind_type.attach(self.__rb_bar_ind, 0, 2, 1, 1)
            self.__tbl_ind_type.attach(self.__rb_circ_ind, 0, 3, 1, 1)
            self.__tbl_ind_type.attach(self.__rb_square_ind, 0, 4, 1, 1)
            self.__tbl_ind_type.attach(self.__rb_tri_ind, 1, 0, 1, 1)
            self.__tbl_ind_type.attach(self.__rb_dia_ind, 1, 1, 1, 1)
            self.__tbl_ind_type.attach(self.__rb_subway_ind, 1, 2, 1, 1)
            self.__tbl_ind_type.attach(self.__rb_no_ind, 1, 3, 1, 1)

        self.__frame_ind_type_align = Gtk.Alignment(xalign=0.5, yalign=0.5,
                                                    xscale=1.0, yscale=1.0)
        self.__frame_ind_type_align.set_padding(0, 0, 12, 0)
        self.__frame_ind_type_align.add(self.__tbl_ind_type)
        self.__frame_ind_type.add(self.__frame_ind_type_align)

        self.__frame_bg = create_frame("Active icon background")
        self.__rb_grad_bg = Gtk.RadioButton(label="Gradient fill")
        self.__rb_fill_bg = Gtk.RadioButton(group=self.__rb_grad_bg,
                                            label="Solid fill")
        self.__rb_grad_bg.connect("toggled", self.setting_toggled)
        self.__rb_fill_bg.connect("toggled", self.setting_toggled)

        self.__vbox_bg_type = self.create_vbox
        self.__vbox_bg_type.add(self.__rb_grad_bg)
        self.__vbox_bg_type.add(self.__rb_fill_bg)
        self.__frame_bg_align = Gtk.Alignment(xalign=0.5, yalign=0.5,
                                              xscale=1.0, yscale=1.0)
        self.__frame_bg_align.set_padding(0, 0, 12, 0)
        self.__frame_bg_align.add(self.__vbox_bg_type)
        self.__frame_bg.add(self.__frame_bg_align)

        if build_gtk2:
            self.__appearance_tbl.attach(self.__frame_preview, 0, 1, 0, 1,
                                         Gtk.AttachOptions.FILL,
                                         Gtk.AttachOptions.SHRINK,
                                         2, 2)
            self.__appearance_tbl.attach(self.__frame_ind_type, 0, 1, 1, 2,
                                         Gtk.AttachOptions.FILL,
                                         Gtk.AttachOptions.SHRINK,
                                         2, 2)
            self.__appearance_tbl.attach(self.__cb_multi_ind, 0, 1, 2, 3,
                                         Gtk.AttachOptions.FILL,
                                         Gtk.AttachOptions.SHRINK,
                                         2, 2)
            self.__appearance_tbl.attach(self.__frame_bg, 0, 1, 3, 4,
                                         Gtk.AttachOptions.FILL,
                                         Gtk.AttachOptions.SHRINK,
                                         2, 2)

        else:
            self.__appearance_tbl.attach(self.__frame_preview, 0, 0, 1, 1)
            self.__appearance_tbl.attach(self.__frame_ind_type, 0, 1, 1, 1)
            self.__appearance_tbl.attach(self.__cb_multi_ind, 0, 2, 1, 1)
            self.__appearance_tbl.attach(self.__frame_bg, 0, 3, 1, 1)

        self.__frame_pinned_apps = create_frame("Pinned application dock icons")
        self.__rb_pinned_all_ws = Gtk.RadioButton(label="Display on all workspaces")
        self.__rb_pinned_pin_ws = Gtk.RadioButton(label="Display only on the workspace the app was pinned",
                                                  group=self.__rb_pinned_all_ws)

        if build_gtk2:
            self.__table_pinned_apps = Gtk.Table(rows=2, columns=1,
                                                 homogeneous=False)
            self.__table_pinned_apps.attach(self.__rb_pinned_all_ws,
                                            0, 1, 0, 1,
                                            Gtk.AttachOptions.FILL,
                                            Gtk.AttachOptions.SHRINK,
                                            2, 2)
            self.__table_pinned_apps.attach(self.__rb_pinned_pin_ws,
                                            0, 1, 1, 2,
                                            Gtk.AttachOptions.FILL,
                                            Gtk.AttachOptions.SHRINK,
                                            2, 2)
        else:
            self.__table_pinned_apps = Gtk.Grid()
            self.__table_pinned_apps.set_row_spacing(2)
            self.__table_pinned_apps.set_column_spacing(2)
            self.__table_pinned_apps.attach(self.__rb_pinned_all_ws,
                                            0, 0, 1, 1)
            self.__table_pinned_apps.attach(self.__rb_pinned_pin_ws,
                                            0, 1, 1, 1)

        self.__frame_pinned_apps_align = Gtk.Alignment(xalign=0.5, yalign=0.5,
                                                       xscale=1.0, yscale=1.0)
        self.__frame_pinned_apps_align.set_padding(0, 0, 12, 0)
        self.__frame_pinned_apps_align.add(self.__table_pinned_apps)
        self.__frame_pinned_apps.add(self.__frame_pinned_apps_align)

        self.__frame_unpinned_apps = create_frame("Unpinned application dock icons")
        self.__rb_unpinned_all_ws = Gtk.RadioButton(label="Display unpinned apps from all workspaces")
        self.__rb_unpinned_cur_ws = Gtk.RadioButton(group=self.__rb_unpinned_all_ws,
                                    label="Display unpinned apps only from current workspace")

        if build_gtk2:
            self.__table_unpinned_apps = Gtk.Table(rows=2, columns=1,
                                                   homogeneous=False)
            self.__table_unpinned_apps.attach(self.__rb_unpinned_all_ws,
                                              0, 1, 0, 1,
                                              Gtk.AttachOptions.FILL,
                                              Gtk.AttachOptions.SHRINK,
                                              2, 2)
            self.__table_unpinned_apps.attach(self.__rb_unpinned_cur_ws,
                                              0, 1, 1, 2,
                                              Gtk.AttachOptions.FILL,
                                              Gtk.AttachOptions.SHRINK,
                                              2, 2)
        else:
            self.__table_unpinned_apps = Gtk.Grid()
            self.__table_unpinned_apps.set_row_spacing(2)
            self.__table_unpinned_apps.set_column_spacing(2)
            self.__table_unpinned_apps.attach(self.__rb_unpinned_all_ws,
                                              0, 0, 1, 1)
            self.__table_unpinned_apps.attach(self.__rb_unpinned_cur_ws,
                                              0, 1, 1, 1)

        self.__frame_unpinned_apps_align = Gtk.Alignment(xalign=0.5, yalign=0.5,
                                                         xscale=1.0, yscale=1.0)
        self.__frame_unpinned_apps_align.set_padding(0, 0, 12, 0)
        self.__frame_unpinned_apps_align.add(self.__table_unpinned_apps)
        self.__frame_unpinned_apps.add(self.__frame_unpinned_apps_align)

        self.__cb_win_cur_ws = Gtk.CheckButton(label="Display indicators/window list items for current workspace only")

        self.__notes_scrolled_win = Gtk.ScrolledWindow()
        self.__notes_scrolled_win.set_policy(Gtk.PolicyType.NEVER,
                                             Gtk.PolicyType.AUTOMATIC)
        self.__tv_notes = Gtk.TextView()
        self.__tv_notes.set_wrap_mode(Gtk.WrapMode.WORD)
        self.__tv_notes.set_editable(False)
        self.__notes_text_buf = Gtk.TextBuffer()

        self.__tv_notes.set_buffer(self.__notes_text_buf)
        iter = self.__notes_text_buf.get_start_iter()
        self.__notes_text_buf.insert(iter,
                                     "Note: when displaying pinned apps only on the workspace where they were " +
                                     "created, it is a good idea to also select the 'Display unpinned apps' " +
                                     "and 'Display indicators/window list' items for the current workspace " +
                                     "only options.")

        self.__ws_vbox = self.create_vbox
        self.__ws_vbox.set_spacing(2)
        self.__ws_vbox.pack_start(self.__frame_pinned_apps, False, False, 4)
        self.__ws_vbox.pack_start(self.__frame_unpinned_apps, False, False, 4)
        self.__ws_vbox.pack_start(self.__cb_win_cur_ws, False, False, 4)
        self.__ws_vbox.pack_end(self.__tv_notes, False, False, 4)

        self.__frame_win_sel = create_frame("Window selection")
        self.__rb_win_list = Gtk.RadioButton(label="From applet's window list")
        self.__rb_win_thumb = Gtk.RadioButton(group=self.__rb_win_list,
                                              label="From window thumbnail previews (requires Compiz)")
        self.__table_win_sel = Gtk.Table(rows=2, columns=1,
                                         homogeneous=False)
        self.__table_win_sel.attach(self.__rb_win_list,
                                    0, 1, 0, 1,
                                    Gtk.AttachOptions.FILL,
                                    Gtk.AttachOptions.SHRINK,
                                    2, 2)
        self.__table_win_sel.attach(self.__rb_win_thumb,
                                    0, 1, 1, 2,
                                    Gtk.AttachOptions.FILL,
                                    Gtk.AttachOptions.SHRINK,
                                    2, 2)

        self.__frame_win_sel_align = Gtk.Alignment(xalign=0.5, yalign=0.5,
                                                   xscale=1.0, yscale=1.0)
        self.__frame_win_sel_align.set_padding(0, 0, 12, 0)
        self.__frame_win_sel_align.add(self.__table_win_sel)
        self.__frame_win_sel.add(self.__frame_win_sel_align)

        self.__win_sel_vbox = self.create_vbox
        self.__win_sel_vbox.set_spacing(2)
        self.__win_sel_vbox.pack_start(self.__frame_win_sel, False,
                                       False, 4)

        self.__frame_spc = create_frame("App spacing")
        if build_gtk2:
            self.__sb_spc = Gtk.SpinButton()
            self.__sb_spc.set_adjustment(Gtk.Adjustment(0, 0, 7, 1, 4))
        else:
            self.__sb_spc = Gtk.SpinButton.new_with_range(0, 7, 1)

        self.__sb_spc.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self.__sb_spc.set_numeric(True)
        self.__sb_spc.set_max_length(1)
        self.__sb_spc.set_snap_to_ticks(True)

        self.__frame_spc_align = Gtk.Alignment(xalign=0.5, yalign=0.5,
                                               xscale=1.0, yscale=1.0)
        self.__frame_spc_align.set_padding(0, 0, 12, 300)
        self.__frame_spc_align.add(self.__sb_spc)
        self.__frame_spc.add(self.__frame_spc_align)

        self.__frame_color_change = create_frame("Panel colour")
        self.__cb_panel_color_change = Gtk.CheckButton(label="Change panel colour to match wallpaper")
        self.__cb_panel_color_change.connect("toggled", self.color_change_toggled)
        self.__cb_dock_panel_only = Gtk.CheckButton(label="Change colour of dock's panel only")

        if build_gtk2:
            self.__table_color_change = Gtk.Table(rows=3, columns=1,
                                                  homogeneous=False)
            self.__table_color_change.attach(self.__cb_panel_color_change,
                                             0, 1, 0, 1,
                                             Gtk.AttachOptions.FILL,
                                             Gtk.AttachOptions.SHRINK,
                                             2, 2)
            self.__table_color_change.attach(self.__cb_dock_panel_only,
                                             0, 1, 1, 2,
                                             Gtk.AttachOptions.FILL,
                                             Gtk.AttachOptions.SHRINK,
                                             2, 2)

        else:
            self.__table_color_change = Gtk.Grid()
            self.__table_color_change.set_row_spacing(2)
            self.__table_color_change.set_column_spacing(2)

            self.__table_color_change.attach(self.__cb_panel_color_change,
                                             0, 0, 1, 1)
            self.__table_color_change.attach(self.__cb_dock_panel_only,
                                             0, 1, 1, 1)

        self.__frame_color_change_align = Gtk.Alignment(xalign=0.5, yalign=0.5,
                                                        xscale=1.0, yscale=1.0)
        self.__frame_color_change_align.set_padding(0, 0, 12, 0)
        self.__frame_color_change_align.add(self.__table_color_change)
        self.__frame_color_change.add(self.__frame_color_change_align)

        if not build_gtk2:
            self.__frame_dock_size = create_frame("Dock size")
            self.__rb_variable_ds = Gtk.RadioButton(label="Variable - expand or contract as necessary")
            self.__rb_fixed_ds = Gtk.RadioButton(group=self.__rb_variable_ds,
                                                 label="Fixed")

            self.__lbl_fixed_size = Gtk.Label("Display up to ")

            self.__sb_fixed_size = Gtk.SpinButton.new_with_range(2, 64, 1)
            self.__sb_fixed_size.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
            self.__sb_fixed_size.set_numeric(True)
            self.__sb_fixed_size.set_max_length(2)
            self.__sb_fixed_size.set_snap_to_ticks(True)

            self.__lbl_fixed_size1 = Gtk.Label(" app icons")

            self.__hbox_fixed_size = self.create_hbox
            self.__hbox_fixed_size.set_spacing(2)
            self.__hbox_fixed_size.pack_start(self.__lbl_fixed_size, False, False, 4)
            self.__hbox_fixed_size.pack_start(self.__sb_fixed_size, False, False, 4)
            self.__hbox_fixed_size.pack_start(self.__lbl_fixed_size1, False, False, 4)

            self.__table_dock_size = Gtk.Grid()
            self.__table_dock_size.set_row_spacing(2)
            self.__table_dock_size.set_column_spacing(2)

            self.__table_dock_size.attach(self.__rb_variable_ds,
                                             0, 0, 1, 1)
            self.__table_dock_size.attach(self.__rb_fixed_ds,
                                             0, 1, 1, 1)
            self.__table_dock_size.attach(self.__hbox_fixed_size, 0, 2, 1, 1)

            self.__frame_dock_size_align = Gtk.Alignment(xalign=0.5, yalign=0.5,
                                                      xscale=1.0, yscale=1.0)
            self.__frame_dock_size_align.set_padding(0, 0, 12, 0)
            self.__frame_dock_size_align.add(self.__table_dock_size)
            self.__frame_dock_size.add(self.__frame_dock_size_align)

        self.__cb_pan_act = Gtk.CheckButton(label="Disable popup action list " +
                                            "and show app actions\non panel " +
                                            "right click menu only")

        self.__panel_vbox = self.create_vbox
        self.__panel_vbox.set_spacing(2)
        self.__panel_vbox.pack_start(self.__frame_spc, False, False, 4)
        self.__panel_vbox.pack_start(self.__frame_color_change,
                                     False, False, 4)
        if not build_gtk2:
            self.__panel_vbox.pack_start(self.__frame_dock_size,
                                         False, False, 4)

        self.__panel_vbox.pack_start(self.__cb_pan_act,
                                     False, False, 4)

        self.__frame_fb_bar_col = create_frame("Fallback bar indicator colour")
        self.__lbl_fb_bar_col = Gtk.Label("Colour")
        self.__cbtn_fb_bar_col = Gtk.ColorButton()
        self.__cbtn_fb_bar_col.set_tooltip_text("Colour used for drawing bar indicators when theme colour " +
                                                "cannot be determined or when using Gtk2")

        self.__fb_bar_col_hbox = self.create_hbox
        self.__fb_bar_col_hbox.set_spacing(2)
        self.__fb_bar_col_hbox.pack_start(self.__lbl_fb_bar_col, False, False, 2)
        self.__fb_bar_col_hbox.pack_start(self.__cbtn_fb_bar_col, True, True, 2)
        self.__fb_bar_col_vbox = self.create_vbox
        self.__fb_bar_col_vbox.set_spacing(2)
        self.__fb_bar_col_vbox.pack_start(self.__fb_bar_col_hbox, False, False, 2)
        self.__frame_fb_bar_col.add(self.__fb_bar_col_vbox)

        self.__frame_attention_type = create_frame("Action when apps need attention")
        self.__rb_attention_blink = Gtk.RadioButton(label="Blink the app icon")
        self.__rb_attention_badge = Gtk.RadioButton(label="Show a badge on the app icon",
                                                    group=self.__rb_attention_blink)

        if build_gtk2:
            self.__table_attention_type = Gtk.Table(rows=2, columns=1,
                                                    homogeneous=False)
            self.__table_attention_type.attach(self.__rb_attention_blink,
                                               0, 1, 0, 1,
                                               Gtk.AttachOptions.FILL,
                                               Gtk.AttachOptions.SHRINK,
                                               2, 2)
            self.__table_attention_type.attach(self.__rb_attention_badge,
                                               0, 1, 1, 2,
                                               Gtk.AttachOptions.FILL,
                                               Gtk.AttachOptions.SHRINK,
                                               2, 2)

        else:
            self.__table_attention_type = Gtk.Grid()
            self.__table_attention_type.set_row_spacing(2)
            self.__table_attention_type.set_column_spacing(2)

            self.__table_attention_type.attach(self.__rb_attention_blink,
                                               0, 0, 1, 1)
            self.__table_attention_type.attach(self.__rb_attention_badge,
                                               0, 1, 1, 1)

        self.__frame_attention_type_align = Gtk.Alignment(xalign=0.5, yalign=0.5,
                                                          xscale=1.0, yscale=1.0)
        self.__frame_attention_type_align.set_padding(0, 0, 12, 0)
        self.__frame_attention_type_align.add(self.__table_attention_type)
        self.__frame_attention_type.add(self.__frame_attention_type_align)

        self.__frame_pdel = create_frame("Popup Delay(s)")
        if build_gtk2:
            self.__sb_pdel = Gtk.SpinButton()
            self.__sb_pdel.set_adjustment(Gtk.Adjustment(1.0, 0.1, 5.0, 0.1, 1))
        else:
            self.__sb_pdel = Gtk.SpinButton.new_with_range(0.1, 5, 0.1)

        self.__sb_pdel.set_digits(1)

        self.__sb_pdel.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self.__sb_pdel.set_numeric(True)
        self.__sb_pdel.set_max_length(3)
        self.__sb_pdel.set_snap_to_ticks(True)

        self.__frame_pdel_align = Gtk.Alignment(xalign=0.5, yalign=0.5,
                                                xscale=1.0, yscale=1.0)
        self.__frame_pdel_align.set_padding(0, 0, 12, 300)
        self.__frame_pdel_align.add(self.__sb_pdel)
        self.__frame_pdel.add(self.__frame_pdel_align)

        self.__misc_vbox = self.create_vbox
        self.__misc_vbox.set_spacing(2)
        self.__misc_vbox.pack_start(self.__frame_fb_bar_col, False, False, 4)
        self.__misc_vbox.pack_start(self.__frame_attention_type, False, False, 4)
        self.__misc_vbox.pack_start(self.__frame_pdel, False, False, 4)

        self.__vbox.pack_start(self.__notebook, True, True, 4)
        self.__notebook.append_page(self.__appearance_tbl, Gtk.Label("Appearance"))
        self.__notebook.append_page(self.__ws_vbox, Gtk.Label("Workspaces"))
        self.__notebook.append_page(self.__win_sel_vbox, Gtk.Label("Windows"))
        self.__notebook.append_page(self.__panel_vbox,
                                    Gtk.Label("Panel Options"))
        self.__notebook.append_page(self.__misc_vbox, Gtk.Label("Misc"))

        self.__vbox.pack_start(Gtk.HSeparator(), True, True, 4)
        self.__vbox.pack_start(self.__hbbx, False, False, 0)

        self.set_fallback_bar_col([192, 128, 0])
        self.add(self.__vbox)
        self.show_all()

    @property
    def create_vbox(self):
        """
            Convenience function to create a Gtk2 VBox or a Gtk3 Box
            oriented vertically

        Returns:
            the vbox/box we created
        """

        if build_gtk2:
            vbox = Gtk.VBox()
        else:
            vbox = Gtk.Box()
            vbox.set_orientation(Gtk.Orientation.VERTICAL)

        return vbox

    @property
    def create_hbox(self):
        """
            Convenience function to create a Gtk2 HBox or a Gtk3 Box
            oriented horizontally

        Returns:
            the hbox/box we created
        """

        if build_gtk2:
            hbox = Gtk.HBox()
        else:
            hbox = Gtk.Box()
            hbox.set_orientation(Gtk.Orientation.HORIZONTAL)

        return hbox

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

    def draw_preview(self, drawing_area, event):
        """Draw a preview of the current appearance settings

        Draw a dark or light background to represent the panel
        Draw an appropriate type of active background
        Draw an app icon
        Draw the appropriate type of indicator (or no indicator)

        Args:

            drawing_area : our drawing area that caused the event
            event        : the event parameters
        """

        if build_gtk2:
            tgt_ctx = self.__da_preview.window.cairo_create()
        else:
            tgt_ctx = event

        # if a dark indicator is set, we draw a light background, otherwise a
        # dark background
        if self.__rb_dark_ind.get_active():
            tgt_ctx.set_source_rgb(0.85, 0.85, 0.85)
        else:
            tgt_ctx.set_source_rgb(0.15, 0.21, 0.15)
        tgt_ctx.rectangle(0, 0, self.PREVIEW_SIZE * 3, self.PREVIEW_SIZE)
        tgt_ctx.fill()

        app_size = self.PREVIEW_SIZE + ind_extra_s(self.get_indicator_type())
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, app_size, self.PREVIEW_SIZE)
        ctx = cairo.Context(surface)

        # draw the app icon
        Gdk.cairo_set_source_pixbuf(ctx, self.__app_pb, 3, 3)
        ctx.paint()

        # draw the active background - first we need the colour of the background in cairo
        # values
        red = self.__app.highlight_color.r / 255
        green = self.__app.highlight_color.g / 255
        blue = self.__app.highlight_color.b / 255

        if self.__rb_grad_bg.get_active():
            bgd = DefaultBackgroundDrawer(ctx, self.PREVIEW_SIZE,
                                          MatePanelApplet.AppletOrient.UP, red, green, blue)
        else:
            bgd = AlphaFillBackgroundDrawer(ctx, self.PREVIEW_SIZE,
                                            MatePanelApplet.AppletOrient.UP, red, green, blue, 0.5)

        bgd.draw()

        # draw the indicator(s) if necessary
        if not self.__rb_no_ind.get_active():
            # if we're showing indicators for each open window, show multiple indicators
            if self.__cb_multi_ind.get_active():
                num_ind = randint(2, 4)
            else:
                num_ind = 1

            if self.__rb_light_ind.get_active():
                ind = DefaultLightInd(ctx, self.PREVIEW_SIZE,
                                      MatePanelApplet.AppletOrient.UP, num_ind)
            elif self.__rb_dark_ind.get_active():
                ind = DefaultDarkInd(ctx, self.PREVIEW_SIZE,
                                     MatePanelApplet.AppletOrient.UP, num_ind)
            elif self.__rb_bar_ind.get_active():
                ind = ThemeBarInd(ctx, self.PREVIEW_SIZE, MatePanelApplet.AppletOrient.UP,
                                  self.__app.applet)
            elif self.__rb_circ_ind.get_active():
                ind = ThemeCircleInd(ctx, self.PREVIEW_SIZE, MatePanelApplet.AppletOrient.UP,
                                     self.__app.applet, num_ind)
            elif self.__rb_square_ind.get_active():
                ind = ThemeSquareInd(ctx, self.PREVIEW_SIZE, MatePanelApplet.AppletOrient.UP,
                                     self.__app.applet, num_ind)
            elif self.__rb_tri_ind.get_active():
                ind = ThemeTriInd(ctx, self.PREVIEW_SIZE, MatePanelApplet.AppletOrient.UP,
                                  self.__app.applet, num_ind)
            elif self.__rb_dia_ind.get_active():
                ind = ThemeDiaInd(ctx, self.PREVIEW_SIZE, MatePanelApplet.AppletOrient.UP,
                                  self.__app.applet, num_ind)
            elif self.__rb_subway_ind.get_active():
                active = bool(randint(0, 1))
                ind = SubwayInd(ctx, self.PREVIEW_SIZE, MatePanelApplet.AppletOrient.UP,
                                self.__app.applet, num_ind, surface, active)
            else:
                ind = None

            if ind is not None:
                ind.draw()

            # now draw to the screen
            if build_gtk2:
                tgt_ctx = drawing_area.window.cairo_create()
                tgt_ctx.rectangle(event.area.x, event.area.y,
                                  event.area.width, event.area.height)
                tgt_ctx.clip()

                tgt_ctx.set_source_surface(surface, self.PREVIEW_SIZE, 0)

                tgt_ctx.paint()
                tgt_ctx = None
            else:
                tgt_ctx.set_source_surface(surface, self.PREVIEW_SIZE, 0)
                tgt_ctx.paint()

            ctx = None

    def color_change_toggled(self, widget):
        """Handler for the panel color change checkbox toggled event

        If the panel colour change option is selected, enable the checkbox that
        specifies whether or not all panels are to change colour

        """

        self.__cb_dock_panel_only.set_sensitive(self.__cb_panel_color_change.get_active())

    def setting_toggled(self, widget):
        """ Handler for updating the preview when appearance settings are changed

        Args:
            widget: the widget the caused the event
        """
        self.__da_preview.queue_draw()

    def rb_no_ind_toggled(self, widget):
        """ Handler for the no indicator radio button toggled event, also
            used by the bar indicator rb

        If either the no indicator or bar indicator ption is selected, disable
        the multiple indicator checkbox

        Update the appearance preview
        """

        self.__cb_multi_ind.set_sensitive(self.__rb_no_ind.get_active() is not True and
                                          self.__rb_bar_ind.get_active() is not True)
        self.setting_toggled(widget)

    def set_dock_size_visible(self, vis):
        """ Set whether the dock size frame is visible or not

        Params: vis - bool

        """

        self.__frame_dock_size.set_visible(vis)

    def get_indicator_type(self):
        """Get the indicator type specified in the preferences window.

        Returns : IndicatorType
        """

        if self.__rb_light_ind.get_active():
            return IndicatorType.LIGHT
        elif self.__rb_dark_ind.get_active():
            return IndicatorType.DARK
        elif self.__rb_bar_ind.get_active():
            return IndicatorType.TBAR
        elif self.__rb_circ_ind.get_active():
            return IndicatorType.TCIRC
        elif self.__rb_square_ind.get_active():
            return IndicatorType.TSQUARE
        elif self.__rb_tri_ind.get_active():
            return IndicatorType.TTRI
        elif self.__rb_dia_ind.get_active():
            return IndicatorType.TDIA
        elif self.__rb_subway_ind.get_active():
            return IndicatorType.SUBWAY
        else:
            return IndicatorType.NONE

    def set_indicator(self, indicator):
        """Set the indicator type

        Args : indicator - an IndicatorType
        """

        if indicator == IndicatorType.LIGHT:
            self.__rb_light_ind.set_active(True)
        elif indicator == IndicatorType.DARK:
            self.__rb_dark_ind.set_active(True)
        elif indicator == IndicatorType.TBAR:
            self.__rb_bar_ind.set_active(True)
        elif indicator == IndicatorType.TCIRC:
            self.__rb_circ_ind.set_active(True)
        elif indicator == IndicatorType.TSQUARE:
            self.__rb_square_ind.set_active(True)
        elif indicator == IndicatorType.TTRI:
            self.__rb_tri_ind.set_active(True)
        elif indicator == IndicatorType.TDIA:
            self.__rb_dia_ind.set_active(True)
        elif indicator == IndicatorType.SUBWAY:
            self.__rb_subway_ind.set_active(True)
        else:
            self.__rb_no_ind.set_active(True)

    def get_multi_ind(self):
        """Gets whether or not to use display an indicator for each open
           window that a docked app has

        Returns: boolean
        """

        return self.__cb_multi_ind.get_active()

    def set_bg(self, bg):
        """ Set the active icon background type

        Args : bg - an ActiveBgType
        """

        if bg == ActiveBgType.GRADIENT:
            self.__rb_grad_bg.set_active(True)
        else:
            self.__rb_fill_bg.set_active(True)

    def get_bg(self):
        """ Gets the currently selected active icon background type

        Returns : An ActiveBgType

        """

        if self.__rb_grad_bg.get_active():
            return ActiveBgType.GRADIENT
        else:
            return ActiveBgType.ALPHAFILL

    def set_multi_ind(self, use_multi_ind):
        """Sets whether or not to display multiple indicators

        Args: use_multi_ind - boolean
        """

        self.__cb_multi_ind.set_active(use_multi_ind)

    def get_show_unpinned_apps_on_all_ws(self):
        """Gets whether unpinned apps are displayed in the dock on all workspaces

        Returns: boolean
        """

        return self.__rb_unpinned_all_ws.get_active()

    def set_show_unpinned_apps_on_all_ws(self, show_on_all):
        """Sets whether unpinned apps are displayed in the dock on all workspaces

        Args: show_on_all - boolean
        """

        if show_on_all:
            self.__rb_unpinned_all_ws.set_active(True)
        else:
            self.__rb_unpinned_cur_ws.set_active(True)

    def get_show_pinned_apps_on_all_ws(self):
        """Gets whether pinned apps are displayed in the dock on all workspaces
           or just on the workspace where they were created

        Returns: boolean
        """

        return self.__rb_pinned_all_ws.get_active()

    def set_show_pinned_apps_on_all_ws(self, show_on_all):
        """Sets whether pinned apps are displayed in the dock on all workspaces

        Args: show_on_all - boolean
        """

        if show_on_all:
            self.__rb_pinned_all_ws.set_active(True)
        else:
            self.__rb_pinned_pin_ws.set_active(True)

    def get_pan_act(self):
        """ Gets whether or not the show the action list on the panel
            right click menu, rather than as a popup

            Returns: boolean
        """

        return self.__cb_pan_act.get_active()

    def set_pan_act(self, pan_act):
        """ Sets whether or not the show the action list on the panel
            right click menu, rather than as a popup

            Args:
                pan_act: boolean
        """

        self.__cb_pan_act.set_active(pan_act)

    def get_use_win_list(self):
        """Gets whether to use the dock's window list to select windows
        or whether to use Compiz thumbnail previews

            Returns: boolean
        """

        return self.__rb_win_list.get_active()

    def set_use_win_list(self, use_win_list):
        """Sets whether to use the dock's window list to select windows
        or whether to use Compiz thumbnail previews

        Args: use_win_list - boolean
        """

        if use_win_list:
            self.__rb_win_list.set_active(True)
        else:
            self.__rb_win_thumb.set_active(True)

    def get_change_panel_color(self):
        """ Get whether the panel colour is to be changed according to the
            current wallpaper

        Returns: boolean
        """

        return self.__cb_panel_color_change.get_active()

    def set_change_panel_color(self, change_color):
        """ Sets whether the panel color is to be changed according to the
            current wallpaper

        Args: change_color - boolean
        """

        self.__cb_panel_color_change.set_active(change_color)

    def get_change_dock_color_only(self):
        """ Get whether only the panel containing the dock is to be changed
            when setting the panel colour according to the current wallpaper

        Returns: boolean
        """

        return self.__cb_dock_panel_only.get_active()

    def rb_variable_ds_toggled(self, widget):
        """ Handler for dock fixed size setting changes

        Update the ui according to the current settingd

        """

        size_fixed = self.__rb_fixed_ds.get_active()

        # enable/diable the parts of the interface that allow the user to set the number
        # of app icons in a fixed size dock
        self.__lbl_fixed_size.set_sensitive(size_fixed)
        self.__sb_fixed_size.set_sensitive(size_fixed)
        self.__lbl_fixed_size1.set_sensitive(size_fixed)

    def set_fixed_size(self, fixed_size, num_icons, mutiny_layout):
        """ Set whether or not the dock is a fixed size, and if so the number
            of app icons it can contain before enabling scrolling

        If we're using the Mutiny panel layout, disable all fixed size settings

        Params:
            fixed_size : bool - whether or not the dock is a fixed size
            num_icons  : int - the number of icons
            mutiny_layout : bool - indicates whether or not we're using the Mutiny layour
        """

        self.__rb_variable_ds.connect("toggled", self.rb_variable_ds_toggled)

        if not mutiny_layout:
            self.__rb_fixed_ds.set_sensitive(True)
            self.__rb_variable_ds.set_sensitive(True)
            self.__rb_fixed_ds.set_active(fixed_size)
            self.rb_variable_ds_toggled(self.__rb_variable_ds) # ensure ui is updated
            self.__sb_fixed_size.set_value(num_icons)

        else:
            self.__lbl_fixed_size.set_sensitive(False)
            self.__sb_fixed_size.set_sensitive(False)
            self.__lbl_fixed_size1.set_sensitive(False)
            self.__rb_fixed_ds.set_sensitive(False)
            self.__rb_variable_ds.set_sensitive(False)
            self.__rb_variable_ds.disconnect_by_func(self.rb_variable_ds_toggled)
            self.__rb_fixed_ds.set_active(fixed_size)

    def get_fixed_size(self):
        """ Get the dock fixed size settings

        Note: the dock should not call this method if the Mutiny panel layout is being
              used

        Returns:
            a bool - whether or not the dock is of fixed size
            an int - the number of app icons in a fixed size dock
        """

        return self.__rb_fixed_ds.get_active(), self.__sb_fixed_size.get_value()

    def set_change_dock_color_only(self, dock_only):
        """ Sets whether only the panel containing the dock is to be changed
            when settings the panel colour according to the current wallpaper

        Args: dock_only - boolean
        """

        self.__cb_dock_panel_only.set_active(dock_only)

    def get_win_cur_ws_only(self):
        """ Gets whether the dock will show indicators/window list items for
            the current workspace only

        Returns: boolean
        """

        return self.__cb_win_cur_ws.get_active()

    def set_win_cur_ws_only(self, win_cur_ws_only):
        """ Sets whether the dock will show indicators/window list items for
            the current workspace only

        Args: win_cur_ws_only - boolean
        """

        self.__cb_win_cur_ws.set_active(win_cur_ws_only)

    def set_fallback_bar_col(self, colrgb):
        """
            Set the colour of the fallback bar indicator colour button

        Args:
            colrgb : a list containing the r,g and b colour components(0-255) as strings
        """

        colstr = "#%0.2X%0.2X%0.2X" % (int(colrgb[0]), int(colrgb[1]), int(colrgb[2]))

        if build_gtk2:
            cbrgba = Gdk.color_parse(colstr)
            self.__cbtn_fb_bar_col.set_color(color=cbrgba)
        else:
            cbrgba = Gdk.RGBA()
            cbrgba.parse(colstr)
            self.__cbtn_fb_bar_col.set_rgba(cbrgba)

        self.__cbtn_fb_bar_col.set_use_alpha(False)

    def get_fallback_bar_col(self):
        """
            Get the colour of the fallback bar indicator colour button

        Returns:
            a list containing the r, g, and b colour components(0-255)
        """

        if build_gtk2:
            cbrgba = self.__cbtn_fb_bar_col.get_color()
        else:
            cbrgba = self.__cbtn_fb_bar_col.get_rgba().to_color()

        return ["%s" % int(cbrgba.red / 256), "%s" % int(cbrgba.green / 256), "%s" % int(cbrgba.blue / 256)]

    def set_app_spacing(self, spacing):
        """ Set the amount of space between icons in the dock
        """

        self.__sb_spc.set_value(spacing)
    
    def get_app_spacing(self):
        """
            Get the amount of space between icons in the dock
            
        :return: int
         
        """

        self.__sb_spc.update()
        return self.__sb_spc.get_value()

    def set_attention_type(self, attention_type):
        """ Set the attention type
        
        Args : attention_type: An AttentionType e.g. AttentionType.BLINK
        """
        if attention_type == AttentionType.BLINK:
            self.__rb_attention_blink.set_active(True)
        else:
            self.__rb_attention_badge.set_active(True)

    def get_attention_type(self):
        """
            Get the attention type
            
        Returns: An AttentionType
                    
        """

        if self.__rb_attention_blink.get_active():
            return AttentionType.BLINK
        else:
            return AttentionType.SHOW_BADGE

    def set_popup_delay(self, delay):
        """ Set the amount of space between icons in the dock

        Args:
            delay: the delay in ms
        """

        # convert delay to seconds
        self.__sb_pdel.set_value(delay/1000)

    def get_popup_delay(self):
        """
            Get the popup delay, converting from seconds to ms

        :return: int

        """

        self.__sb_pdel.update()
        return int(self.__sb_pdel.get_value()*1000)


def main():
    """main function - debug code can go here"""
   # dpw = DockPrefsWindow(Gtk.main_quit)
   # Gtk.main()


if __name__ == "__main__":
    main()
