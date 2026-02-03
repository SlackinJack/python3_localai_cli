# package modules.command.toggle


import modules.command.toggle.Toggle as Toggle
import modules.core.Configuration as Configuration


def toggle():
    current = not Configuration.getConfig("enable_internet")
    Configuration.setConfig("enable_internet", current)
    yield from Toggle.getMessage("Internet usage is now ", current, " for responses.")
    return


def command():
    for _ in toggle():
        pass
    return
