# package modules.command.toggle


import modules.core.Configuration as Configuration
import modules.core.Util as Util


def commandReprompt():
    Configuration.setConfig(
        "do_reprompts",
        Util.toggleSetting(
            Configuration.getConfig("do_reprompts"),
            "Reprompting is now disabled.",
            "Reprompting is now enabled."
        )
    )
    return
