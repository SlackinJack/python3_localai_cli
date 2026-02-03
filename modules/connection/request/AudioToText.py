# package modules.connection.request


import modules.connection.request.Request as Request
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.string.Endpoint as Endpoint


def createRequest(dataIn):
    TypeCheck.enforce(dataIn, Types.DICTIONARY)

    while not Util.getShouldInterruptCurrentOutputProcess():
        result = Request.sendRequest(Util.getRandomSeed(), Endpoint.STT_ENDPOINT, dataIn, True, True)
        if result is not None:
            if result.get("text") is not None:
                text = result["text"]
                return text
        return None
    return None
