# package modules.command.toggle


import modules.core.Configuration as Configuration
import modules.core.Util as Util
import modules.strings.Strings as Strings


def __stringBuilder(statusIn):
    return Strings.getCommandToggleString(Strings.REPROMPTING, statusIn, Strings.RESPONSES)


def command():
    Configuration.setConfig(
        "do_reprompts",
        Util.toggleSetting(
            Configuration.getConfig("do_reprompts"),
            __stringBuilder(Strings.DISABLED),
            __stringBuilder(Strings.ENABLED),
        )
    )
    return
