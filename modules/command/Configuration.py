# modules.command


import os as OS


import modules.Configuration as Configuration
import modules.file.Reader as Reader
import modules.Model as Model
import modules.Print as Print
import modules.string.Path as Path
import modules.string.Prompt as Prompt
import modules.Util as Util


def commandConfiguration():
    choices = [
        "Load",
        "Reload"
    ]

    def menu():
        selection = Util.printMenu("Configuration menu", "", choices)
        if selection is None:
            return
        elif selection == "Load":
            subcommandConfigurationLoad()
        elif selection == "Reload":
            subcommandConfigurationReload()
        else:
            Print.error("\nInvalid selection.\n")
        menu()
        return
    menu()
    Print.generic("\nReturning to main menu.\n")
    return


def subcommandConfigurationLoad():
    configList = []

    for config in OS.listdir(Path.CONFIGS_PATH):
        if config != "models.json" and config.endswith(".json"):
            configList.append(config)

    choices = configList

    def verifier(configNameIn):
        if len(configNameIn) > 0:
            bestMatch = None
            configNameIn = configNameIn.lower()
            for config in configList:
                if configNameIn.lower() == config.lower():
                    return [config, True]
                elif configNameIn in config.lower():
                    if bestMatch is not None:
                        nextCandidate = Util.getStringMatchPercentage(configNameIn, config.lower())
                        currentCandidate = Util.getStringMatchPercentage(bestMatch.lower(), config.lower())
                        if nextCandidate > currentCandidate:
                            bestMatch = config
                    else:
                        bestMatch = config
            if bestMatch is not None:
                return [bestMatch, True]
        return ["", False]

    selection = Util.printMenu("Configurations available", "", choices)
    if selection is not None:
        if len(selection) > 0:
            nextConfiguration = verifier(selection)
            if nextConfiguration[1]:
                Configuration.setConfigurationFileName(nextConfiguration[0])
                Print.green("\nConfiguration set to " + nextConfiguration[0] + "\n")
                commandLoadModelConfiguration()
                commandLoadConfiguration()
            else:
                Print.error("\nCannot find configuration - returning to configuration menu.\n")
        else:
            Print.error("\nInvalid selection - returning to configuration menu.\n")
    else:
        Print.red("\nReturning to configuration menu.\n")
    return None


def subcommandConfigurationReload():
    commandLoadModelConfiguration()
    commandLoadConfiguration()
    Print.green("\nConfiguration reloaded.\n")
    return


def commandLoadConfiguration():
    Configuration.loadConfiguration()
    Prompt.loadConfiguration()
    Reader.loadConfiguration()

    for modelType in list(Model.getModelTypes()):
        Configuration.setConfig(
            "default_" + modelType + "_model",
            Model.getModelFromConfiguration(Configuration.getConfig("default_" + modelType + "_model"), modelType, False)
        )

    Configuration.setDefaultTextModel(Configuration.getConfig("default_text_to_text_model"))
    return


def commandLoadModelConfiguration():
    Configuration.loadModelConfiguration()
    return
