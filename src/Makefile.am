
SUBDIRS =

appletdir = $(libdir)/mate-applets/mate-dock-applet/
applet_SCRIPTS = dock_applet.py dock.py docked_app.py dock_prefs.py dock_about.py log_it.py dock_custom_launcher.py dock_win_list.py \
		 dock_action_list.py dock_xml.py dock_color_changer.py dom_color.py dock_info.py dock_popup.py docked_app_helpers.py window_control.py

APPLET_LOCATION = $(appletdir)dock_applet.py

appletsdir       = $(datadir)/mate-panel/applets
applets_in_files = org.mate.panel.DockApplet.mate-panel-applet.in
applets_DATA     = $(applets_in_files:.mate-panel-applet.in=.mate-panel-applet)

config.py: config.py.in
	$(AM_V_GEN)sed					\
		-e s!\@prefix\@!$(prefix)!		\
		-e s!\@datadir\@!$(datadir)!		\
		-e s!\@pkgdatadir\@!$(pkgdatadir)!	\
		-e s!\@libexecdir\@!$(libexecdir)!	\
		-e s!\@pythondir\@!$(pythondir)!	\
		-e s!\@libdir\@!$(libdir)!		\
		-e s!\@PACKAGE\@!$(PACKAGE)!		\
		-e s!\@VERSION\@!$(VERSION)!		\
		-e s!\@GETTEXT_PACKAGE\@!$(GETTEXT_PACKAGE)!	\
		-e s!\@WITH_GTK3\@!$(WITH_GTK3)!		\
		< $< > $@

servicedir       = $(datadir)/dbus-1/services
service_in_files = org.mate.panel.applet.DockAppletFactory.service.in
service_DATA     = $(service_in_files:.service.in=.service)

xmldir		 =$(appletdir)
xml_DATA 	 = app_match.xml

gsettings_SCHEMAS = org.mate.panel.applet.dock.gschema.xml

org.mate.panel.applet.DockAppletFactory.service: $(service_in_files)
	$(AM_V_GEN)sed \
		-e "s|\@LOCATION\@|$(appletdir)dock_applet.py|" $< > $@

org.mate.panel.DockApplet.mate-panel-applet: $(applets_in_files)
	$(AM_V_GEN)sed \
		-e "s|\@LOCATION\@|$(appletdir)|" $< > $@

CLEANFILES = $(applet_SCRIPTS) \
	     org.mate.panel.applet.DockAppletFactory.service \
	     org.mate.panel.DockApplet.mate-panel-applet \
	     config.py

EXTRA_DIST = $(gsettings_SCHEMAS) \
	     $(applets_in_files) \
	     $(service_in_files) \
	     $(xml_DATA) \
	     config.py.in

all-local: config.py
