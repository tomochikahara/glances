# -*- coding: utf-8 -*-
#
# This file is part of Glances.
#
# Copyright (C) 2015 Nicolargo <nicolas@nicolargo.com>
#
# Glances is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Glances is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Manage the Glances standalone session."""

# Import Glances libs
from glances.core.glances_globals import is_windows
from glances.core.glances_logging import logger
from glances.core.glances_processes import glances_processes
from glances.core.glances_stats import GlancesStats
from glances.outputs.glances_curses import GlancesCursesStandalone


class GlancesStandalone(object):

    """This class creates and manages the Glances standalone session."""

    def __init__(self, config=None, args=None):
        # Init stats
        self.stats = GlancesStats(config=config, args=args)

        # Default number of processes to displayed is set to 50
        glances_processes.max_processes = 50

        # If process extended stats is disabled by user
        if not args.enable_process_extended:
            logger.debug("Extended stats for top process are disabled")
            glances_processes.disable_extended()
        else:
            logger.debug("Extended stats for top process are enabled")
            glances_processes.enable_extended()

        # Manage optionnal process filter
        if args.process_filter is not None:
            glances_processes.process_filter = args.process_filter

        if (not is_windows) and args.no_kernel_threads:
            # Ignore kernel threads in process list
            glances_processes.disable_kernel_threads()

        if args.process_tree:
            # Enable process tree view
            glances_processes.enable_tree()

        # Initial system informations update
        self.stats.update()

        if args.silent:
            self.silent_mode = True
        else:
            self.silent_mode = False
            # Init screen
            self.screen = GlancesCursesStandalone(args=args)

    def serve_forever(self):
        """Main loop for the CLI."""
        while True:
            # Update system informations
            self.stats.update()

            if not self.silent_mode:
                # Update the screen
                self.screen.update(self.stats)

            # Export stats using export modules
            self.stats.export(self.stats)

    def end(self):
        """End of the standalone CLI."""
        if not self.silent_mode:
            self.screen.end()

        # Exit from export modules
        self.stats.end()
