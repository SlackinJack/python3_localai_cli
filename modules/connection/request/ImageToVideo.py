# package modules.connection.request


import modules.connection.request.Request as Request
import modules.core.file.Operation as Operation
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.string.Endpoint as Endpoint


def createImageToVideoRequest(dataIn):
    TypeCheck.enforce(dataIn, Types.DICTIONARY)

    while not Util.getShouldInterruptCurrentOutputProcess():
        result = Request.sendRequest(Util.getRandomSeed(), Endpoint.IMAGE_ENDPOINT, dataIn, False, True)
        if result is not None:
            if result.get("data") is not None:
                data = result["data"]
                if len(data) > 0:
                    data0 = data[0]
                    if data0.get("url") is not None:
                        return Operation.getFileFromURL(data0["url"], "image")
        return None
    return None
