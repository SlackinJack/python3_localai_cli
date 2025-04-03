# modules.command


import modules.Configuration as Configuration
import modules.Print as Print
import modules.Util as Util


def commandSystemPrompt():
    Print.generic("\nCurrent system prompt:")
    Util.printCurrentSystemPrompt(Print.generic, "\n")
    Configuration.setConfig("system_prompt", Util.printInput("Enter the new system prompt"))
    Print.green("\nSet system prompt to:")
    Util.printCurrentSystemPrompt(Print.green, "\n")
    return
