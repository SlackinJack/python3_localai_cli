# package modules.command.toggle


import modules.core.Configuration as Configuration
import modules.core.Util as Util
import modules.strings.Strings as Strings


def __stringBuilder(statusIn):
    return Strings.getCommandToggleString(Strings.RESPONSE_MODEL, statusIn, Strings.RESPONSES)


def command():
    Configuration.setConfig(
        "enable_automatic_model_switching",
        Util.toggleSetting(
            Configuration.getConfig("enable_automatic_model_switching"),
            __stringBuilder(Strings.WILL_NOT_BE_SWITCHED_STRING),
            __stringBuilder(Strings.WILL_BE_AUTOMATICALLY_CHOSEN_STRING),
        )
    )
    return
