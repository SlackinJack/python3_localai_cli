# package modules.connection.response


import json as JSON


import modules.connection.request.TextToAudio as TextToAudio
import modules.core.file.Operation as Operation
import modules.core.file.Reader as Reader
import modules.core.Configuration as Configuration
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.Model as Model
import modules.string.Path as Path


def getResponse(promptIn, silent):
    TypeCheck.enforce(promptIn, Types.STRING)
    TypeCheck.enforce(silent, Types.BOOLEAN)

    model = Configuration.getConfig("default_text_to_audio_model")
    if model is None or len(model) == 0:
        Util.printError("Text-to-Audio is disabled because the Text-to-Audio model is not set.")
        return None

    textToAudioModel = Model.getModelByNameAndType(Configuration.getConfig("default_text_to_audio_model"), "text_to_audio", False, False, False)
    if textToAudioModel is not None and len(textToAudioModel) > 0:
        model = list(textToAudioModel)[0]
        if textToAudioModel[model].get("backend") is not None:
            backend = textToAudioModel[model]["backend"]
            requestParameters = {
                "backend": backend,
                "input": promptIn,
                "model": None if model == backend else model,
            }
            Util.setShouldInterruptCurrentOutputProcess(False)
            response = TextToAudio.createRequest(requestParameters)
            Util.setShouldInterruptCurrentOutputProcess(True)

            if response is not None:
                filename = Path.AUDIO_FILE_PATH + Util.getDateTimeString() + ".wav"
                Operation.writeFileBinary(filename, response)
                if Configuration.getConfig("write_output_params"):
                    Operation.appendFile(filename + ".params", JSON.dumps(requestParameters, indent=4))
                if silent:
                    return filename
                else:
                    if Configuration.getConfig("automatically_open_files"):
                        Util.printDebug("Playing Text-to-Audio output...")
                        Reader.openLocalFile(filename, None, True)
                    return "Your audio file is available at: " + filename
            else:
                Util.printError("Text-to-Audio creation failed!")
        else:
            Util.printError("No backend specified for model.")
    else:
        Util.printError("Cannot find your default Text-to-Audio backend/model.")

    return None
