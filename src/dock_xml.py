#!/usr/bin/env python3

"""Read and write applet xml configuration files.

Provide functionality allowing the dock applets configuration to be saved
and loaded.

Store the configuration in a specified XML file

The file will contain the following information:
    : a list of all pinned app's .desktop files
    : the indicator type (light or dark)
    : whether unpinned apps from all workspaces are to be displayed
    : whether an indicator for each open window is to be displayed


Also provide the ability to read an xml file which contains details
of apps which are difficult to match with their respective .desktop
files and which specifies the .desktop file to use
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

import xml.etree.ElementTree as ET
import sys
import os
import platform


def write_xml(filename, desktop_files, light_ind, show_all_apps, multi_ind,
              use_dock_win_list, win_from_cur_ws_only,
              panel_change_color, dock_panel_change_only, use_panel_act_list,
              active_icon_bg, fallback_bar_col, spacing, attention_type,
              popup_delay, saved_configs, pa_on_all_ws, dock_fixed_size):
    """ Write the xml file using the specified information

    The xml file will be in e.g. the following format:

        <root>
            <pinned_apps>
                <desktop_file name="name1"/>
                <desktop_file name="name2"/>
                etc...
            </pinned_apps>
            <light_ind>int</>
            <show_all_apps>True or False</>
            <multi_ind>True or False</>
            <click_restore_last_active>True or False</>
            <win_from_cur_ws_only>True or False</>
            <panel_change_color>True or False</>
            <dock_panel_change_only>True or False</>
            ...
            ...

        </root>

    Args:
        filename : the filename to use. If the file already exists it will be
                   overwritten.
        desktop_files: a list containing the names of the applet's pinned app's
                       .desktop files e.g. ['pluma.desktop']
        light_ind : int - the indicator type e.g. light, dark, bar to be used
        show_all_apps : boolean - Whether or not unpinned apps from all
                        workspaces are to be shown
        multi_ind : Whether indicators for each of an app's open windows are to
                    be shown
        use_dock_win_list: : boolean : whether to use the applet's own window list
                                  for switching between an app's open windows,
                                  or to use Compiz thumbnail previews
        win_from_cur_ws_only: boolean - If True, indicators and window list
                              items will only be shown for windows on the
                              current workspace (new with V0.67)
        panel_change_color : boolean - Whether or not MATE panels are to change
                             color according to the desktop wallpaper (new
                             with V0.66)
        dock_panel_change_only : boolean - whether panel colour changes are to
                                 limited to only the panel containing the dock
                                 applet (new with V0.66)
        use_panel_act_list:  boolean - whether to display an app's actions in
                                 the panel right click menu, as opposed to
                                 using the popup action list
        active_icon_bg:      int - the type of active icon background e.g.
                                   gradient or fill
        fallback_bar_col:   a list of the rgb elements of a color to be used
                            for bar indicators when the theme highlight colour
                            cannot be read
        spacing : the amount of spacing (0-8) between apps in the dock
        attention_type : how a docked app notifies the user when an app requires
                         attention
        popup_delay : the delay before action/windows lists appear

        saved_configs : a list of tuples containing details of the pinned app
                        config. Each tuple contains the
                        following:
                            string - the config name
                            string - the workspace (if any) the config is to be
                                     automatically loaded for
                            string - a .desktop filename specifying a pinned app
                            string - another .desktop filename etc. etc.
        pa_on_all_ws : boolean - whether pinned apps appear on all workspaces or
                                 only the workspace where they were pinned

        dock_fixed_size : the fixed size (if any) that the dock is to maintain
    Returns:
        Boolean - True if the file was written successfully, False otherwise

    """

    root = ET.Element("root")
    pa_el = ET.Element("pinned_apps")

    for df in desktop_files:
        df_el = ET.Element("desktop_file", name=df)
        pa_el.append(df_el)

    ind_el = ET.Element("ind_type", light="%d" % light_ind)
    sa_el = ET.Element("show_all", show_all="%s" % show_all_apps)
    mi_el = ET.Element("multi_ind", show_multi="%s" % multi_ind)
    uwl_el = ET.Element("use_win_list",
                        uwl="%s" % use_dock_win_list)
    wcw_el = ET.Element("win_from_cur_ws_only",
                        wcw="%s" % win_from_cur_ws_only)
    pcc_el = ET.Element("panel_change_color", pcc="%s" % panel_change_color)
    dcc_el = ET.Element("dock_panel_change_only",
                        dcc="%s" % dock_panel_change_only)
    pal_el = ET.Element("panel_act_list",
                        pal="%s" % use_panel_act_list)
    abg_el = ET.Element("bg_type", type="%d" % active_icon_bg)

    fbc_el = ET.Element("fallback_bar_col")
    for col in fallback_bar_col:
        col_el = ET.Element("col", value="%s" % col)
        fbc_el.append(col_el)

    spc_el = ET.Element("spacing", spc="%d" % spacing)
    att_el = ET.Element("attention_type", type="%d" % attention_type)
    pdy_el = ET.Element("popup_delay", delay="%d" % popup_delay)

    sc_el = ET.Element("saved_configs")
    for config in saved_configs:
        cfg_el = ET.Element("config")
        cnm_el = ET.Element("config_name", name=config[0])
        cws_el = ET.Element("workspace_name", workspace=config[1])
        cpa_el = ET.Element("pinned_apps")
        for loop in range(2, len(config)):
            df = config[loop]
            df_el = ET.Element("desktop_file", name=df)
            cpa_el.append(df_el)

        cfg_el.append(cnm_el)
        cfg_el.append(cws_el)
        cfg_el.append(cpa_el)

        sc_el.append(cfg_el)

    paoaws_el = ET.Element("pinned_apps_all_workspaces", paoaws="%s" % pa_on_all_ws)

    dfs_el = ET.Element("dock_fixed_size", dfs="%d" %dock_fixed_size)

    root.append(pa_el)
    root.append(ind_el)
    root.append(sa_el)
    root.append(mi_el)
    root.append(uwl_el)
    root.append(wcw_el)
    root.append(pcc_el)
    root.append(dcc_el)
    root.append(pal_el)
    root.append(abg_el)
    root.append(fbc_el)
    root.append(spc_el)
    root.append(att_el)
    root.append(pdy_el)
    root.append(sc_el)
    root.append(paoaws_el)
    root.append(dfs_el)

    try:
        ET.ElementTree(root).write(filename, xml_declaration=True)
    except FileNotFoundError:
        return False  # invalid file or path name

    return True


def read_xml(filename):
    """ Reads an xml file created using the write_xml method

    Args:
        filename - the filename to read.

    Returns:
        boolean : True if the file was read successfully, False otherwise

        A tuple containing the following:
            a list of the .desktop files in the file (i.e. the pinned apps)
            an integer - the indicator setting
            a boolean - the show_all_apps setting
            a boolean - the multiple indicators setting
            a boolean - the use window list setting
            a boolean - the show indicators and win list items from the current
                        workspace only setting
            a boolean - the change panel colour setting
            a boolean - the change dock panel color only setting
            a boolean - the use panel action list setting
            an integer - the active icon background type
            a list of the r,g and b values (as strings) of the fallback bar indicator colour
            an integer - the spacing between apps
            an integer - the delay before window and acion lists popup
            a list of the workspace indexes that pinned apps are pinned to
            a tuple containing the details of pinned app configs - format is the same used when
            saving...
            a boolean - the pinned apps on all workspaces setting
            an int    - the fixed size (if any) of the dock

    """

    try:
        root = ET.parse(filename)
    except FileNotFoundError:
        return [False]

    df_list = []
    pinned_apps = root.find("pinned_apps")
    if pinned_apps is not None:
        for df in pinned_apps:
            df_list.append(df.get("name"))

    # note - values may be missing from the config file e.g. if a new version
    # of the applet adds a new configuration settings. If this happens, we just
    # assume a default option rather than reporting an error

    ind_el = root.find("ind_type")
    if ind_el is not None:
        light_ind = int(ind_el.get("light"))
    else:
        light_ind = 0

    ufa_el = root.find("show_all")
    if ufa_el is not None:
        show_all = ufa_el.get("show_all") == "True"
    else:
        show_all = True

    mi_el = root.find("multi_ind")
    if mi_el is not None:
        multi_ind = mi_el.get("show_multi") == "True"
    else:
        multi_ind = False

    uwl_el = root.find("use_win_list")
    if uwl_el is not None:
        use_win_list = uwl_el.get("uwl") == "True"
    else:
        use_win_list = True

    crla_el = root.find("win_from_cur_ws_only")
    if crla_el is not None:
        win_from_cur_ws_only = crla_el.get("wcw") == "True"
    else:
        win_from_cur_ws_only = True

    crla_el = root.find("panel_change_color")
    if crla_el is not None:
        panel_change_color = crla_el.get("pcc") == "True"
    else:
        panel_change_color = False

    crla_el = root.find("dock_panel_change_only")
    if crla_el is not None:
        dock_panel_change_only = crla_el.get("dcc") == "True"
    else:
        dock_panel_change_only = False

    pal_el = root.find("panel_act_list")
    if pal_el is not None:
        use_panel_act_list = pal_el.get("pal") == "True"
    else:
        use_panel_act_list = False

    abg_el = root.find("bg_type")
    if abg_el is not None:
        bg_type = int(abg_el.get("type"))
    else:
        bg_type = 0

    fallback_bar_col = []
    fbc_col = root.find("fallback_bar_col")
    if fbc_col is not None and (len(fbc_col) == 3):
        for col in fbc_col:
            fallback_bar_col.append(col.get("value"))
    else:
        fallback_bar_col = ["128", "128", "128"]

    spc_el = root.find("spacing")
    if spc_el is not None:
        spacing = int(spc_el.get("spc"))
    else:
        spacing = 0

    att_el = root.find("attention_type")
    if att_el is not None:
        attention_type = int(att_el.get("type"))
    else:
        attention_type = 0

    pdy_el = root.find("popup_delay")
    if pdy_el is not None:
        popup_delay = int(pdy_el.get("delay"))
    else:
        popup_delay = 1000

    saved_configs = []
    sc_el = root.find("saved_configs")
    if sc_el is not None:
        for config in sc_el:

            config_name = ""
            config_ws = ""
            cnm_el = config.find("config_name")
            if cnm_el is not None:
                config_name = cnm_el.get("name")
            cws_el = config.find("workspace_name")
            if cws_el is not None:
                config_ws = cws_el.get("workspace")

            conf = []
            conf.append(config_name)
            conf.append(config_ws)
            pinned_apps = config.find("pinned_apps")
            if pinned_apps is not None:
                for app in pinned_apps:
                    conf.append(app.get("name"))

            saved_configs.append(conf)

    paoaws_el = root.find("pinned_apps_all_workspaces")
    if paoaws_el is not None:
        pinned_apps_all_workspaces = paoaws_el.get("paoaws") == "True"
    else:
        pinned_apps_all_workspaces = True

    dfs_el = root.find("dock_fixed_size")
    if dfs_el is not None:
        dock_fixed_size = int(dfs_el.get("dfs"))
    else:
        dock_fixed_size = -1  # the dock has no fixed size

    return [True, df_list, light_ind, show_all, multi_ind,
            use_win_list, win_from_cur_ws_only,
            panel_change_color, dock_panel_change_only,
            use_panel_act_list, bg_type, fallback_bar_col,
            spacing, attention_type, popup_delay, saved_configs,
            pinned_apps_all_workspaces, dock_fixed_size]


def read_app_xml(filename):
    """ Reads the xml file containing the list of hard to match apps

    Args:
        filename - the filename to read.

    Returns:
        boolean : True if the file was read successfully, False otherwise

        A list of tuples containing the following:
            a string - the app name (as identified by wnck)
            a string - the window class of the app (as identified by wnck)
            a string - the .desktop file to be used for this app

        Note: the list will only contain enries relating to the distro the app
        is running on
    """

    distro, release, did = platform.linux_distribution()
    # Note: platform.linux_distribution is deprecated. Once it is removed,
    # the ld module can be used instead

    if (distro is None) or (distro == ""):
        return [False]

    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except FileNotFoundError:
        return [False]

    app_list = []
    for entry in root.findall("app"):
        add_it = False
        if (distro is not None) and (distro != ""):
            if distro == entry.find("distro").text:
                if (release is not None) and (release != ""):

                    target_rel = entry.find("release").text
                    if target_rel is None:
                        # if we specify a release but the distro doesn't have one, just assume a match
                        add_it = True
                    else:
                        add_it = release in target_rel

                else:
                    add_it = True

        if add_it:
            app_list.append([entry.find("name").text,
                            entry.find("class").text,
                            entry.find("desktop").text])
    return [True, app_list]


def main():
    """Main function.

    Debugging code can go here
    """

    print(os.path.dirname(sys.argv[0]))
    results = read_app_xml("src/app_match.xml")
    if results[0]:
        for app in results[1]:
            print("App name = %s" % app[0])
            print("App class = %s" % app[1])
            print("App desktop = %s" % app[2])
    else:
        print("could not read app_match.xml")

#    write_xml ("/home/robin/tmp/text.xml", ["thing.desktop","blah.desktop"], 99, False, True, False, False, True, False)
#    results = read_xml ("/home/robin/tmp/text.xml")
#    if results[0] == True:
#        for df in results[1]:
#            print ("Desktop file found: %s" %df)

#        print ("Use light ind = %d" %results[2])
#        print ("Show unpinned on all = %s" %results[3])
#        print ("Multi ind = %s" %results[4])
#        print ("Click restore all = %s" %results[5])
#        print ("pinned on all = %s" %results[6])
#        print ("panel change color = %s" %results[7])
#        print ("dock panel only = %s" %results[8])
#    else:
#        print ("Error reading file....")


if __name__ == "__main__":
    main()
