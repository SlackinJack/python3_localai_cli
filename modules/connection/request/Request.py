# modules.connection.request


import json as JSON
import requests as Requests


import modules.string.Endpoint as Endpoint
import modules.Configuration as Configuration
import modules.Print as Print
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types
import modules.Util as Util


def sendRequest(endpointIn, dataIn, dataAsFile, returnJson):
    TypeCheck.check(endpointIn, Types.STRING)
    TypeCheck.checkList(dataIn, [Types.DICTIONARY, Types.NONE])
    TypeCheck.check(dataAsFile, Types.BOOLEAN)
    TypeCheck.check(returnJson, Types.BOOLEAN)

    if len(endpointIn) == 0:
        Print.error("\nNo endpoint set.\n")
        return None

    address = Configuration.getConfig("address")
    address = address.replace("/v1", "/")
    postUrl = address + endpointIn

    if dataIn is not None:
        if dataIn.get("model") is not None:
            model = dataIn["model"]
            if not findModelOnServer(model):
                Print.error("\nRequested model does not exist.")
                return None
    try:
        if dataIn is not None:
            if dataAsFile:
                Util.printDebug("\nSending request to: " + postUrl)
                if dataIn.get("model") is not None:
                    dataIn["model"] = (None, dataIn["model"])
                preview = dataIn.copy()
                try:
                    preview["file"] = "[TRUNCATED]"
                except Exception as e:
                    pass
                Util.printDump("\nRequest Data (as file):\n" + Util.formatJSONToString(preview))
                result = Requests.post(postUrl, files=dataIn)
            else:
                Util.printDebug("\nSending request to: " + postUrl)
                preview = dataIn.copy()
                try:
                    preview["messages"][0]["content"][1]["image_url"] = "[TRUNCATED]"
                except Exception as e:
                    pass
                Util.printDump("\nRequest Data:\n" + Util.formatJSONToString(dataIn))
                result = Requests.post(postUrl, json=dataIn)
        else:
            Util.printDebug("\nSending request to: " + postUrl)
            result = Requests.get(postUrl)
    except Exception as e:
        Print.error("\nError communicating with server.")
        Print.error(str(e))
        return None

    if result is not None:
        response = str(result)
        resultContent = result.content
        if response == "<Response [200]>":
            if returnJson:
                resultJson = result.json()
                if TypeCheck.softcheck(resultJson, Types.DICTIONARY):
                    if resultJson.get("error") is not None:
                        error = resultJson.get("error")
                        if error.get("message") is not None:
                            message = error["message"]
                            Print.error("\nError: " + message)
                        return
                    # return json.loads(str(resultContent, "utf-8"))
                    return resultJson
                else:
                    Print.error("\nUnknown server response format.\n")
                    Print.error(str(resultJson))
            else:
                return resultContent
        elif response == "<Response [404]>":
            Print.error("\nResource cannot be found on the server - check the endpoint address.\n")
        else:
            jsonError = JSON.loads(str(resultContent, "utf-8"))
            if jsonError.get("error") is not None:
                error = jsonError.get("error")
                Print.error("\nError: " + response)
                if error.get("message") is not None:
                    message = error["message"]
                    Print.error("\n" + message)
            else:
                Print.error("\nResponse: " + str(jsonError))
    return None


def getModelsFromServer():
    result = sendRequest(Endpoint.MODELS_ENDPOINT, None, False, True)
    if result is not None:
        Util.printDump("\nModels on server:\n" + Util.formatJSONToString(result))
        # if not Util.checkEmptyString(result):
        if result.get("data") is not None:
            data = result["data"]
            return data
    Print.error("\nError getting model list.")
    return None


def findModelOnServer(modelNameIn):
    TypeCheck.check(modelNameIn, Types.STRING)

    models = getModelsFromServer()
    if models is not None:
        for model in models:
            if model.get("id") is not None:
                id = model["id"]
                if id.lower() == modelNameIn.lower():
                    return True

    return False
