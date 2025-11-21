# package modules.connection.request


import modules.connection.request.Request as Request
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.string.Endpoint as Endpoint


def createRequest(dataIn):
    TypeCheck.enforce(dataIn, Types.DICTIONARY)

    # handled in command
    # while not Util.getShouldInterruptCurrentOutputProcess():
    result = Request.sendRequest(Util.getRandomSeed(), Endpoint.TTS_ENDPOINT, dataIn, False, False)
    if result is not None:
        return result

    return None
