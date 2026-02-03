# package modules.command.toggle


import modules.command.toggle.Toggle as Toggle
import modules.core.Configuration as Configuration


def toggle():
    current = not Configuration.getConfig("enable_automatic_model_switching")
    Configuration.setConfig("enable_automatic_model_switching", current)
    yield from Toggle.getMessage("Response model switching is now ", current, " for responses.")
    return


def command():
    for _ in toggle():
        pass
    return
