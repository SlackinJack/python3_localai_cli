# modules.connection.request


import modules.connection.request.Request as Request
import modules.string.Endpoint as Endpoint
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types


def createTextToAudioRequest(dataIn):
    TypeCheck.check(dataIn, Types.DICTIONARY)

    result = Request.sendRequest(Endpoint.TTS_ENDPOINT, dataIn, False, False)
    if result is not None:
        return result

    return None
