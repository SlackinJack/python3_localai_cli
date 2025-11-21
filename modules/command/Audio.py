# pacakge modules.command


import threading as Threading


import modules.Audio as Audio
import modules.connection.response.AudioToText as AudioToText
import modules.connection.response.TextToAudio as TextToAudio
import modules.core.Configuration as Configuration
import modules.core.file.Operation as Operation
import modules.core.Print as Print
import modules.core.Util as Util
import modules.PromptHandler as PromptHandler
import modules.string.Path as Path
import modules.string.Strings as Strings


def command():
    def __menu():
        choices = [
            Strings.COMMAND_AUDIO_MENU_PROMPT_TITLE,
            Strings.COMMAND_AUDIO_MENU_TRANSCRIBE_TITLE,
            Strings.COMMAND_AUDIO_MENU_TTS_TITLE,
        ]

        selection = Util.printMenu(Strings.COMMAND_AUDIO_MENU_TITLE, "", choices)
        if selection is None:                                           return
        elif selection == Strings.COMMAND_AUDIO_MENU_PROMPT_TITLE:      submenuAudioToText()
        elif selection == Strings.COMMAND_AUDIO_MENU_TRANSCRIBE_TITLE:  submenuAudioToTextContinuous()
        elif selection == Strings.COMMAND_AUDIO_MENU_TTS_TITLE:         submenuTextToAudio()
        else:                                                           Util.printError(f"\n{Strings.INVALID_SELECTION}\n")
        __menu()
        return
    __menu()
    Print.generic(f"\n{Strings.RETURNING_TO_MAIN_MENU}\n")
    return


def submenuAudioToText():
    while True:
        micInput = Audio.getMicrophoneInput(0)

        if micInput is not None:
            Util.setShouldInterruptCurrentOutputProcess(False)
            Util.startTimer(0)
            result = AudioToText.getResponse(micInput)
            Util.endTimer(0)
            Util.setShouldInterruptCurrentOutputProcess(True)
            Operation.deleteFile(micInput, Configuration.getConfig("disable_all_file_delete_functions"))
            Print.separator()

            if result is not None:
                Print.generic("\nTranscribed speech: " + result + "\n")
                next = Util.printYNQuestion("Continue with this transcript?")

                match next:
                    case 0:
                        PromptHandler.handlePrompt([result], Util.getRandomSeed())
                        break
                    case 1:
                        Print.red("\nDiscarded speech.\n")
                        if not Util.printYNQuestion("Would you like to try again?") == 0:
                            Print.generic(f"\n{Strings.RETURNING_TO_MENU}\n")
                            break
                    case 2:
                        Print.generic(f"\n{Strings.RETURNING_TO_MENU}\n")
                        break
            else:
                Util.printError("\nAn error occurred getting the transcript.\n")
                break
        else:
            Print.generic(f"\n{Strings.RETURNING_TO_MENU}\n")
            break
    return


def submenuAudioToTextContinuous():
    isMicrophoneInUse = False
    transcriptionErrored = False
    transcriptionFileName = ""
    if Configuration.getConfig("live_transcription_to_file"):
        transcriptionFileName = Path.AUDIO_FILE_PATH + Path.MICROPHONE_FILE_TRANSCRIPTION_NAME + Util.getTimeString()
        Operation.writeFile(transcriptionFileName)
    Util.setShouldInterruptCurrentOutputProcess(False)
    Print.generic("\n(Press [" + Util.getKeybindStopName() + "] at any time to stop live transcription.)\n")

    def __getTranscription(micInputIn):
        nonlocal transcriptionErrored, transcriptionFileName
        if not transcriptionErrored and not Util.getShouldInterruptCurrentOutputProcess():
            result = AudioToText.getResponse(micInputIn)
            if result is not None and not transcriptionErrored and not Util.getShouldInterruptCurrentOutputProcess():
                result = Util.cleanupString(result)
                Print.separator()
                Print.response("\n" + result + "\n", "\n")
                if len(transcriptionFileName) > 0:
                    Operation.appendFile(transcriptionFileName, "\n" + result)
            elif result is None:
                Util.setShouldInterruptCurrentOutputProcess(True)
                transcriptionErrored = True
                Util.printError("\nError getting transcript - returning to audio menu.\n")
            Operation.deleteFile(micInputIn, Configuration.getConfig("disable_all_file_delete_functions"))
        return

    while True:
        currentFile = ""
        lastFile = ""
        if not Util.getShouldInterruptCurrentOutputProcess() and not transcriptionErrored:
            if not isMicrophoneInUse:
                isMicrophoneInUse = True
                micInput = Audio.getMicrophoneInput(Configuration.getConfig("live_transcription_delay"))
                if micInput is not None:
                    isMicrophoneInUse = False
                    lastFile = currentFile
                    currentFile = micInput
                    fileToUse = currentFile
                    if len(lastFile) > 0 and len(currentFile) > 0:
                        fileToUse = Audio.combineAudio(lastFile, currentFile)
                    Threading.Thread(target=__getTranscription, args=(fileToUse,)).start()
                else:
                    Util.printError("\nError getting transcription - exiting.\n")
                    transcriptionErrored = True
        else:
            if not isMicrophoneInUse:
                Operation.deleteFilesWithPrefix(Path.AUDIO_FILE_PATH, Path.MICROPHONE_FILE_NAME, Configuration.getConfig("disable_all_file_delete_functions"))
                Print.generic("\nExiting live transcriptions - returning to audio menu.\n")
                break
    return


def submenuTextToAudio():
    prompt = Util.printInput("Enter the text to synthesize")
    if len(prompt) > 0 and not Util.checkEmptyString(prompt):
        Util.startTimer(0)
        Print.generic("\nGetting Text-to-Audio response...\n")
        Util.setShouldInterruptCurrentOutputProcess(False)
        response = TextToAudio.getResponse(prompt, False)
        Util.setShouldInterruptCurrentOutputProcess(True)
        if response is not None:
            Print.response("\n" + response, "\n")
        else:
            Util.printError("\nError getting Text-to-Audio response.")
        Util.endTimer(0)
    else:
        Print.generic("\nText was empty - returning to text menu.\n")
    return
