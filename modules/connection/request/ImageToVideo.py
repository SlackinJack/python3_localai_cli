# modules.connection.request


import modules.connection.request.Request as Request
import modules.file.Operation as Operation
import modules.string.Endpoint as Endpoint
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types
import modules.Util as Util


def createImageToVideoRequest(dataIn):
    TypeCheck.check(dataIn, Types.DICTIONARY)

    result = Request.sendRequest(Util.getRandomSeed(), Endpoint.IMAGE_ENDPOINT, dataIn, False, True)
    if result is not None:
        if result.get("data") is not None:
            data = result["data"]
            if len(data) > 0:
                data0 = data[0]
                if data0.get("url") is not None:
                    return Operation.getFileFromURL(data0["url"], "image")

    return None
