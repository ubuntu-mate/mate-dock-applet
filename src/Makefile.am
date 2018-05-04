
SUBDIRS =

applet_SCRIPTS = dock_applet.py dock.py docked_app.py dock_prefs.py dock_about.py log_it.py dock_custom_launcher.py dock_win_list.py \
		 dock_action_list.py dock_xml.py dock_color_changer.py dom_color.py dock_info.py dock_popup.py docked_app_helpers.py window_control.py

appletdir = $(libdir)/mate-applets/mate-dock-applet/

APPLET_LOCATION = $(appletdir)dock_applet.py

appletsdir       = $(datadir)/mate-panel/applets
applets_in_files = org.mate.panel.DockApplet.mate-panel-applet
applets_DATA     = $(applets_in_files:.mate-panel-applet.in=.mate-panel-applet)

config.py: config.py.in
	$(AM_V_GEN)sed					\
		-e s!\@prefix\@!$(prefix)!		\
		-e s!\@datadir\@!$(datadir)!		\
		-e s!\@pkgdatadir\@!$(pkgdatadir)!	\
		-e s!\@libexecdir\@!$(libexecdir)!	\
		-e s!\@libdir\@!$(libdir)!		\
		-e s!\@PACKAGE\@!$(PACKAGE)!		\
		-e s!\@VERSION\@!$(VERSION)!		\
		-e s!\@GETTEXT_PACKAGE\@!$(GETTEXT_PACKAGE)!	\
		< $< > $@
config.py: Makefile

#@echo "This is a test"
#if WITH_GTK2_SET
#	$(info **************  Legacy Mode - Building for Gtk2  **************)
#else
#	$(info **************  Building for Gtk3 **************)
#endif

if WITH_GTK3_SET
do_substitution = $(AM_V_GEN)sed \
		-e 's,[@]pythondir[@],$(pythondir),g' \
		-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	  	-e 's,[@]VERSION[@],$(VERSION),g' \
	    -e 's,[@]LOCATION[@],$(appletdir),g' \
	    -e 's,[@]localedir[@],$(datadir)/locale,g'
else
do_substitution = $(AM_V_GEN)sed \
		-e 's,[@]pythondir[@],$(pythondir),g' \
		-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	  	-e 's,[@]VERSION[@],$(VERSION),g' \
	    -e 's,[@]LOCATION[@],$(appletdir),g' \
	    -e 's,[@]localedir[@],$(datadir)/locale,g' \
	    -e 's,build_gtk2 = False,build_gtk2 = True,g'
endif

#$(applets_in_files): $(applets_in_files).in Makefile
#	$(AM_V_GEN)sed \
#		-e "s|\@LOCATION\@|$(appletdir)|" \
#		-e "s|\@pythondir\@|$(pythondir)|" \
#	  	-e "s|\@PACKAGE\@|$(PACKAGE)|" \
#	  	-e "s|\@VERSION\@|$(VERSION)|" \
#		$< > $@

#%.mate-panel-applet.in: %.mate-panel-applet.in.in Makefile
#	$(AM_V_GEN)sed \
#		-e "s|\@LOCATION\@|$(appletdir)|" \
#		-e "s|\@pythondir\@|$(pythondir)|" \
#	  	-e "s|\@PACKAGE\@|$(PACKAGE)|" \
#	  	-e "s|\@VERSION\@|$(VERSION)|" \
#		-e "s|\@localdir\@|$(datadir)//locale|" \
#		$< > $@

#@PANEL_INTLTOOL_MATE_PANEL_APPLET_RULE@

servicedir       = $(datadir)/dbus-1/services
service_in_files = org.mate.panel.applet.DockAppletFactory.service.in
service_DATA     = $(service_in_files:.service.in=.service)

xmldir		 =$(appletdir)
xml_DATA 	 = app_match.xml

#imagedir	 = $(libexecdir)
#image_DATA	 = sahsl.png \
#		   sahsd.png \
#		   boinc.png

#%.gschema.xml.in: %.gschema.xml.in.in Makefile
#	$(AM_V_GEN)sed -e 's^\@GETTEXT_PACKAGE\@^$(GETTEXT_PACKAGE)^g' < $< > $@
#
gsettings_SCHEMAS = org.mate.panel.applet.dock.gschema.xml

#
#@INTLTOOL_XML_NOMERGE_RULE@
#@GSETTINGS_RULES@

#$(gsettings_SCHEMAS).in: $(gsettings_SCHEMAS).in.in Makefile
#	$(AM_V_GEN)sed -e 's^\@GETTEXT_PACKAGE\@^$(GETTEXT_PACKAGE)^g' \
# 		       -e "s|\@LOCATION\@|$(libexecdir)|" \
#		       < $< > $@

