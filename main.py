#!.venv/bin/python3

# package <root>


import os as OS
import sys as System
import traceback as Traceback


import modules.command.CommandHandler as CommandHandler
import modules.command.CommandMap as CommandMap
import modules.command.Configuration as ConfigurationCommand
import modules.command.Exit as Exit
import modules.command.Settings as Settings
import modules.Conversation as Conversation
import modules.core.Print as Print
import modules.core.Util as Util
import modules.server.Server as Server
import modules.string.Strings as Strings


# disable selenium stats for cleaner output when using headless mode
OS.environ["SE_AVOID_STATS"] = "1"


# TODO:
# - make server-mode better over curl (text formatting)
# - complete server-mode

# TODO (tests):

# TODO (nice to have):


try:
    ConfigurationCommand.commandLoadModelConfiguration()
    ConfigurationCommand.commandLoadConfiguration()

    args = System.argv
    conversationName = Conversation.getConversationName()

    # normal entry
    if len(args) == 1:
        Print.clear()

        Conversation.setConversation(conversationName)

        import pynput as Pynput
        keyboardListener = Pynput.keyboard.Listener(on_press=Util.keyListener)
        keyboardListener.start()

        Print.separator()
        Print.generic(f"""Note: This script can interfere with the use of the [{Util.getKeybindStopName()}] key. Remap this in code if needed.""")  # in modules.core.Util
        Print.separator()

        Settings.command()

        def __main():
            Print.setIsServer(False)
            prompt = Util.printInput("Enter a prompt (\"/help\" for list of commands)")
            if not Util.checkEmptyString(prompt):
                if prompt == "exit" or prompt == "0" or prompt.startswith("/exit"):
                    keyboardListener.stop()
                    Exit.command()
                    return
                else:
                    CommandHandler.checkPromptForCommandsAndTriggers(prompt, False)
            else:
                CommandMap.commandHelp()
            __main()
        __main()

    # server entry
    else:
        shouldStartServer = False
        del args[0]
        for arg in args:
            if "--server" in arg:
                shouldStartServer = True
            else:
                Print.error("Unknown argument: " + arg)
                break
        if shouldStartServer:
            def __main():
                Conversation.setConversation(conversationName)
                Server.startServer()
                return
            __main()
except KeyboardInterrupt as ki:
    Print.generic("")
except Exception as e:
    Util.printError("An error has occurred: " + str(e))
    Util.printError(Traceback.format_exc())

