
SUBDIRS =

applet_SCRIPTS = dock_applet.py dock.py docked_app.py dock_prefs.py dock_about.py log_it.py

appletdir = $(libdir)/mate-applets/mate-dock-applet/

APPLET_LOCATION = $(appletdir)/dock_applet.py

appletsdir       = $(datadir)/mate-panel/applets
applets_in_files = org.mate.panel.DockApplet.mate-panel-applet 
applets_DATA     = $(applets_in_files:.mate-panel-applet.in=.mate-panel-applet)

do_substitution = $(AM_V_GEN)sed \
		  -e 's,[@]pythondir[@],$(pythondir),g' \
		  -e 's,[@]PACKAGE[@],$(PACKAGE),g' \
		  -e 's,[@]VERSION[@],$(VERSION),g' \
		  -e 's,[@]LOCATION[@],$(appletdir),g' \
		  -e 's,[@]localedir[@],$(datadir)/locale,g' 

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
#	$(AM_V_GEN)sed \
#		-e "s|\@LOCATION\@|$(appletdir)|" \
#		-e "s|\@pythondir\@|$(pythondir)|" \
#	  	-e "s|\@PACKAGE\@|$(PACKAGE)|" \
#	  	-e "s|\@VERSION\@|$(VERSION)|" \
#		-e "s|\@localdir\@|$(datadir)//locale|" \
#		$< > $@


dock_applet.py: dock_applet.in Makefile
	$(do_substitution) < $(srcdir)/dock_applet.in > dock_applet.py
	chmod +x dock_applet.py

dock_about.py: dock_about.in Makefile
	$(do_substitution) < $(srcdir)/dock_about.in > dock_about.py
	chmod +x dock_about.py

dock_prefs.py: dock_prefs.in Makefile
	$(do_substitution) < $(srcdir)/dock_prefs.in > dock_prefs.py
	chmod +x dock_prefs.py

dock.py: dock.in Makefile
	$(do_substitution) < $(srcdir)/dock.in > dock.py
	chmod +x dock.py

docked_app.py: docked_app.in Makefile
	$(do_substitution) < $(srcdir)/docked_app.in > docked_app.py
	chmod +x docked_app.py

log_it.py: log_it.in Makefile
	$(do_substitution) < $(srcdir)/log_it.in > log_it.py
	chmod +x log_it.py
applet_PYTHON = \
		     dock_applet.py \
		     dock_about.py \
		     dock_prefs.py \
		     dock.py \
		     docked_app.py \
		     log_it.py

#install-data-hook:
# TODO: find a better way of coping with this
#  move the .mate-panel-applet file to /usr/share/mate-panel/applets since it doesn't seem to work
# in /usr/local/share/mate-panel/applets
#	mv $(appletsdir)/org.mate.panel.DockApplet.mate-panel-applet /usr/share/mate-panel/applets/

CLEANFILES = $(applet_SCRIPTS) 
#	     $(gsettings_SCHEMAS) \
#	     org.mate.panel.applet.DockAppletFactory.service 

#	     $(gsettings_SCHEMAS).in 
	
EXTRA_DIST = dock_applet.in \
	     dock_about.in \
	     dock_prefs.in \
	     dock.in \
	     docked_app.in \
	     log_it.in \
	     $(gsettings_SCHEMAS) \
	     $(applets_in_files) \
	     $(service_in_files)

