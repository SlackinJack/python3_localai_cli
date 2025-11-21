# package modules.command


import modules.core.Configuration as Configuration
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Print as Print
import modules.core.Util as Util
import modules.Model as Model


def modelVerifier(nextModelIn, modelTypeIn):
    TypeCheck.enforce(nextModelIn, Types.STRING)
    TypeCheck.enforce(modelTypeIn, Types.STRING)
    result = Model.getModelByNameAndType(nextModelIn, modelTypeIn, True, False, False)
    return [result, (result is not None)]


def command():
    def __menu():
        choices = [
            "Change Models",
            "Scan Server for Models",
        ]

        selection = Util.printMenu("Model menu", "", choices)
        if selection is None:                       return
        elif selection == "Change Models":          submenuChangeModel()
        elif selection == "Scan Server for Models": modelScanner()
        else:                                       Util.printError("\nInvalid selection.\n")
        __menu()
        return
    __menu()
    Print.generic("\nReturning to main menu.\n")
    return


def submenuChangeModel():
    choices = list(Model.getModelTypes().values())

    def __menu():
        selection = Util.printMenu("Model menu", "(Tip: You can use spaces to match for long model names!)", choices)
        matched = False
        if selection is None:
            return
        else:
            for k, v in Model.getModelTypes().items():
                if selection == v:
                    matched = True
                    modelChanger(k, v)
                    break
            if not matched:
                Util.printError("\nInvalid selection.\n")
        __menu()
        return
    __menu()
    Print.generic("\nReturning to model menu.\n")
    return


def modelChanger(modelTypeIn, modelTypeNameIn):
    TypeCheck.enforce(modelTypeIn, Types.STRING)
    TypeCheck.enforce(modelTypeNameIn, Types.STRING)
    choices = list(Model.getModelsWithType(modelTypeIn))
    selection = Util.printMenu("Available models", "", choices)
    if selection is not None:
        if len(selection) > 0:
            matched = modelVerifier(selection, modelTypeIn)
            if matched[1]:
                Configuration.setConfig("default_" + modelTypeIn + "_model", matched[0])
                Print.green("\n" + modelTypeNameIn + " model set to: " + matched[0] + "\n")
            else:
                Util.printError(
                    "\nCannot find a match - keeping current " + modelTypeNameIn + " model:"
                    " " + Configuration.getConfig("default_" + modelTypeIn + "_model") + "\n"
                )
        else:
            Print.red("\nInvalid selection - returning to models menu.\n")
    else:
        Print.red("\nKeeping current model: " + Configuration.getConfig("default_" + modelTypeIn + "_model") + "\n")
    return


def modelChangerHeadless(modelNameIn):
    TypeCheck.enforce(modelNameIn, Types.STRING)
    nextModel = modelVerifier(modelNameIn, "text_to_text")
    if nextModel[1]:
        Configuration.setConfig("default_text_to_text_model", nextModel[0])


def modelScanner():
    Model.updateModelConfiguration()
    return
