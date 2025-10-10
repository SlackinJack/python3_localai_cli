# package modules


import modules.connection.response.TextToText as TextToText
import modules.core.Configuration as Configuration
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.string.Strings as Strings


def handlePrompt(promptWithDataIn, seedIn):
    TypeCheck.enforce(promptWithDataIn, Types.LIST)
    TypeCheck.enforce(seedIn, Types.INTEGER)
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
        Util.printInfo(f"\n{Strings.FUNCTIONS_DISABLED_STRING}")
        return TextToText.getTextToTextResponseStreamed(promptIn, seedIn, datas, True, False, "")
