# package modules.command.toggle


import modules.core.Configuration as Configuration
import modules.core.Util as Util
import modules.strings.Strings as Strings


def __stringBuilder(statusIn):
    return Strings.getCommandToggleString(Strings.FUNCTIONS_STRING, statusIn, Strings.RESPONSES)


def command():
    Configuration.setConfig(
        "enable_functions",
        Util.toggleSetting(
            Configuration.getConfig("enable_functions"),
            __stringBuilder(Strings.DISABLED),
            __stringBuilder(Strings.ENABLED),
        )
    )
    return
