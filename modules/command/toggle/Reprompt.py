# package modules.command.toggle


import modules.core.Configuration as Configuration
import modules.core.Util as Util
import modules.string.Strings as Strings


def __stringBuilder(statusIn):
    return Strings.getCommandToggleString("Reprompting", statusIn, "responses")


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
