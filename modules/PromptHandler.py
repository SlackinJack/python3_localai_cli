# modules.util


import modules.connection.response.TextToText as TextToText
import modules.Configuration as Configuration
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types
import modules.Util as Util


def handlePrompt(promptWithDataIn, seedIn):
    TypeCheck.check(promptWithDataIn, Types.LIST)
    TypeCheck.check(seedIn, Types.INTEGER)
    promptIn = promptWithDataIn[0]
    datas = []
    if len(promptWithDataIn) > 1:
        skipFirst = False
        for data in promptWithDataIn:
            if not skipFirst:
                skipFirst = True
                continue
            else:
                datas.append(data)
    if Configuration.getConfig("enable_functions"):
        return TextToText.getTextToTextResponseFunctions(promptIn, seedIn, datas)
    else:
        Util.printInfo("\nFunctions are disabled - using chat completion only.")
        return TextToText.getTextToTextResponseStreamed(promptIn, seedIn, datas, True)
