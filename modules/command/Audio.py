# modules.command


import threading as Threading


import modules.connection.response.AudioToText as AudioToText
import modules.connection.response.TextToAudio as TextToAudio
import modules.file.Operation as Operation
import modules.string.Path as Path
import modules.Audio as Audio
import modules.Configuration as Configuration
import modules.Print as Print
import modules.PromptHandler as PromptHandler
import modules.Util as Util


def commandAudio():
    def menu():
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
        else:                                                   Print.error("\nInvalid selection.\n")
        menu()
        return
    menu()
    Print.generic("\nReturning to main menu.\n")
    return


def submenuAudioToText():
    while True:
        micInput = Audio.getMicrophoneInput(0)

        if micInput is not None:
            Util.startTimer(0)
            result = AudioToText.getAudioToTextResponse(micInput)
            Util.endTimer(0)
            Operation.deleteFile(micInput)  # for legal reasons
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
                            Print.generic("\nReturning to menu.\n")
                            break
                    case 2:
                        Print.generic("\nReturning to menu.\n")
                        break
            else:
                Print.error("\nAn error occurred getting the transcript.\n")
                break
        else:
            Print.generic("\nReturning to menu.\n")
            break
    return


def submenuAudioToTextContinuous():
    isMicrophoneInUse = False
    transcriptionErrored = False
    Util.setShouldInterruptCurrentOutputProcess(False)
    Print.generic("\n(Press [" + Util.getKeybindStopName() + "] at any time to stop live transcription.)\n")

    def getTranscription(micInputIn):
        nonlocal transcriptionErrored
        transcriptionFileName = ""
        if Configuration.getConfig("live_transcription_to_file"):
            transcriptionFileName = Path.AUDIO_FILE_PATH + Path.MICROPHONE_FILE_TRANSCRIPTION_NAME + Util.getTimeString()
            Operation.writeFile(transcriptionFileName)
        if not transcriptionErrored and not Util.getShouldInterruptCurrentOutputProcess():
            result = AudioToText.getAudioToTextResponse(micInputIn)
            if result is not None and not transcriptionErrored and not Util.getShouldInterruptCurrentOutputProcess():
                Print.separator()
                Print.response("\n" + result + "\n", "\n")
                if len(transcriptionFileName) > 0:
                    Operation.appendFile(transcriptionFileName, "\n" + result)
            elif result is None:
                Util.setShouldInterruptCurrentOutputProcess(True)
                transcriptionErrored = True
                Print.error("\nError getting transcript - returning to audio menu.\n")
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
                    Threading.Thread(target=getTranscription, args=(fileToUse,)).start()
                else:
                    Print.error("\nError getting transcription - exiting.\n")
                    transcriptionErrored = True
        else:
            if not isMicrophoneInUse:
                Operation.deleteFilesWithPrefix(Path.AUDIO_FILE_PATH, Path.MICROPHONE_FILE_NAME)
                Print.generic("\nExiting live transcriptions - returning to audio menu.\n")
                break
    return


def submenuTextToAudio():
    prompt = Util.printInput("Enter the text to synthesize")
    if len(prompt) > 0 and not Util.checkEmptyString(prompt):
        Util.startTimer(0)
        Print.generic("\nGetting Text-to-Audio response...\n")
        response = TextToAudio.getTextToAudioResponse(prompt, False)
        if response is not None:
            Print.response("\n" + response, "\n")
        else:
            Print.error("\nError getting Text-to-Audio response.")
        Util.endTimer(0)
    else:
        Print.generic("\nText was empty - returning to text menu.\n")
    return
