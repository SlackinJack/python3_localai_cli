# modules.command.toggle


import modules.Configuration as Configuration
import modules.Util as Util


def commandHistory():
    Configuration.setConfig(
        "enable_chat_history_consideration",
        Util.toggleSetting(
            Configuration.getConfig("enable_chat_history_consideration"),
            "Chat history will not be used in prompts.",
            "Chat history will be used in prompts."
        )
    )
    return
