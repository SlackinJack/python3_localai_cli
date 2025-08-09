# modules.command


import modules.command.Audio as Audio
import modules.command.Clear as Clear
import modules.command.Configuration as Configuration
import modules.command.Conversation as Conversation
import modules.command.Curl as Curl
import modules.command.Exit as Exit
import modules.command.Image as Image
import modules.command.Model as Model
import modules.command.Settings as Settings
import modules.command.SystemPrompt as SystemPrompt
import modules.command.Test as Test
import modules.command.toggle.Function as Function
import modules.command.toggle.History as History
import modules.command.toggle.Internet as Internet
import modules.command.toggle.Reprompt as Reprompt
import modules.command.toggle.Switcher as Switcher
import modules.Print as Print
import modules.Util as Util


def getCommandMap():
    return {
        commandHelp:                            ["/help",           "General",      "Show available commands."],
        Clear.commandClear:                     ["/clear",          "General",      "Clear the prompt window."],
        Configuration.commandConfiguration:     ["/config",         "General",      "Load or reload configuration files."],
        Settings.commandSettings:               ["/settings",       "General",      "Print current settings."],
        Exit.commandExit:                       ["/exit",           "General",      "Exit the program."],

        Conversation.commandConversation:       ["/convo",          "Settings",     "Change the conversation file."],
        Model.commandModel:                     ["/model",          "Settings",     "Manage models."],
        SystemPrompt.commandSystemPrompt:       ["/system",         "Settings",     "Change the system prompt."],

        Function.commandFunctions:              ["/functions",      "Toggles",      "Toggle on/off functions."],
        History.commandHistory:                 ["/history",        "Toggles",      "Toggle on/off chat history consideration."],
        Internet.commandInternet:               ["/internet",       "Toggles",      "Toggle on/off internet for actions."],
        Reprompt.commandReprompt:               ["/reprompt",       "Toggles",      "Toggle on/off reprompting for chat."],
        Switcher.commandSwitcher:               ["/switcher",       "Toggles",      "Toggle on/off automatic model switcher."],

        Audio.commandAudio:                     ["/audio",          "Tools",        "Audio menu."],
        Curl.commandCurl:                       ["/curl",           "Tools",        "Send cURL commands to the server."],
        Image.commandImage:                     ["/image",          "Tools",        "Image menu."],
        Test.commandTest:                       ["/test",           "Tools",        "Test all program functionalities."],
    }


def commandHelp():
    Print.generic("\nAvailable commands:")
    currentCategory = ""
    for c in getCommandMap().values():
        commandName = Util.padStringToLength(c[0], 12)
        commandCategory = c[1]
        commandDescription = c[2]
        if len(currentCategory) == 0:
            currentCategory = commandCategory
            Print.generic("\n---------------------- " + currentCategory + " ----------------------\n")
        else:
            if not currentCategory == commandCategory:
                currentCategory = commandCategory
                Print.generic("\n---------------------- " + currentCategory + " ----------------------\n")
        Print.generic(" - " + commandName + "> " + commandDescription)
    Print.generic("")
    return
