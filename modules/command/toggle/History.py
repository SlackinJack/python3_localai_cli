# package modules.command.toggle


import modules.command.toggle.Toggle as Toggle
import modules.core.Configuration as Configuration


def toggle():
    current = not Configuration.getConfig("enable_chat_history_consideration")
    Configuration.setConfig("enable_chat_history_consideration", current)
    yield from Toggle.getMessage("Chat history is now ", current, " for responses.")
    return


def command():
    for _ in toggle():
        pass
    return
