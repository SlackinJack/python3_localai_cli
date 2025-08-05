# modules.connection.request


import modules.connection.request.Request as Request
import modules.file.Operation as Operation
import modules.string.Endpoint as Endpoint
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types
import modules.Util as Util


def createTextToImageRequest(requestIdIn, dataIn):
    TypeCheck.check(requestIdIn, Types.INTEGER)
    TypeCheck.check(dataIn, Types.DICTIONARY)

    result = Request.sendRequest(requestIdIn, Endpoint.IMAGE_ENDPOINT, dataIn, False, True)
    if result is not None:
        if result.get("data") is not None:
            data = result["data"]
            if len(data) > 0:
                data0 = data[0]
                if data0.get("url") is not None:
                    url = data0["url"]
                    return Operation.getFileFromURL(url, "image")

    return None
