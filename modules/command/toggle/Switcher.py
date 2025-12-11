# package modules.command.toggle


import modules.core.Configuration as Configuration
import modules.core.Util as Util
import modules.string.Strings as Strings


def __stringBuilder(statusIn):
    return Strings.getCommandToggleString("Response model", statusIn, "responses")


def command():
    Configuration.setConfig(
        "enable_automatic_model_switching",
        Util.toggleSetting(
            Configuration.getConfig("enable_automatic_model_switching"),
            __stringBuilder("will not be switched"),
            __stringBuilder("will be automatically chosen"),
        )
    )
    return
