# package modules.command


import modules.command.Audio as Audio
import modules.command.Clear as Clear
import modules.command.Configuration as Configuration
import modules.command.Conversation as Conversation
import modules.command.Curl as Curl
import modules.command.Exit as Exit
import modules.command.Image as Image
import modules.command.Messages as Messages
import modules.command.Model as Model
import modules.command.Settings as Settings
import modules.command.SystemPrompt as SystemPrompt
import modules.command.Test as Test
import modules.command.toggle.Function as Function
import modules.command.toggle.History as History
import modules.command.toggle.Internet as Internet
import modules.command.toggle.Reprompt as Reprompt
import modules.command.toggle.Switcher as Switcher
import modules.core.Print as Print
import modules.core.Util as Util


def getCommandMap():
    return {
        commandHelp:            ["/help",           "General",      "Show available commands."],
        Clear.command:          ["/clear",          "General",      "Clear the prompt window."],
        Messages.command:       ["/messages",       "General",      "Shows the current conversation message log."],
        Configuration.command:  ["/config",         "General",      "Load or reload configuration files."],
        Settings.command:       ["/settings",       "General",      "Print current settings."],
        Exit.command:           ["/exit",           "General",      "Exit the program."],

        Conversation.command:   ["/convo",          "Settings",     "Change the conversation file."],
        Model.command:          ["/model",          "Settings",     "Manage models."],
        SystemPrompt.command:   ["/system",         "Settings",     "Change the system prompt."],

        Function.command:       ["/functions",      "Toggles",      "Toggle on/off functions."],
        History.command:        ["/history",        "Toggles",      "Toggle on/off chat history consideration."],
        Internet.command:       ["/internet",       "Toggles",      "Toggle on/off internet for actions."],
        Reprompt.command:       ["/reprompt",       "Toggles",      "Toggle on/off reprompting for chat."],
        Switcher.command:       ["/switcher",       "Toggles",      "Toggle on/off automatic model switcher."],

        Audio.command:          ["/audio",          "Tools",        "Audio menu."],
        Curl.command:           ["/curl",           "Tools",        "Send cURL commands to the server."],
        Image.command:          ["/image",          "Tools",        "Image menu."],
        Test.command:           ["/test",           "Tools",        "Test all program functionalities."],
    }


def commandHelp():
    Print.generic("Available commands:")
    currentCategory = ""
    for c in getCommandMap().values():
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
