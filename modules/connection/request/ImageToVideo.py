# modules.connection.request


import modules.connection.request.Request as Request
import modules.file.Operation as Operation
import modules.string.Endpoint as Endpoint
import modules.Configuration as Configuration
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types


def createImageToVideoRequest(dataIn):
    TypeCheck.check(dataIn, Types.DICTIONARY)

    result = Request.sendRequest(Endpoint.IMAGE_ENDPOINT, dataIn, False, True)
    if result is not None:
        if result.get("data") is not None:
            data = result["data"]
            if len(data) > 0:
                data0 = data[0]
                if data0.get("url") is not None:
                    url = data0["url"]
                    new_file_ext = Configuration.getConfig("video_format")
                    new_url = url.replace(".png", new_file_ext)
                    return Operation.getFileFromURL(new_url, "image")

    return None
