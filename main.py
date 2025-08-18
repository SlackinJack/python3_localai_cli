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

        import pynput as Pynput
        keyboardListener = Pynput.keyboard.Listener(on_press=Util.keyListener)
        keyboardListener.start()

        Print.separator()
        Print.generic("Note: This script can interfere with the use of the [" + Util.getKeybindStopName() + "] key.")
        Print.generic("Remap this in code if needed.")  # in modules.core.Util
        Print.separator()

        Settings.commandSettings()

        def __main():
            prompt = Util.printInput("Enter a prompt (\"/help\" for list of commands)")
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
                    Print.generic("""This script can be in two modes.
Run the script without arguments: CLI mode with all supported features.
Run the script with arguments: headless single-prompt mode.
By default, internet and functions are disabled for headless-mode.
Reprompting is not supported in headless-mode.

========================
Headless-mode modes:
========================
- text-to-text (default)
- text-to-image
- image-to-text

========================
Headless-mode arguments:
========================
[Required]
--prompt="<prompt>"         : the prompt to process
--image="<imagepath>"       : image path (only required for image-to-x modes)

[Optional]
--mode="<mode>"             : set the operation mode (unset = text-to-text)
--model="<modelname>"       : set the model to use (unset = config)
--convo="<filename>"        : set the conversation file in output/conversations/ (unset = new file)
--functions                 : enable functions for this prompt
--internet                  : enable internet for this prompt
--system_prompt="<prompt>   : set the system prompt (unset = config)"
--debug_level=X             : set the debug level (unset = 0)
--line_break_threshold=X    : set the line-break threshold (unset = config)
""")
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
                        Util.printError("--debug_level expects integer.")
                        return
                elif "--system_prompt=" in arg:
                    Configuration.setConfig("system_prompt", arg.split("--system_prompt=")[1])
                elif "--line_break_threshold=" in arg:
                    Configuration.setConfig("line_break_threshold", int(arg.split("--line_break_threshold=")[1]))
                else:
                    Util.printError("Unknown argument: " + arg)
                    return
                continue
            if len(prompt) > 0:
                if prompt.startswith("/"):
                    Util.printError("You cannot use commands in headless mode.")
                    return
            else:
                if len(prompt) == 0:
                    if mode != "image-to-text":
                        Util.printError("You must provide a prompt.")
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
                    Util.printError("Unsupported mode: " + mode)
                    return
            return
        __main()
except KeyboardInterrupt as ki:
    Print.generic("")
except Exception as e:
    Util.printError("An error has occurred: " + str(e))
    Util.printError(Traceback.format_exc())


def __headlessTextToText(promptIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    CommandHandler.checkPromptForCommandsAndTriggers(promptIn, True)
    return


def __headlessImageToText(promptIn, imageLocationIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    TypeCheck.enforce(imageLocationIn, Types.STRING)
    if len(imageLocationIn) == 0:
        Configuration.setConfig("debug_level", 1)
        Util.printError("You must provide an image.")
        return
    result = ImageToText.getImageToTextResponse(promptIn, imageLocationIn)
    if result is not None:
        Print.response("\n" + result + "\n", "\n")
    return


def __headlessTextToImage(promptIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    result = TextToImage.getTextToImageResponse(0, promptIn, "", None, 2, None)
    if result is not None:
        Print.response(result)
    return
