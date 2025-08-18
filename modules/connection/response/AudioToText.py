# package modules.connection.response


import modules.connection.request.AudioToText as AudioToText
import modules.core.file.Operation as Operation
import modules.core.Configuration as Configuration
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util


def getAudioToTextResponse(audioFilePathIn):
    TypeCheck.enforce(audioFilePathIn, Types.STRING)

    model = Configuration.getConfig("default_audio_to_text_model")
    if model is None or len(model) == 0:
        Util.printError("\nAudio-to-Text is disabled because the Audio-to-Text model is not set.\n")
        return None

    if Operation.fileExists(audioFilePathIn):
        Util.setShouldInterruptCurrentOutputProcess(False)
        response = AudioToText.createAudioToTextRequest(
            {
                "file": Operation.readFileBinary(audioFilePathIn),
                "model": Configuration.getConfig("default_audio_to_text_model"),
            }
        )
        Util.setShouldInterruptCurrentOutputProcess(True)
        if response is not None:
            return response
        else:
            Util.printError("\nError getting transcriptions.\n")
    else:
        Util.printError("\nFile does not exist!\n")
    return None
