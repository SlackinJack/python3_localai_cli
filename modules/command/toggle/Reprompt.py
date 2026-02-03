# package modules.command.toggle


import modules.command.toggle.Toggle as Toggle
import modules.core.Configuration as Configuration


def toggle():
    current = not Configuration.getConfig("do_reprompts")
    Configuration.setConfig("do_reprompts", current)
    yield from Toggle.getMessage("Reprompting is now ", current, " for responses.")
    return


def command():
    for _ in toggle():
        pass
    return
