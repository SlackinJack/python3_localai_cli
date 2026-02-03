# package modules.command

import modules.command.CommandMap as CommandMap
import modules.core.Print as Print
import modules.core.Util as Util


def command():
    Print.generic("Available commands:")
    currentCategory = ""
    for c in CommandMap.getCommandMap().values():
        commandName = Util.padStringToLength(c[0], 12)
        commandCategory = c[1]
        commandDescription = c[2]
        if len(currentCategory) == 0:
            currentCategory = commandCategory
            Print.generic("---------------------- " + currentCategory + " ----------------------")
        else:
            if not currentCategory == commandCategory:
                currentCategory = commandCategory
                Print.generic("---------------------- " + currentCategory + " ----------------------")
        Print.generic(" - " + commandName + "> " + commandDescription)
    Print.generic("")
    return
