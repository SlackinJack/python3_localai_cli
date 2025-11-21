#!.venv/bin/python3

# package <root>


import os as OS
import sys as System
import traceback as Traceback


import modules.command.CommandHandler as CommandHandler
import modules.command.CommandMap as CommandMap
import modules.command.Configuration as ConfigurationCommand
import modules.command.Exit as Exit
import modules.command.Model as Model
import modules.command.Settings as Settings
import modules.connection.response.ImageToText as ImageToText
import modules.connection.response.TextToImage as TextToImage
import modules.Conversation as Conversation
import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.string.Prompt as Prompt
import modules.string.Strings as Strings


# disable selenium stats for cleaner output when using headless mode
OS.environ["SE_AVOID_STATS"] = "1"


# TODO:

# TODO (tests):

# TODO (nice to have):
# - audio_to_text:
# -     STT input button


def __headlessTextToText(promptIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    CommandHandler.checkPromptForCommandsAndTriggers(promptIn, True)
    return


def __headlessImageToText(promptIn, imageLocationIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    TypeCheck.enforce(imageLocationIn, Types.STRING)
    if len(imageLocationIn) == 0:
        Configuration.setConfig("debug_level", 1)
        Util.printError(Strings.MUST_INPUT_IMAGE_STRING)
        return
    result = ImageToText.getResponse(promptIn, imageLocationIn)
    if result is not None:
        Print.response("\n" + result + "\n", "\n")
    return


def __headlessTextToImage(promptIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    result = TextToImage.getResponse(0, promptIn, "", None, 2, None)
    if result is not None:
        Print.response(result)
    return


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
        Print.generic(Strings.getKeyInterferenceString(Util.getKeybindStopName()))  # in modules.core.Util
        Print.separator()

        Settings.commandSettings()

        def __main():
            prompt = Util.printInput(Strings.INPUT_PROMPT_STRING)
            if not Util.checkEmptyString(prompt):
                if prompt == "exit" or prompt == "0" or prompt.startswith("/exit"):
                    keyboardListener.stop()
                    Exit.commandExit()
                    return
                else:
                    CommandHandler.checkPromptForCommandsAndTriggers(prompt, False)
            else:
                CommandMap.commandHelp()
            __main()
        __main()

    # headless entry
    else:
        def __main():
            prompt = ""
            imageLocation = ""
            debugLevel = 0
            mode = "text-to-text"
            Configuration.setConfig("debug_level", 1)
            Configuration.setConfig("enable_internet", False)
            Configuration.setConfig("enable_functions", False)
            Configuration.setConfig("do_reprompts", False)
            del args[0]
            for arg in args:
                arg = arg.replace("\"", "")
                if "--help" in arg:
                    Print.generic(Strings.HEADLESS_HELP_STRING)
                    return
                elif "--mode=" in arg:
                    mode = arg.split("--mode=")[1]
                elif "--prompt=" in arg:
                    prompt = arg.split("--prompt=")[1]
                elif "--model=" in arg:
                    Model.modelChangerHeadless(arg.split("--model=")[1])
                elif "--convo=" in arg:
                    Conversation.setConversation(arg.split("--convo=")[1])
                    Configuration.setConfig("enable_chat_history_consideration", True)
                elif "--functions" in arg:
                    Configuration.setConfig("enable_functions", True)
                elif "--internet" in arg:
                    Configuration.setConfig("enable_internet", True)
                elif "--image=" in arg:
                    imageLocation = arg.split("--image=")[1]
                elif "--debug_level=" in arg:
                    try:
                        debugLevel = int(arg.split("--debug_level=")[1])
                    except:
                        Util.printError("--debug_level expects an integer.")
                        return
                elif "--system_prompt=" in arg:
                    Configuration.setConfig("system_prompt", arg.split("--system_prompt=")[1])
                elif "--line_break_threshold=" in arg:
                    Configuration.setConfig("line_break_threshold", int(arg.split("--line_break_threshold=")[1]))
                else:
                    Util.printError(Strings.UNKNOWN_ARGUMENT_STRING + arg)
                    return
                continue
            if len(prompt) > 0:
                if prompt.startswith("/"):
                    Util.printError(Strings.COMMANDS_NOT_ALLOWED_STRING)
                    return
            else:
                if len(prompt) == 0:
                    if mode != "image-to-text":
                        Util.printError(Strings.MUST_INPUT_PROMPT_STRING)
                        return
                    else:
                        prompt = Prompt.getImageToTextDefaultUserPrompt()
            Configuration.setConfig("debug_level", debugLevel)
            match mode:
                case "text-to-text":
                    return __headlessTextToText(prompt)
                case "image-to-text":
                    return __headlessImageToText(prompt, imageLocation)
                case "text-to-image":
                    return __headlessTextToImage(prompt)
                case _:
                    Util.printError(Strings.UNSUPPORTED_MODE_STRING + mode)
                    return
            return
        __main()
except KeyboardInterrupt as ki:
    Print.generic("")
except Exception as e:
    Util.printError(Strings.ERROR_OCCURRED_STRING + str(e))
    Util.printError(Traceback.format_exc())

