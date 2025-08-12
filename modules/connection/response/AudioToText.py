# modules.connection.response


import modules.connection.request.AudioToText as AudioToText
import modules.file.Operation as Operation
import modules.Configuration as Configuration
import modules.Print as Print
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types


def getAudioToTextResponse(audioFilePathIn):
    TypeCheck.check(audioFilePathIn, Types.STRING)

    model = Configuration.getConfig("default_audio_to_text_model")
    if model is None or len(model) == 0:
        Util.printError("\nAudio-to-Text is disabled because the Audio-to-Text model is not set.\n")
        return None

    if Operation.fileExists(audioFilePathIn):
        response = AudioToText.createAudioToTextRequest(
            {
                "file": Operation.readFileBinary(audioFilePathIn),
                "model": Configuration.getConfig("default_audio_to_text_model"),
            }
        )
        if response is not None:
            return response
        else:
            Util.printError("\nError getting transcriptions.\n")
    else:
        Util.printError("\nFile does not exist!\n")

    return None
