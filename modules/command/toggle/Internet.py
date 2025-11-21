# package modules.command.toggle


import modules.core.Configuration as Configuration
import modules.core.Util as Util
import modules.strings.Strings as Strings


def __stringBuilder(statusIn):
    return Strings.getCommandToggleString(Strings.INTERNET_USAGE_STRING, statusIn, Strings.FILES_AND_FUNCTIONS_STRING)


def command():
    Configuration.setConfig(
        "enable_internet",
        Util.toggleSetting(
            Configuration.getConfig("enable_internet"),
            __stringBuilder(Strings.DISABLED),
            __stringBuilder(Strings.ENABLED),
        )
    )
    return
