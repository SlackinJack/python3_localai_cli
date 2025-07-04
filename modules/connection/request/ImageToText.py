# modules.connection.request


import modules.connection.request.Request as Request
import modules.string.Endpoint as Endpoint
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types
import modules.Util as Util


def createImageToTextRequest(dataIn):
    TypeCheck.check(dataIn, Types.DICTIONARY)

    result = Request.sendRequest(Util.getRandomSeed(), Endpoint.TEXT_ENDPOINT, dataIn, False, True)
    if result is not None:
        if result.get("choices") is not None:
            choices = result["choices"]
            if len(choices) > 0:
                choices0 = choices[0]
                if choices0.get("message") is not None:
                    message = choices0["message"]
                    if message.get("content") is not None:
                        content = message["content"]
                        return content

    return None
