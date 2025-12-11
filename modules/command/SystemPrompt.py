# package modules.command


import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.core.Util as Util


def command():
    Print.generic("Current system prompt:")
    Util.printCurrentSystemPrompt(Print.generic, "")
    Configuration.setConfig("system_prompt", Util.printInput("Enter the new system prompt"))
    Print.green("Set system prompt to:")
    Util.printCurrentSystemPrompt(Print.green, "")
    return
