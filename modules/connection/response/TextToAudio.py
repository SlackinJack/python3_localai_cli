# modules.connection.response


import modules.connection.request.TextToAudio as TextToAudio
import modules.file.Operation as Operation
import modules.file.Reader as Reader
import modules.string.Path as Path
import modules.Configuration as Configuration
import modules.Model as Model
import modules.Print as Print
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types
import modules.Util as Util


def getTextToAudioResponse(promptIn, silent):
    TypeCheck.check(promptIn, Types.STRING)
    TypeCheck.check(silent, Types.BOOLEAN)

    model = Configuration.getConfig("default_text_to_audio_model")
    if model is None or len(model) == 0:
        Print.error("\nText-to-Audio is disabled because the Text-to-Audio model is not set.\n")
        return None

    textToAudioModel = Model.getModelByNameAndType(Configuration.getConfig("default_text_to_audio_model"), "text_to_audio", False, False, False)
    if textToAudioModel is not None and len(textToAudioModel) > 0:
        model = list(textToAudioModel)[0]
        if textToAudioModel[model].get("backend") is not None:
            backend = textToAudioModel[model]["backend"]

            response = TextToAudio.createTextToAudioRequest(
                {
                    "backend": backend,
                    "input": promptIn,
                    "model": None if model == backend else model,
                }
            )

            if response is not None:
                filename = Path.AUDIO_FILE_PATH + Util.getDateTimeString() + ".wav"
                Operation.writeFileBinary(filename, response)
                if silent:
                    return filename
                else:
                    if Configuration.getConfig("automatically_open_files"):
                        Util.printDebug("\nPlaying Text-to-Audio output...\n")
                        Reader.openLocalFile(filename, None, True)
                    return "Your audio file is available at: " + filename
            else:
                Print.error("\nText-to-Audio creation failed!")
        else:
            Print.error("\nNo backend specified for model.")
    else:
        Print.error("\nCannot find your default Text-to-Audio backend/model.")

    return None
