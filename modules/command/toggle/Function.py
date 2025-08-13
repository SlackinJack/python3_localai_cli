# package modules.command.toggle


import modules.core.Configuration as Configuration
import modules.core.Util as Util


def commandFunctions():
    Configuration.setConfig(
        "enable_functions",
        Util.toggleSetting(
            Configuration.getConfig("enable_functions"),
            "Functions is now disabled for prompts.",
            "Functions is now enabled for prompts."
        )
    )
    return
