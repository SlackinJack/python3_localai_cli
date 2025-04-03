# modules.command


import modules.Configuration as Configuration
import modules.Model as Model
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types
import modules.Print as Print
import modules.Util as Util


def __modelVerifier(nextModelIn, modelTypeIn):
    TypeCheck.check(nextModelIn, Types.STRING)
    TypeCheck.check(modelTypeIn, Types.STRING)
    result = Model.getModelByNameAndType(nextModelIn, modelTypeIn, True, False, False)
    return [result, (result is not None)]


def commandModel():
    def menu():
        choices = [
            "Change Models",
            "Scan Server for Models",
        ]

        selection = Util.printMenu("Model menu", "", choices)
        if selection is None:
            return
        elif selection == "Change Models":
            submenuChangeModel()
        elif selection == "Scan Server for Models":
            modelScanner()
        else:
            Print.error("\nInvalid selection.\n")
        menu()
        return
    menu()
    Print.generic("\nReturning to main menu.\n")
    return


def submenuChangeModel():
    choices = list(Model.getModelTypes().values())

    def menu():
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
                Print.error("\nInvalid selection.\n")
        menu()
        return
    menu()
    Print.generic("\nReturning to model menu.\n")
    return


def modelChanger(modelTypeIn, modelTypeNameIn):
    TypeCheck.check(modelTypeIn, Types.STRING)
    TypeCheck.check(modelTypeNameIn, Types.STRING)
    choices = list(Model.getModelsWithType(modelTypeIn))
    selection = Util.printMenu("Available models", "", choices)
    if selection is not None:
        if len(selection) > 0:
            matched = __modelVerifier(selection, modelTypeIn)
            if matched[1]:
                Configuration.setConfig("default_" + modelTypeIn + "_model", matched[0])
                Print.green("\n" + modelTypeNameIn + " model set to: " + matched[0] + "\n")
            else:
                Print.error(
                    "\nCannot find a match - keeping current " + modelTypeNameIn + " model:"
                    " " + Configuration.getConfig("default_" + modelTypeIn + "_model") + "\n"
                )
        else:
            Print.red("\nInvalid selection - returning to models menu.\n")
    else:
        Print.red("\nKeeping current model: " + Configuration.getConfig("default_" + modelTypeIn + "_model") + "\n")
    return


def modelScanner():
    Model.updateModelConfiguration()
    return
