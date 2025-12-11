# package modules.connection.request


import copy as Copy
import json as JSON
import requests as Requests


import modules.core.Configuration as Configuration
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.string.Endpoint as Endpoint


__lastRequestId = 0
__lastUsedModel = []


def __findModelOnServer(modelNameIn):
    models = getModelsFromServer()
    if models is not None:
        for model in models:
            if model.get("id") is not None:
                id = model["id"]
                if id.lower() == modelNameIn.lower():
                    return True
    return False


def getModelsFromServer():
    result = sendRequest(0, Endpoint.MODELS_ENDPOINT, None, False, True)
    if result is not None:
        Util.printDump("Models on server:" + Util.formatJSONToString(result))
        if result.get("data") is not None:
            data = result["data"]
            return data
    Util.printError("Error getting model list.")
    return None


def updateLastUsed(requestIdIn, modelIn):
    global __lastRequestId, __lastUsedModel

    TypeCheck.enforce(requestIdIn, Types.INTEGER)
    TypeCheck.enforce(modelIn, Types.STRING)

    if modelIn not in __lastUsedModel:
        Util.printInfo("Requesting a different model - it may take a while to load it.")
        Util.printDebug("Loading model: " + modelIn)
    if __lastRequestId != requestIdIn:
        __lastRequestId = requestIdIn
        if modelIn not in __lastUsedModel:
            __lastUsedModel = []
    __lastUsedModel.append(modelIn)
    return


def sendRequest(requestIdIn, endpointIn, dataIn, dataAsFile, returnJson):
    global __lastRequestId, __lastUsedModel

    TypeCheck.enforce(requestIdIn, Types.INTEGER)
    TypeCheck.enforce(endpointIn, Types.STRING)
    TypeCheck.enforceList(dataIn, [Types.DICTIONARY, Types.NONE])
    TypeCheck.enforce(dataAsFile, Types.BOOLEAN)
    TypeCheck.enforce(returnJson, Types.BOOLEAN)

    if len(endpointIn) == 0:
        Util.printError("No endpoint set.")
        return None

    address = Configuration.getConfig("address")
    address = address.replace("/v1", "/")
    postUrl = address + endpointIn

    if dataIn is not None:
        if dataIn.get("model") is not None:
            model = dataIn["model"]
            if not __findModelOnServer(model):
                Util.printError("Requested model does not exist.")
                return None
            nextModel = dataIn.get("model")
            updateLastUsed(requestIdIn, nextModel)
    try:
        if dataIn is not None:
            if dataAsFile:
                Util.printDebug("Sending request to: " + postUrl)
                if dataIn.get("model") is not None:
                    dataIn["model"] = (None, dataIn["model"])
                preview = Copy.deepcopy(dataIn)
                try:
                    preview["file"] = "[TRUNCATED]"
                except Exception:
                    pass
                Util.printDump("Request Data (as file):" + Util.formatJSONToString(preview))
                result = Requests.post(postUrl, files=dataIn)
            else:
                Util.printDebug("Sending request to: " + postUrl)
                preview = Copy.deepcopy(dataIn)
                try:
                    preview["messages"][1]["content"][0]["image_url"]["url"] = "[TRUNCATED]"
                except Exception:
                    pass
                Util.printDump("Request Data:" + Util.formatJSONToString(preview))
                result = Requests.post(postUrl, json=dataIn)
        else:
            Util.printDebug("Sending request to: " + postUrl)
            result = Requests.get(postUrl)
    except Exception as e:
        Util.printError("Error communicating with server.")
        Util.printError(str(e))
        return None

    if result is not None:
        response = str(result)
        resultContent = result.content
        if response == "<Response [200]>":
            if returnJson:
                resultJson = result.json()
                if TypeCheck.check(resultJson, Types.DICTIONARY):
                    if resultJson.get("error") is not None:
                        error = resultJson.get("error")
                        if error.get("message") is not None:
                            message = error["message"]
                            Util.printError("Error: " + message)
                        return
                    # return json.loads(str(resultContent, "utf-8"))
                    return resultJson
                else:
                    Util.printError("Unknown server response format.")
                    Util.printError(str(resultJson))
            else:
                return resultContent
        elif response == "<Response [404]>":
            Util.printError("Resource cannot be found on the server - check the endpoint address.")
        else:
            jsonError = JSON.loads(str(resultContent, "utf-8"))
            if jsonError.get("error") is not None:
                error = jsonError.get("error")
                Util.printError("Error: " + response)
                if error.get("message") is not None:
                    message = error["message"]
                    Util.printError("" + message)
            else:
                Util.printError("Response: " + str(jsonError))
    return None
