# package modules


import modules.connection.request.Request as Request
import modules.core.file.Operation as Operation
import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.string.Path as Path


__modelTypes = {
    "audio_to_text": "Audio-to-Text",
    "image_to_image": "Image-to-Image",
    "image_to_text": "Image-to-Text",
    "image_to_video": "Image-to-Video",
    "text_to_audio": "Text-to-Audio",
    "text_to_image": "Text-to-Image",
    "text_to_text": "Text-to-Text",
}


def getModelTypes():
    return __modelTypes


def getModelByName(modelNameIn):
    TypeCheck.enforce(modelNameIn, Types.STRING)
    modelNameIn = modelNameIn.lower()
    for model, data in Configuration.getModelConfigAll().items():
        m = model.lower()
        if modelNameIn == m:
            return model
    return None


def getModelByNameAndType(modelNameIn, modelTypeIn, modelOnly, strictMatching, silent):
    TypeCheck.enforce(modelNameIn, Types.STRING)
    TypeCheck.enforce(modelTypeIn, Types.STRING)
    TypeCheck.enforce(modelOnly, Types.BOOLEAN)
    TypeCheck.enforce(strictMatching, Types.BOOLEAN)
    TypeCheck.enforce(silent, Types.BOOLEAN)

    modelNameIn = modelNameIn.lower()
    outModel = ""
    outModelData = None
    modelNames = None
    if " " in modelNameIn:
        modelNames = modelNameIn.split(" ")
    # L1
    for model, data in Configuration.getModelConfigAll().items():
        if data["model_type"].lower() == modelTypeIn:
            m = model.lower()
            if strictMatching:
                if modelNameIn == m:
                    outModel = model
                    outModelData = data
                    break  # L1
            else:
                if modelNames is not None:
                    matchesNames = True
                    for part in modelNames:  # L2
                        if part not in m:
                            matchesNames = False
                            break  # L2
                    if matchesNames and (len(outModel) == 0 or (Util.getStringMatchPercentage(m, modelNameIn) > Util.getStringMatchPercentage(m, list(outModel)[0]))):
                        outModel = model
                        outModelData = data
                elif modelNameIn in m or m in modelNameIn:
                    if len(outModel) == 0 or (Util.getStringMatchPercentage(m, modelNameIn) > Util.getStringMatchPercentage(m, list(outModel)[0])):
                        outModel = model
                        outModelData = data
    if len(outModel) > 0:
        if modelOnly:
            return outModel
        else:
            return {outModel: outModelData}
    else:
        if not silent:
            Util.printError("\nNo model found with name: " + modelNameIn)


def getModelsWithType(modelTypeIn):
    TypeCheck.enforce(modelTypeIn, Types.STRING)
    out = {}
    for model, data in Configuration.getModelConfigAll().items():
        if data["model_type"].lower() == modelTypeIn:
            out[model] = data
    return out


def getSwitchableTextModels():
    out = []
    for model, data in getModelsWithType("text_to_text").items():
        if data["switchable"] and len(data["description"]) > 0:
            out.append(model)
    return out


def getSwitchableTextModelDescriptions():
    out = ""
    for model, data in getModelsWithType("text_to_text").items():
        if data["switchable"] and len(data["description"]) > 0:
            if len(out) > 0:
                out += " "
            out += data["description"]
    return out


def getChatModelFormat(modelNameIn):
    TypeCheck.enforce(modelNameIn, Types.STRING)
    formatting = getModelDataIfExists("format", modelNameIn)
    if formatting is None:
        return "default"
    else:
        return formatting


def getChatModelPromptOverride(modelNameIn):
    TypeCheck.enforce(modelNameIn, Types.STRING)
    return getModelDataIfExists("prompt", modelNameIn)


def getModelDataIfExists(dataNameIn, modelNameIn):
    TypeCheck.enforce(dataNameIn, Types.STRING)
    TypeCheck.enforce(modelNameIn, Types.STRING)
    modelNameIn = modelNameIn.lower()
    for model, data in Configuration.getModelConfigAll().items():
        if modelNameIn == model.lower():
            if data.get(dataNameIn) is not None and not Util.checkEmptyString(data[dataNameIn]):
                return data[dataNameIn]
            break
    return None


def getModelFromConfiguration(modelToGet, modelType, writeAsCaps):
    TypeCheck.enforce(modelToGet, Types.STRING)
    TypeCheck.enforce(modelType, Types.STRING)
    TypeCheck.enforce(writeAsCaps, Types.BOOLEAN)
    model = getModelByNameAndType(modelToGet, modelType, True, False, False)
    if model is None:
        model = getModelByNameAndType("", modelType, True, False, False)
        if writeAsCaps:
            modelType = modelType.upper()
        if "_" in modelType:
            modelType = modelType.replace("_", " ")
        if model is not None:
            Util.printError("\nConfiguration-specified " + modelType + " model not found - using " + model + ".")
        else:
            Util.printError("\nCannot find a(n) " + modelType + " model - configure a model in order to use this functionality.")
    return model


def updateModelConfiguration():
    if not Configuration.getConfig("disable_all_file_delete_functions"):
        modelList = Request.getModelsFromServer()
        if modelList is not None:
            addModels = {}
            for model in modelList:
                matchedIgnored = False
                for ignored in Configuration.getConfig("model_scanner_ignored_filenames"):
                    if ignored in model["id"]:
                        matchedIgnored = True
                        break
                if not matchedIgnored and not model["id"] in Configuration.getModelConfigAll():
                    Util.printDebug(model["id"] + " is missing from model config")
                    addModels[model["id"]] = {"model_type": "unknown"}
            Util.printDebug("")

            newModelsJson = Configuration.getModelConfigAll() | addModels
            outputFileString = Util.formatJSONToString(newModelsJson)
            outputFileString = Util.cleanupString(outputFileString)

            Util.printDump("\nNew models.json:\n" + outputFileString)

            Operation.deleteFile(Path.CONFIGS_PATH + Path.MODELS_CONFIG_FILE_NAME, Configuration.getConfig("disable_all_file_delete_functions"))
            Operation.appendFile(Path.CONFIGS_PATH + Path.MODELS_CONFIG_FILE_NAME, outputFileString)
            Configuration.loadModelConfiguration()

            Print.green("\nSuccessfully updated your models.json!\n")
        else:
            Util.printError("\nCould not update your models.json - check your connection?\n")
    else:
        Print.red("\nYou have disabled 'disable_all_file_delete_functions'.")
        Print.red("This configuration must be disabled in order to update your model configuration.")
        Print.red("Not updating model list.\n")
    return


def getServerHasImageModels(searchModelIn):
    TypeCheck.enforce(searchModelIn, Types.STRING)
    modelList = Request.getModelsFromServer()
    if modelList is None:
        return None
    result = []
    for model in modelList:
        if searchModelIn.lower() in model["id"].lower():
            result.append(model["id"])
    return result
