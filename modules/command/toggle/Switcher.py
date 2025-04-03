# modules.command.toggle


import modules.Configuration as Configuration
import modules.Util as Util


def commandSwitcher():
    Configuration.setConfig(
        "enable_automatic_model_switching",
        Util.toggleSetting(
            Configuration.getConfig("enable_automatic_model_switching"),
            "Response model will not be switched.",
            "Response model will be automatically chosen."
        )
    )
    return
