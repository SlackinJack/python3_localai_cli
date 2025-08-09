#!.venv/bin/python3

# <root>


import pynput as Pynput
import sys as System
import traceback as Traceback


import modules.command.CommandHandler as CommandHandler
import modules.command.CommandMap as CommandMap
import modules.command.Configuration as Configuration
import modules.command.Exit as Exit
import modules.command.Settings as Settings
import modules.Conversation as Conversation
import modules.Print as Print
import modules.Util as Util


# TODO:
# - main:
# -     expand headless mode
# - audio:
# -     dont write anything to disk
# - text:
# -     conversation deepseek bos fix

# TODO (tests):
# - audio-to-text
# |     live transcription file output

# TODO (nice to have):
# - audio_to_text:
# -     STT input button


try:
    Print.clear()
    Configuration.commandLoadModelConfiguration()
    Configuration.commandLoadConfiguration()


    args = System.argv
    conversationName = Conversation.getConversationName()


    if len(args) == 1:
        Conversation.setConversation(conversationName)

        keyboardListener = Pynput.keyboard.Listener(on_press=Util.keyListener)
        keyboardListener.start()

        Print.separator()
        Print.generic("Note: This script can interfere with the use of the [" + Util.getKeybindStopName() + "] key.")
        Print.generic("Remap this in code if needed.")  # in modules.Util
        Print.separator()

        Settings.commandSettings()

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
    else:
        def main():
            prompt = ""
            Print.generic("Running in headless mode.")
            del args[0]
            for arg in args:
                arg = arg.replace("\"", "")
                if "--convo=" in arg:
                    conversationName = arg.replace("--convo=", "").replace("'", "")
                    Conversation.setConversation(conversationName)
                elif "--prompt=" in arg:
                    prompt = arg.replace("--prompt=", "")
                else:
                    Print.generic("Unknown argument: " + arg)
                    return
                continue
            if len(prompt) == 0:
                Print.error("You must provide a prompt.")
            else:
                if prompt.startswith("/"):
                    Print.error("You cannot use commands in headless mode.")
                else:
                    Settings.commandSettings()
                    CommandHandler.checkPromptForCommandsAndTriggers(prompt, disableSeed=True)
            return
        main()
except KeyboardInterrupt as ki:
    Print.generic("")
except Exception as e:
    Print.error("An error has occurred: " + str(e))
    Print.error(Traceback.format_exc())
