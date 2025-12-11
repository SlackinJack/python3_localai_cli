# package modules.command.toggle


import modules.core.Configuration as Configuration
import modules.core.Util as Util
import modules.string.Strings as Strings


def __stringBuilder(statusIn):
    return Strings.getCommandToggleString("Chat history", statusIn, "responses")


def command():
    Configuration.setConfig(
        "enable_chat_history_consideration",
        Util.toggleSetting(
            Configuration.getConfig("enable_chat_history_consideration"),
            __stringBuilder(Strings.DISABLED),
            __stringBuilder(Strings.ENABLED),
        )
    )
    return
