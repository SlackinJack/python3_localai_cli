# modules.connection.request


import modules.connection.request.Request as Request
import modules.string.Endpoint as Endpoint
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types


def createAudioToTextRequest(dataIn):
    TypeCheck.check(dataIn, Types.DICTIONARY)

    result = Request.sendRequest(Endpoint.STT_ENDPOINT, dataIn, True, True)
    if result is not None:
        if result.get("text") is not None:
            text = result["text"]
            return text

    return None
