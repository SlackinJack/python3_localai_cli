# package modules.command


import json as JSON


import modules.connection.request.Request as Request
import modules.core.Print as Print
import modules.core.Util as Util
import modules.string.Endpoint as Endpoint


def command():
    choices = [
        "Apply",
        "Available",
        "Models",
        "Raw"
    ]

    def __menu():
        selection = Util.printMenu("cURL menu", "", choices)
        if selection is None:
            return
        elif selection == "Apply":      Request.sendRequest(0, Endpoint.MODELS_APPLY_ENDPOINT, None, False, True)
        elif selection == "Available":  Request.sendRequest(0, Endpoint.MODELS_AVAILABLE_ENDPOINT, None, False, True)
        elif selection == "Models":     Request.sendRequest(0, Endpoint.MODELS_ENDPOINT, None, False, True)
        elif selection == "Raw":        submenuCurlRaw()
        else:                           Util.printError("Invalid selection.")
        __menu()
        return
    __menu()
    Print.generic("Returning to main menu.")
    return


def submenuCurlRaw():
    endpoint = Util.printInput("Enter the endpoint (eg. v1/chat/completions)")
    jsonData = "{" + Util.printInput("Input the JSON data") + "}"
    Request.sendRequest(0, endpoint, JSON.loads(jsonData), False, True)
    return
