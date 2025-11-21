# package modules.command


import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.core.Util as Util


def command():
    Print.generic("\nCurrent system prompt:")
    Util.printCurrentSystemPrompt(Print.generic, "\n")
    Configuration.setConfig("system_prompt", Util.printInput("Enter the new system prompt"))
    Print.green("\nSet system prompt to:")
    Util.printCurrentSystemPrompt(Print.green, "\n")
    return
