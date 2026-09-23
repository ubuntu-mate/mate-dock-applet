AC_INIT([mate-dock-applet], [20.04.0],
        [https://github.com/ubuntu-mate/mate-dock-applet/issues], [mate-dock-applet])

AM_INIT_AUTOMAKE([foreign -Wall])
AM_PATH_PYTHON([3.3])

GETTEXT_PACKAGE=mate-dock-applet
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE], ["$GETTEXT_PACKAGE"], [Gettext package])

GLIB_GSETTINGS

AM_GNU_GETTEXT_VERSION([0.19])
AM_GNU_GETTEXT([external])

AC_CONFIG_FILES([Makefile src/Makefile po/Makefile.in])
AC_OUTPUT
