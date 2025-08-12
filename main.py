#!.venv/bin/python3

# <root>


import os as OS
import pynput as Pynput
import sys as System
import traceback as Traceback


import modules.command.CommandHandler as CommandHandler
import modules.command.CommandMap as CommandMap
import modules.command.Configuration as ConfigurationCommand
import modules.command.Exit as Exit
import modules.command.Model as Model
import modules.command.Settings as Settings
import modules.Configuration as Configuration
import modules.Conversation as Conversation
import modules.Print as Print
import modules.Util as Util


# disable selenium stats for cleaner output when using headless mode
OS.environ["SE_AVOID_STATS"] = "1"


# TODO:
# - audio:
# -     dont write anything to disk

# TODO (tests):

# TODO (nice to have):
# - audio_to_text:
# -     STT input button


try:
    ConfigurationCommand.commandLoadModelConfiguration()
    ConfigurationCommand.commandLoadConfiguration()


    args = System.argv
    conversationName = Conversation.getConversationName()


    if len(args) == 1:
        Print.clear()
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
            type = "text-to-text"
            Configuration.setConfig("debug_level", 0)
            Configuration.setConfig("enable_internet", False)
            Configuration.setConfig("enable_functions", False)
            Configuration.setConfig("do_reprompts", False)
            del args[0]
            for arg in args:
                arg = arg.replace("\"", "").replace("\'", "")
                if "--help" in arg:
                    Print.generic("""This script can be in two modes.
Run the script without arguments: CLI mode with all supported features.
Run the script with arguments: headless single-use mode.

Headless mode arguments:

[Required]
--prompt="<prompt>"     : the prompt to process

[Optional]
--model="<modelname>"   : set the model to use (unset = config text-to-text model)
--convo="<filename>"    : set the conversation file in output/conversations (unset = new file)
--functions             : enable functions
--internet              : enable internet
""")
                    return
                elif "--convo=" in arg:
                    Conversation.setConversation(arg.replace("--convo=", ""))
                    Configuration.setConfig("enable_chat_history_consideration", True)
                elif "--model=" in arg:
                    Model.modelChangerHeadless(arg.replace("--model=", ""))
                elif "--prompt=" in arg:
                    prompt = arg.replace("--prompt=", "")
                elif "--internet" in arg:
                    Configuration.setConfig("enable_internet", True)
                elif "--functions" in arg:
                    Configuration.setConfig("enable_functions", True)
                else:
                    Print.generic("Unknown argument: " + arg)
                    return
                continue
            if len(prompt) == 0:
                Util.printError("You must provide a prompt.")
            else:
                if prompt.startswith("/"):
                    Util.printError("You cannot use commands in headless mode.")
                else:
                    match type:
                        case "text-to-text":
                            CommandHandler.checkPromptForCommandsAndTriggers(prompt, disableSeed=True)
                        case _:
                            # TODO: raise ex
                            return
            return
        main()
except KeyboardInterrupt as ki:
    Print.generic("")
except Exception as e:
    Util.printError("An error has occurred: " + str(e))
    Util.printError(Traceback.format_exc())
