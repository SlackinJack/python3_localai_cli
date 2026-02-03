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


def command():
    def __menu():
        choices = [
            "Audio-to-Text (Prompt)",
            "Audio-to-Text (Live Transcription)",
            "Text-to-Audio",
        ]

        selection = Util.printMenu("Audio menu", "", choices)
        if selection is None:                                   return
        elif selection == "Audio-to-Text (Prompt)":             submenuAudioToText()
        elif selection == "Audio-to-Text (Live Transcription)": submenuAudioToTextContinuous()
        elif selection == "Text-to-Audio":                      submenuTextToAudio()
        else:                                                   Util.printError("Invalid selection.")
        __menu()
        return
    __menu()
    Print.generic("Returning to main menu.")
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
                Print.generic("Transcribed speech: " + result)
                next = Util.printYNQuestion("Continue with this transcript?")

                match next:
                    case 0:
                        PromptHandler.handlePrompt([result], Util.getRandomSeed())
                        break
                    case 1:
                        Print.red("Discarded speech.")
                        if not Util.printYNQuestion("Would you like to try again?") == 0:
                            Print.generic("Returning to menu.")
                            break
                    case 2:
                        Print.generic("Returning to menu.")
                        break
            else:
                Util.printError("An error occurred getting the transcript.")
                break
        else:
            Print.generic("Returning to menu.")
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
    Print.generic("(Press [" + Util.getKeybindStopName() + "] at any time to stop live transcription.)")

    def __getTranscription(micInputIn):
        nonlocal transcriptionErrored, transcriptionFileName
        if not transcriptionErrored and not Util.getShouldInterruptCurrentOutputProcess():
            result = AudioToText.getResponse(micInputIn)
            if result is not None and not transcriptionErrored and not Util.getShouldInterruptCurrentOutputProcess():
                result = Util.cleanupString(result)
                Print.separator()
                Print.response(result, "")
                if len(transcriptionFileName) > 0:
                    Operation.appendFile(transcriptionFileName, result)
            elif result is None:
                Util.setShouldInterruptCurrentOutputProcess(True)
                transcriptionErrored = True
                Util.printError("Error getting transcript - returning to audio menu.")
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
                    Util.printError("Error getting transcription - exiting.")
                    transcriptionErrored = True
        else:
            if not isMicrophoneInUse:
                Operation.deleteFilesWithPrefix(Path.AUDIO_FILE_PATH, Path.MICROPHONE_FILE_NAME, Configuration.getConfig("disable_all_file_delete_functions"))
                Print.generic("Exiting live transcriptions - returning to audio menu.")
                break
    return


def submenuTextToAudio():
    prompt = Util.printInput("Enter the text to synthesize")
    if len(prompt) > 0 and not Util.checkEmptyString(prompt):
        Util.startTimer(0)
        Print.generic("Getting Text-to-Audio response...")
        Util.setShouldInterruptCurrentOutputProcess(False)
        response = TextToAudio.getResponse(prompt, False)
        Util.setShouldInterruptCurrentOutputProcess(True)
        if response is not None:
            Print.response(response, "")
        else:
            Util.printError("Error getting Text-to-Audio response.")
        Util.endTimer(0)
    else:
        Print.generic("Text was empty - returning to text menu.")
    return
