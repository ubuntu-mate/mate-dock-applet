#!/usr/bin/env python3

"""Provide an application dock applet for the MATE panel

Create a Mate panel applet and handle events generated
by it

Note: Functionality for docked apps is provided in docked_app.py

      Function for the dock is provided in dock.py

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
from . import config

if not config.WITH_GTK3:
    gi.require_version("Gtk", "2.0")
    gi.require_version("Wnck", "1.0")
else:
    gi.require_version("Gtk", "3.0")
    gi.require_version("Wnck", "3.0")

gi.require_version("MatePanelApplet", "4.0")

import os
import sys
import threading
sys.path.insert(1, config.pythondir)

from Xlib.display import Display
from Xlib import X, error
from gi.repository import Gtk
from gi.repository import MatePanelApplet
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Wnck

import xdg.DesktopEntry as DesktopEntry
from urllib.parse import urlparse

import docked_app
import dock

from log_it import log_it as log_it

drag_dropped = False   # nasty global var used to keep track of whether or not a drag-drop event has
                       # occurred

# define a list of keyboard shortcuts to be used to activate specific apps in the dock
# '<Super>1' to '<Super>0' will correspond to apps 1 to 10
# '<Super><Alt>1' to '<Super><Alt>9' will correspond to apps 11 to 20
keyb_shortcuts = ["<Super>1", "<Super>2", "<Super>3", "<Super>4", "<Super>5",
                  "<Super>6", "<Super>7", "<Super>8", "<Super>9", "<Super>0",
                  "<Super><Alt>1", "<Super><Alt>2", "<Super><Alt>3", "<Super><Alt>4", "<Super><Alt>5",
                  "<Super><Alt>6", "<Super><Alt>7", "<Super><Alt>8", "<Super><Alt>9", "<Super><Alt>0"]


def applet_button_press(widget, event, the_dock):
    """Button press event for the applet

    Handle right button press events only

    Find the app that was right clicked and make a record of it

    Args:
        widget : the widget that was clicked
        event : the event args
        the_dock : the Dock object
    """

    # we don't get click events for the right mouse button presumably
    # because the panel hijacks them in order to produce the context menu
    # However, we do get button press event for the right mouse button,
    # so we can do what we need to do here ....
    if event.button == 3:
        # right click, so save the app that was clicked because
        # the_dock.app_with_mouse is going to be set to None when the
        # right click menu appears and we move the mouse over the menu to
        # select an option
        app = the_dock.get_app_at_mouse(event.x, event.y)
        the_dock.right_clicked_app = app

        # because the right click menu is about to be shown, we need to hide
        # the window list
        the_dock.hide_win_list()
        the_dock.hide_act_list()
    elif event.button == 1:
        dx, dy = the_dock.get_drag_coords()
        if (dx == -1) and (dy == -1):
            the_dock.set_drag_coords (event.x, event.y)


def applet_button_release(widget, event, the_dock):
    """Button press event for the applet

    Handle left button release events only

    If the button is released over a non-running app, start the app

    If the button is released over a running app that isn't on the
    current workspace, change workspace

    If the button is released over a running app:
        If the app has only a single window open, activate it
        If window list is showing, hide it
        If the window list is not visible, show it

    Since the button has been released, make sure that
    icon dragging doesn't occur

    Args:
        widget : the widget that registered the release event
        event : the event args
        the_dock : the Dock object

    """

    if event.button == 1:

        the_dock.clear_drag_coords()

        # hide popups
        the_dock.hide_act_list()

        app = the_dock.get_app_at_mouse(event.x, event.y)
        if app is not None:

            start_app = app.is_running() is False
            start_app = start_app | (event.state &
                                     Gdk.ModifierType.SHIFT_MASK) != 0
            if start_app:
                app.start_app()
            else:

                # if the app only has a single window minimize or restore it, otherwise
                # allow the user to select a window from a list
                if app.get_num_windows() == 1:
                    the_dock.minimize_or_restore_windows(app, event)
                else:
                    the_dock.do_window_selection(app)

    # See https://bugs.launchpad.net/ubuntu-mate/+bug/1554128
    if event.button == 2:
        app = the_dock.get_app_at_mouse(event.x, event.y)
        if app is not None:
            the_dock.hide_win_list()
            the_dock.hide_act_list()
            app.start_app()


def applet_enter_notify(widget, event, the_dock):
    """Enter notify event for the applet

    Brighten the icon of the app which the mouse is currently over

    If another app is currently brightened, darken it to normal

    Set up the right click menu for the dock based on the app which
    the mouse is currently over

    Start the timer for showing app window lists

    Args:
        widget : the widget that registered the event i.e. the applet
        event : the event args
        the_dock : the Dock object
    """

    # get the app underneath the mouse cursor
    app = the_dock.get_app_at_mouse(event.x, event.y)

    # if an app is currently highlighted, de-highlight it
    if the_dock.app_with_mouse is not None:

        the_dock.app_with_mouse.has_mouse = False
        the_dock.app_with_mouse.queue_draw()
        the_dock.app_with_mouse = None

    # highlight the app under the mouse cursor
    if app is not None:
        app.has_mouse = True
        app.queue_draw()

        the_dock.app_with_mouse = app

        # set up the available options for the app
        the_dock.set_actions_for_app(app)
    else:
        the_dock.app_with_mouse = None


def applet_leave_notify(widget, event, the_dock):
    """Leave notify event handle for the applet

    Unbright any brightened app icon

    Args:
        widget : the widget that registered the event i.e. the applet
        event : the event args
        the_dock : the Dock object
    """

    if the_dock.app_with_mouse is not None:
        the_dock.app_with_mouse.has_mouse = False
        the_dock.app_with_mouse.queue_draw()
        the_dock.app_with_mouse = None

        the_dock.stop_act_list_timer()
        if the_dock.scrolling:
            the_dock.stop_scroll_timer()


def applet_motion_notify(widget, event, the_dock):
    """Motion notify event for the applet

    If the docked app under the mouse cursor does not have its icon
    brightened and another app has a brightened icon then darken the other app
    # icon and reset the applet tooltip text

    Then, if the docked app under the mouse cursor does not have its icon
    brightened then brighten it and setup the applet right click menu

    Args:
        widget : the widget that registered the event i.e. the applet
        event : the event args
        the_dock : the Dock object
    """

    app = the_dock.get_app_at_mouse(event.x, event.y)

    if (the_dock.app_with_mouse is not None) and \
       (the_dock.app_with_mouse != app):
        the_dock.app_with_mouse.has_mouse = False
        the_dock.app_with_mouse.queue_draw()

        widget.queue_draw()

        # because a new app is highlighted reset the window list timer and hide
        # any currently open window list and action list
        the_dock.hide_win_list()
        the_dock.reset_act_list_timer()
        the_dock.hide_act_list()

    if app is not None:

        the_dock.app_with_mouse = app

        # reset the window list timer
        the_dock.reset_act_list_timer()

        if the_dock.scrolling and app.scroll_dir != docked_app.ScrollType.SCROLL_NONE:
            the_dock.reset_scroll_timer()

        if app.has_mouse is False:
            app.has_mouse = True
            app.queue_draw()
            the_dock.app_with_mouse = app
            the_dock.set_actions_for_app(app)

    else:
        the_dock.app_with_mouse = None

        the_dock.set_actions_for_app(None)

    dx, dy = the_dock.get_drag_coords()
    if (dx != -1) and (dy != -1) and not the_dock.dragging:
        # we may need to begin a drag operation

        if widget.drag_check_threshold (dx, dy, event.x, event.y):
            target_list = widget.drag_dest_get_target_list()
            context = widget.drag_begin_with_coordinates(target_list,
                                                     Gdk.DragAction.MOVE, 1,
                                                     event, -1, -1)

            applet_drag_begin(widget, context, the_dock)

def applet_change_orient(applet, orient, the_dock):
    """Handler for applet change orientation event

    Set the dock to the new orientation and re-show the applet

    Args:
        applet : the widget that registered the event i.e. the applet
        orient : the new orientation
        the_dock : the Dock object
    """

    the_dock.set_new_orientation(orient)
    the_dock.applet.show_all()
    the_dock.show_or_hide_app_icons()


def applet_size_allocate(applet, allocation, the_dock):
    """ When the applet can play nicely with panel, ensure that it
        fits within the allocated space


    Args :
        applet : the applet
        allocation : a Gtk.Allocation - the space in which the applet must
                     fit
        the_dock : the Dock object
    """

    if the_dock.nice_sizing:
        the_dock.fit_to_alloc()
    return


def applet_change_size(applet, size, the_dock):
    """Handler for the applet change size event

    Resize the icon and recalculate the minimize location of each app in the
    dock

    Args:
        applet : the widget that registered the event i.e. the applet
        size : the new applet size
        the_dock : the Dock object
    """

    for app in the_dock.app_list:
        the_dock.set_app_icon(app, size)


def applet_scroll_event(applet, event, the_dock):
    """ Handler for the scroll event

    Call the dock's  function to move forward/backward through the active app's
    windows

    """

    # with V0.81 the dock contains a scrolled window and we now only get
    # a ScrollDirection of SMOOTH here ....
    if event.direction == Gdk.ScrollDirection.SMOOTH:
        hasdeltas, dx, dy = event.get_scroll_deltas()
        if dy < 0:
            the_dock.do_window_scroll(Gdk.ScrollDirection.DOWN, event.time)
        elif dy > 0:
            the_dock.do_window_scroll(Gdk.ScrollDirection.UP, event.time)


def applet_drag_begin(applet, context, the_dock):
    """
        Let the dock know we're dragging an icon.
        Redraw the icon of the app that's being dragged so that the user has
        visual feedback that the drag has started
        Set the drag cursor to the app icon
        Start a timer to monitor the mouse x,y and move the dragged app icon
        around the dock accordingly

    """

    # we can sometimes get spurious applet-leave events just before a drag
    # commences. This causes app_with_mouse to be set to None. Therefore we
    # may need to identify the app under the mouse ourselves...

    if the_dock.app_with_mouse is None:
        the_dock.app_with_mouse = the_dock.get_app_under_mouse()

    if the_dock.app_with_mouse is not None:
        the_dock.app_with_mouse.set_dragee(True)
        the_dock.app_with_mouse.queue_draw()

        Gtk.drag_set_icon_pixbuf(context, the_dock.app_with_mouse.app_pb,
                                 0, 0)

        the_dock.start_drag_motion_timer(the_dock.app_with_mouse)
        the_dock.dragging = True

        # finally, hide the window list if it was being shown
        the_dock.hide_win_list()
        the_dock.hide_act_list()
        the_dock.stop_scroll_timer()


def applet_drag_data_get(widget, drag_context, data, info, time):
    """
        Handler the for drag-data-get event

        Set some dummy text as data for the drag and drop
    """

    data.set_text("", -1)


def applet_drag_drop(widget, context, x, y, time, the_dock):
    """
        Handler for the drag-drop event

        The drag drop is over so:
            Call Gtk.drag-finish and indicate the drag and drop completed ok
            Let the dock know that the drag and drop has finished and redraw
            the dragged app's icon
            Stop the timer that monitors the mouse position
    """

    app = the_dock.get_dragee()
    if app is not None:
        the_dock.stop_drag_motion_timer()
        app.set_dragee(False)
        app.queue_draw()
        Gtk.drag_finish(context, True, False, time)
    else:
        # set the drag_dropped module level var so that the drag_data_received event knows
        # the dnd needs to finish
        global drag_dropped
        drag_dropped = True

        target = widget.drag_dest_find_target(context, None)
        widget.drag_get_data(context, target, time)
        return True


def applet_drag_data_received(widget, drag_context, x, y, data, info, time, the_dock):
    """ Called when data has been requested from an external source
        during a drag drop operation

    Examine the data - if it is a .desktop file and the app it relates to
    is not already in the dock, add it. If the data isn't a .desktop file
    and the app under the mouse cursor is running, activate it so that
    the dragged data can be dropped there...

    :param widget: the widget responsible for the event
    :param drag_context: the dnd context
    :param x: the x position of the mouse
    :param y:  y the y position of the mouse
    :param data: the dragged data
    :param info:
    :param time:  the time of the event
    :param the_dock: the dock ....
    """

    # examine the data  -did we get any uris ?
    uri_list = data.get_uris()
    if (uri_list is not None) and (len(uri_list) > 0):
        # when dragging .desktop files to the dock we only allow one to be added at
        # a time. Therefore we're only interested in the first item in the list
        uri = urlparse(uri_list[0])
        if uri.scheme == "file":
            # we're looking for a .desktop file
            if (uri.path != "") and (os.path.split(uri.path)[1].endswith(".desktop")) and \
               (os.path.exists(uri.path)):

                # we've got a .desktop file, so if it has been dropped we may need
                # to add it to the dock
                global drag_dropped
                if drag_dropped:
                    # add the .desktop file to the dock if it is not already there,,,
                    the_dock.add_app_to_dock(uri.path)

                    # cancel the dnd
                    Gtk.drag_finish(drag_context, True, False, time)
                    drag_dropped = False
                    return
                else:
                    # the dnd continues ....
                    Gdk.drag_status(drag_context, Gdk.DragAction.COPY, time)
                    return

    # this is not a .desktop so we need to activate the app under the mouse
    tgt_app = the_dock.get_app_under_mouse()
    the_dock.start_da_timer(tgt_app)
    Gdk.drag_status(drag_context, Gdk.DragAction.COPY, time)


def applet_drag_end(widget, context, the_dock):
    """
    Handler for the drag-end event

    This will be triggered when e.g. the use drags an icon off the panel and
    releases the mouse button ....
    Let the dock know that the drag and drop has finished and redraw the
    dragged app's icon
    Stop the timer that monitors the mouse position
    """

    the_dock.stop_drag_motion_timer()

    app = the_dock.get_dragee()
    if app is not None:
        app.set_dragee(False)
        app.queue_draw()

    the_dock.dragging = False
    the_dock.clear_drag_coords()

def applet_drag_motion(widget, context, x, y, time, the_dock):
    """ Handler for the drag-motion event

    :param widget:  - the applet
    :param context: - the dnd context
    :param x:       - x coord of the mouse
    :param y:       - y coord of the mouse
    :param time:    - the time of the event
    :param the_dock - the dock
    :return:
    """

    # if the applet isn't dragging an app icon, we may need to examine
    # the dragged data to see what we are dragging
    app = the_dock.get_dragee()
    if app is None:
        # examine the dragged data so we can decide what to do...
        tgts = context.list_targets()
        for t in tgts:
            if t.name() == "text/uri-list":
                # if the data contains uris, we need to request the data to
                # see if it contains a .desktop file
                widget.drag_get_data(context, t, time)
                return True

        # if the dragged data is anything other than a uri, we just need to activate the app under
        # the mouse...
        tgt_app = the_dock.get_app_under_mouse()
        the_dock.start_da_timer(tgt_app)
        return True
    else:
        # continue the dnd...
        Gdk.drag_status(context, Gdk.DragAction.COPY, time)

    return True


def applet_shortcut_handler(keybinder, the_dock):
    """ Handler for global keyboard shortcut presses

    Start the app if it isn't already running

    If it is already runnning cycle through its windows ...

    :param keybinder: the keybinder object with the keystring which was pressed e.g. "<Super>4"
    :param the_dock: the dock...
    """
    # get the position in the dock of the app we need to activate
    if keybinder.current_shortcut in keybinder.shortcuts:
        app_no = keybinder.shortcuts.index(keybinder.current_shortcut)

    app = the_dock.get_app_by_pos(app_no)
    if app is not None:
        start_app = app.is_running() is False
        if start_app:
            app.start_app()
        else:

            # if the app only has a single window minimize or restore it
            # otherwise scroll through all available windows
            if app.get_num_windows() == 1:
                the_dock.minimize_or_restore_windows(app, None)
            else:
                the_dock.do_window_scroll(Gdk.ScrollDirection.DOWN, 0, app)


def applet_fill(applet):
    """
    Create the applet

    Register the events that we're interested in getting events for and
    connect event handlers for them

    Create a dock and add it V/HBox to the applet


    Args:
        applet : the applet
    """

    os.chdir(os.path.expanduser("~"))

    applet.set_events(applet.get_events() | Gdk.EventMask.BUTTON_PRESS_MASK
                                          | Gdk.EventMask.BUTTON_RELEASE_MASK
                                          | Gdk.EventMask.POINTER_MOTION_MASK
                                          | Gdk.EventMask.KEY_PRESS_MASK
                                          | Gdk.EventMask.KEY_RELEASE_MASK
                                          | Gdk.EventMask.SCROLL_MASK
                                          | Gdk.EventMask.STRUCTURE_MASK)

    the_dock = dock.Dock(applet)
    the_dock.setup_dock()

    if the_dock.nice_sizing:
        applet.set_flags(MatePanelApplet.AppletFlags.EXPAND_MAJOR | MatePanelApplet.AppletFlags.EXPAND_MINOR | \
                         MatePanelApplet.AppletFlags.FLAGS_NONE)

    if not config.WITH_GTK3:
        applet.add(the_dock.box)
    else:
        applet.add(the_dock.scrolled_win)

    applet.show_all()

    # make sure that apps pinned to specific workspaces other than the current one
    # are hidden
    the_dock.show_or_hide_app_icons()

    applet.connect("enter-notify-event", applet_enter_notify, the_dock)
    applet.connect("leave-notify-event", applet_leave_notify, the_dock)
    applet.connect("motion-notify-event", applet_motion_notify, the_dock)
    applet.connect("button-press-event", applet_button_press, the_dock)
    applet.connect("button-release-event", applet_button_release, the_dock)
    applet.connect("change-orient", applet_change_orient, the_dock)
    applet.connect("change-size", applet_change_size, the_dock)
    applet.connect("scroll-event", applet_scroll_event, the_dock)
    applet.connect("size-allocate", applet_size_allocate, the_dock)

    if config.WITH_GTK3:
        # set up drag and drop - gtk3 only
        # NOTE: we don't get drag-motion events when dragging app icons within the
        # dock, making it difficult to tell where the mouse pointer is.....
        # To get around this, dock.py now contains a timer to monitor the
        # mouse x.y during these sorts of drag and drops.
        # drag-motion events do fire when dropping from other apps (e.g. caja)
        # and the drag-motion event is used in these cases

        # we allow .desktop files to be dropped on the applet, so....
        drag_tgts = [Gtk.TargetEntry.new("text/uri-list", 0, 0)]
        applet.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, drag_tgts,
                               Gdk.DragAction.MOVE)


        drag_tgts = [Gtk.TargetEntry.new("text/uri-list", 0, 0)]
        applet.drag_dest_set(Gtk.DestDefaults.MOTION, None, Gdk.DragAction.COPY)
        applet.drag_dest_add_image_targets()
        applet.drag_dest_add_text_targets()
        applet.drag_dest_add_uri_targets()

        applet.connect("drag-data-get", applet_drag_data_get)
        applet.connect("drag-drop", applet_drag_drop, the_dock)
        applet.connect("drag-end", applet_drag_end, the_dock)
        applet.connect("drag-motion", applet_drag_motion, the_dock)
        applet.connect("drag-data-received", applet_drag_data_received, the_dock)

    # set up keyboard shortcuts used to activate apps in the dock
    keybinder = GlobalKeyBinding()
    for shortcut in keyb_shortcuts:
        keybinder.grab(shortcut)
    keybinder.connect("activate", applet_shortcut_handler, the_dock)
    keybinder.start()

    applet.set_background_widget(applet)  # hack for panel transparency


def applet_factory(applet, iid, data):
    """Factory routine called when an applet needs to be created

    Create a dock applet if necessary

    Args:
        applet : the applet
        iid    : the id of the applet that needs to be created
        data   :
    Returns:
        True if we created a dock applet, False otherwise
    """

    if iid != "DockApplet":
        return False

    applet_fill(applet)

    return True


class GlobalKeyBinding(GObject.GObject, threading.Thread):
    __gsignals__ = {
        'activate': (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.display = Display()
        self.screen = self.display.screen()
        self.window = self.screen.root
        self.keymap = Gdk.Keymap().get_default()
        self.ignored_masks = self.get_mask_combinations(X.LockMask | X.Mod2Mask | X.Mod5Mask)
        self.map_modifiers()
        self.shortcuts = []

    def get_mask_combinations(self, mask):
        return [x for x in range(mask+1) if not (x & ~mask)]

    def map_modifiers(self):
        gdk_modifiers = (Gdk.ModifierType.CONTROL_MASK, Gdk.ModifierType.SHIFT_MASK, Gdk.ModifierType.MOD1_MASK,
                         Gdk.ModifierType.MOD2_MASK, Gdk.ModifierType.MOD3_MASK, Gdk.ModifierType.MOD4_MASK, Gdk.ModifierType.MOD5_MASK,
                         Gdk.ModifierType.SUPER_MASK, Gdk.ModifierType.HYPER_MASK)
        self.known_modifiers_mask = 0
        for modifier in gdk_modifiers:
            if "Mod" not in Gtk.accelerator_name(0, modifier) or "Mod4" in Gtk.accelerator_name(0, modifier):
                self.known_modifiers_mask |= modifier

    def idle(self):
        self.emit("activate")
        return False

    def activate(self):
        GLib.idle_add(self.run)

    def grab(self, shortcut):
        keycode = None
        accelerator = shortcut.replace("<Super>", "<Mod4>")
        keyval, modifiers = Gtk.accelerator_parse(accelerator)

        try:
            keycode = self.keymap.get_entries_for_keyval(keyval).keys[0].keycode
        except AttributeError:
            # In older Gtk3 the get_entries_for_keyval() returns an unnamed tuple...
            keycode = self.keymap.get_entries_for_keyval(keyval)[1][0].keycode
        modifiers = int(modifiers)
        self.shortcuts.append([keycode, modifiers])

        # Request to receive key press/release reports from other windows that may not be using modifiers
        catch = error.CatchError(error.BadWindow)
        self.window.change_attributes(onerror=catch, event_mask = X.KeyPressMask)
        if catch.get_error():
            return False

        catch = error.CatchError(error.BadAccess)
        for ignored_mask in self.ignored_masks:
            mod = modifiers | ignored_mask
            result = self.window.grab_key(keycode, mod, True, X.GrabModeAsync, X.GrabModeAsync, onerror=catch)
        self.display.flush()
        if catch.get_error():
            return False
        return True

    def run(self):
        self.running = True
        while self.running:
            event = self.display.next_event()
            if (hasattr(event, 'state')):
                modifiers = event.state & self.known_modifiers_mask
                self.current_shortcut = None
                if event.type == X.KeyPress and [event.detail, modifiers] in self.shortcuts:
                    # Track this shortcut to know which app to activate
                    self.current_shortcut = [event.detail, modifiers]
                    GLib.idle_add(self.idle)
                    self.display.allow_events(X.AsyncKeyboard, event.time)
                else:
                    self.display.allow_events(X.ReplayKeyboard, event.time)

    def stop(self):
        self.running = False
        self.ungrab()
        self.display.close()

    def ungrab(self):
        for shortcut in self.shortcuts:
            self.window.ungrab_key(shortcut[0], X.AnyModifier, self.window)


MatePanelApplet.Applet.factory_main("DockAppletFactory", True,
                                    MatePanelApplet.Applet.__gtype__,
                                    applet_factory, None)


def main():
    """Main function.

    Debugging code can go here
    """
    pass


if __name__ == "__main__":
    main()
