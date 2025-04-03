# modules.command.toggle


import modules.Configuration as Configuration
import modules.Util as Util


def commandInternet():
    Configuration.setConfig(
        "enable_internet",
        Util.toggleSetting(
            Configuration.getConfig("enable_internet"),
            "Internet is now disabled for files and functions.",
            "Internet is now enabled for files and functions."
        )
    )
    return