org.mate.panel.applet.DockAppletFactory.service: $(service_in_files)
	$(AM_V_GEN)sed \
		-e "s|\@LOCATION\@|$(APPLET_LOCATION)|" \
		$< > $@


org.mate.panel.DockApplet.mate-panel-applet: $(applet_in_files)
	$(do_substitution) < $(srcdir)/org.mate.panel.DockApplet.mate-panel-applet.in > org.mate.panel.DockApplet.mate-panel-applet

dock_applet.py: dock_applet.in Makefile
	$(do_substitution) < $(srcdir)/dock_applet.in > dock_applet.py
	chmod +x dock_applet.py

dock_about.py: dock_about.in Makefile
	$(do_substitution) < $(srcdir)/dock_about.in > dock_about.py
	chmod +x dock_about.py

dock_prefs.py: dock_prefs.in Makefile
	$(do_substitution) < $(srcdir)/dock_prefs.in > dock_prefs.py
	chmod +x dock_prefs.py

dock_custom_launcher.py: dock_custom_launcher.in Makefile
	$(do_substitution) < $(srcdir)/dock_custom_launcher.in > dock_custom_launcher.py
	chmod +x dock_custom_launcher.py

dock.py: dock.in Makefile
	$(do_substitution) < $(srcdir)/dock.in > dock.py
	chmod +x dock.py

docked_app.py: docked_app.in Makefile
	$(do_substitution) < $(srcdir)/docked_app.in > docked_app.py
	chmod +x docked_app.py

log_it.py: log_it.in Makefile
	$(do_substitution) < $(srcdir)/log_it.in > log_it.py
	chmod +x log_it.py

dock_win_list.py: dock_win_list.in Makefile
	$(do_substitution) < $(srcdir)/dock_win_list.in > dock_win_list.py
	chmod +x dock_win_list.py

dock_action_list.py: dock_action_list.in Makefile
	$(do_substitution) < $(srcdir)/dock_action_list.in > dock_action_list.py
	chmod +x dock_action_list.py

dock_xml.py: dock_xml.in Makefile
	$(do_substitution) < $(srcdir)/dock_xml.in > dock_xml.py
	chmod +x dock_xml.py

dock_color_changer.py: dock_color_changer.in Makefile
	$(do_substitution) < $(srcdir)/dock_color_changer.in > dock_color_changer.py
	chmod +x dock_color_changer.py

dom_color.py: dom_color.in Makefile
	$(do_substitution) < $(srcdir)/dom_color.in > dom_color.py
	chmod +x dom_color.py

dock_info.py: dock_info.in Makefile
	$(do_substitution) < $(srcdir)/dock_info.in > dock_info.py
	chmod +x dock_info.py

dock_popup.py: dock_popup.in Makefile
		$(do_substitution) < $(srcdir)/dock_popup.in > dock_popup.py
		chmod +x dock_popup.py

docked_app_helpers.py: docked_app_helpers.in Makefile
		$(do_substitution) < $(srcdir)/docked_app_helpers.in > docked_app_helpers.py
		chmod +x docked_app_helpers.py

window_control.py: window_control.in Makefile
		$(do_substitution) < $(srcdir)/window_control.in > window_control.py
		chmod +x window_control.py

applet_PYTHON = \
		     dock_applet.py \
		     dock_about.py \
		     dock_prefs.py \
		     dock.py \
		     docked_app.py \
		     dock_custom_launcher.py \
		     log_it.py \
		     dock_win_list.py \
			 dock_action_list.py \
		     dock_xml.py \
		     dock_color_changer.py \
		     dom_color.py \
		     dock_popup.py \
		     dock_info.in \
		     docked_app_helpers.in \
		     window_control.in

CLEANFILES = $(applet_SCRIPTS) \
	     org.mate.panel.applet.DockAppletFactory.service \
	     org.mate.panel.DockApplet.mate-panel-applet \
	     config.py

EXTRA_DIST = dock_applet.in \
	     dock_about.in \
	     dock_prefs.in \
	     dock.in \
	     docked_app.in \
	     dock_custom_launcher.in \
	     log_it.in \
	     dock_win_list.in \
	     dock_action_list.in \
	     dock_xml.in \
	     dock_color_changer.in \
	     dom_color.in \
	     dock_info.in \
	     dock_popup.in \
	     docked_app_helpers.in \
	     window_control.in \
	     $(gsettings_SCHEMAS) \
	     $(applets_in_files) \
	     $(service_in_files) \
	     $(xml_DATA) \
	     config.py.in

all-local: config.py
