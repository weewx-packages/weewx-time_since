#
#    Copyright (c) 2023 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""Installer for the time_since search list extension

Version: 1.0.1                                            Date: 23 October 2026

Revision History
    23 October 2026     v1.0.1
        -   added this installer, so the extension can be installed with
            weectl extension install

The installer only copies bin/user/time_since.py. A search list extension is
enabled per skin, so a skin has to name it in its CheetahGenerator section:

    search_list_extensions = user.time_since.TimeSince

Doing that automatically would replace any search list extensions the skin
already lists.
"""

from weecfg.extension import ExtensionInstaller

VERSION = "1.0.1"


def loader():
    """Return the installer expected by weectl.

    Returns:
        TimeSinceInstaller: The files of the extension.
    """
    return TimeSinceInstaller()


class TimeSinceInstaller(ExtensionInstaller):
    """Copy the search list extension into the user directory."""

    def __init__(self):
        super().__init__(
            version=VERSION,
            name='time_since',
            description='Search list extension to calculate when an SQL statement last '
                        'evaluated true, or how long since it did.',
            author="Tom Keffer",
            author_email="tkeffer@gmail.com",
            files=[('bin/user', ['bin/user/time_since.py'])]
        )
