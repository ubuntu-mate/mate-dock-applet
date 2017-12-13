#!/bin/bash
xgettext --files-from=POTFILES.in --directory=../ --output=mate-dock-applet.pot --language=Python

while read lingua
do
  msgmerge --update --no-fuzzy-matching --backup=off ${lingua}.po mate-dock-applet.pot
  msgfmt ${lingua}.po --output-file ${lingua}.mo
done < LINGUAS

