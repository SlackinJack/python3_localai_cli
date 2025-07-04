# modules.command


import json as JSON


import modules.connection.request.Request as Request
import modules.string.Endpoint as Endpoint
import modules.Print as Print
import modules.Util as Util


def commandCurl():
    choices = [
        "Apply",
        "Available",
        "Models",
        "Raw"
    ]

    def menu():
        selection = Util.printMenu("cURL menu", "", choices)
        if selection is None:
            return
        elif selection == "Apply":
            Request.sendRequest(0, Endpoint.MODELS_APPLY_ENDPOINT, None, False, True)
        elif selection == "Available":
            Request.sendRequest(0, Endpoint.MODELS_AVAILABLE_ENDPOINT, None, False, True)
        elif selection == "Models":
            Request.sendRequest(0, Endpoint.MODELS_ENDPOINT, None, False, True)
        elif selection == "Raw":
            submenuCurlRaw()
        else:
            Print.error("\nInvalid selection.\n")
        menu()
        return
    menu()
    Print.generic("\nReturning to main menu.\n")
    return


def submenuCurlRaw():
    endpoint = Util.printInput("Enter the endpoint (eg. v1/chat/completions)")
    jsonData = "{" + Util.printInput("Input the JSON data") + "}"
    Request.sendRequest(0, endpoint, JSON.loads(jsonData), False, True)
    return
