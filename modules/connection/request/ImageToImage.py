# package modules.connection.request


import modules.connection.request.Request as Request
import modules.core.file.Operation as Operation
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.string.Endpoint as Endpoint


def createImageToImageRequest(dataIn):
    TypeCheck.check(dataIn, Types.DICTIONARY)

    result = Request.sendRequest(Util.getRandomSeed(), Endpoint.IMAGE_ENDPOINT, dataIn, False, True)
    if result is not None:
        if result.get("data") is not None:
            data = result["data"]
            if len(data) > 0:
                data0 = data[0]
                if data0.get("url") is not None:
                    url = data0["url"]
                    return Operation.getFileFromURL(url, "image")

    return None
