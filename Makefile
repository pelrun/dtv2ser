#
# Makefile - main dtv2ser Makefile
#
# Written by
#  Christian Vogelgsang <chris@vogelgsang.org>
#
# This file is part of dtv2ser.
# See README for copyright notice.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
#  02111-1307  USA.
#

VERSION := 0.5
SUBDIRS := client server servlet
PROJECT := dtv2ser

REVSION := $(shell svn info | awk '/Revision:/ { print $$2 }')
DATE := $(shell date '+%Y%m%d')
DIST_NAME := $(PROJECT)-$(VERSION)
SNAP_NAME := $(PROJECT)-pre$(VERSION)-r$(REVSION)-$(DATE)

clean:
	for a in $(SUBDIRS) ; do $(MAKE) -C $$a clean ; done

dist:
	rm -rf $(DIST_NAME) $(DIST_NAME).zip
	svn export . $(DIST_NAME)
	for a in $(SUBDIRS) ; do $(MAKE) -C $(DIST_NAME)/$$a dist ; done
	zip -r $(DIST_NAME).zip $(DIST_NAME)
	rm -rf $(DIST_NAME)

snap:
	rm -rf $(SNAP_NAME) $(SNAP_NAME).zip
	svn export . $(SNAP_NAME)
	rm -rf $(SNAP_NAME)/hardware
	for a in $(SUBDIRS) ; do $(MAKE) -C $(SNAP_NAME)/$$a dist ; done
	zip -r $(SNAP_NAME).zip $(SNAP_NAME)
	rm -rf $(SNAP_NAME)

