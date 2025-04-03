# <root>


import pynput as Pynput


import modules.command.Exit as Exit
import modules.command.CommandHandler as CommandHandler
import modules.command.CommandMap as CommandMap
import modules.command.Configuration as Configuration
import modules.command.Settings as Settings
import modules.Conversation as Conversation
import modules.Print as Print
import modules.Util as Util


# TODO:
# - fix / test write file operation in functions
# - use tokens/sec instead of chars/sec for text-to-text stats (wait for localai support)
# - append seed to image file names


# TODO (tests):


# TODO (nice to have):
# - STT input button


###########################
""" BEGIN INITALIZATION """
###########################


Print.clear()

Configuration.commandLoadModelConfiguration()
Configuration.commandLoadConfiguration()

Conversation.setConversation(Conversation.getConversationName())

keyboardListener = Pynput.keyboard.Listener(on_press=Util.keyListener)
keyboardListener.start()

Print.separator()
Print.generic("Note: This script can interfere with the use of the [" + Util.getKeybindStopName() + "] key.")
Print.generic("Remap this in code if needed.")  # in modules.Util
Print.separator()

Settings.commandSettings()


##################
""" BEGIN MAIN """
##################


def main():
    prompt = Util.printInput("Enter a prompt (\"/help\" for list of commands)")
    if not Util.checkEmptyString(prompt):
        if prompt == "exit" or prompt == "0" or prompt.startswith("/exit"):
            keyboardListener.stop()
            Exit.commandExit()
            return
        else:
            CommandHandler.checkPromptForCommandsAndTriggers(prompt)
    else:
        CommandMap.commandHelp()
    main()


main()
