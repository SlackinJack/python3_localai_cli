# package modules.core


import json as JSON
import os as OS


import modules.core.file.Operation as Operation
import modules.core.Print as Print
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.string.Path as Path


__configs = {}          # main configuration
__modelConfigs = {}     # model configuration
__configurationFileName = Path.CONFIGS_FILE_NAME
__defaultModelName = ""
__expected_config_types = {

    # main
    "address":                              Types.STRING,
    "location":                             Types.STRING,
    "debug_level":                          Types.INTEGER,
    "clear_window_before_every_prompt":     Types.BOOLEAN,
    "delete_output_files_exit":             Types.BOOLEAN,
    "automatically_open_files":             Types.BOOLEAN,
    "output_folder":                        Types.STRING,
    "always_yes_to_yn":                     Types.BOOLEAN,
    "write_output_params":                  Types.BOOLEAN,
    "dump_text_color":                      Types.STRING,
    "debug_text_color":                     Types.STRING,
    "unicode_only":                         Types.BOOLEAN,   
    "disable_all_file_delete_functions":    Types.BOOLEAN,
    "no_negative_prompts":                  Types.BOOLEAN,         

    # model
    "model_scanner_ignored_filenames":      Types.LIST,

    # behavioural
    "enable_functions":                     Types.BOOLEAN,
    "enable_internet":                      Types.BOOLEAN,
    "enable_automatic_model_switching":     Types.BOOLEAN,
    "enable_chat_history_consideration":    Types.BOOLEAN,
    "max_sources_per_search":               Types.INTEGER,
    "max_sentences_per_source":             Types.INTEGER,
    "enable_source_condensing":             Types.BOOLEAN,
    "enable_determine_source_relevance":    Types.BOOLEAN,

    # text_to_text
    "default_text_to_text_model":           Types.STRING,
    "system_prompt":                        Types.STRING,
    "print_delay":                          Types.FLOAT,
    "allow_setting_text_seeds":             Types.BOOLEAN,
    "do_reprompts":                         Types.BOOLEAN,
    "reprompt_with_history":                Types.BOOLEAN,
    "line_break_punctuations":              Types.LIST,
    "line_break_threshold":                 Types.INTEGER,

    # text_to_image
    "default_text_to_image_model":          Types.STRING,
    "image_size":                           Types.STRING,
    "image_step":                           Types.INTEGER,
    "image_clipskip":                       Types.INTEGER,

    # image_to_text
    "default_image_to_text_model":          Types.STRING,

    # image_to_image
    "default_image_to_image_model":         Types.STRING,

    # image_to_video
    "default_image_to_video_model":         Types.STRING,

    # audio_to_text
    "default_audio_to_text_model":          Types.STRING,
    "audio_device":                         Types.STRING,
    "audio_device_subtype":                 Types.STRING,
    "live_transcription_delay":             Types.INTEGER,
    "live_transcription_to_file":           Types.BOOLEAN,

    # text_to_audio
    "default_text_to_audio_model":          Types.STRING,
    "read_outputs":                         Types.BOOLEAN

}


def getConfig(keyIn):
    TypeCheck.enforce(keyIn, Types.STRING)
    global __configs
    if len(__configs) == 0:
        loadConfiguration()
    return __configs[keyIn]


def setConfig(keyIn, settingIn):
    TypeCheck.enforce(keyIn, Types.STRING)
    global __configs
    __configs[keyIn] = settingIn
    return


def resetConfig():
    global __configs
    __configs = {}
    return


def getModelConfigAll():
    return __modelConfigs


def setModelConfig(keyIn, settingIn):
    TypeCheck.enforce(keyIn, Types.STRING)
    # settingIn is unchecked
    global __modelConfigs
    __modelConfigs[keyIn] = settingIn
    return


def resetModelConfig():
    global __modelConfigs
    __modelConfigs = {}
    return


def loadConfiguration():
    resetConfig()
    configFile = Operation.readFile(Path.CONFIGS_PATH + __configurationFileName, None, False)
    if configFile is not None:
        newConfig = JSON.loads(configFile)
        for k, v in newConfig.items():
            if not k.endswith("_desc") and not k.endswith("_section"):
                if __expected_config_types.get(k, None) is not None:
                    if TypeCheck.enforce(v, __expected_config_types.get(k)):
                        setConfig(k, v)
                else:
                    Print.generic("\nIgnoring unrecognized configuration key/value pair: [" + k + "]: " + str(v))
                    continue
        if not getConfig("address").endswith("/v1"):
            newAddress = getConfig("address")
            if not newAddress.endswith("/"):
                newAddress += "/"
            setConfig("address", newAddress + "v1")
        if len(getConfig("output_folder")) > 0:
            outputFolder = getConfig("output_folder")
            if not outputFolder.endswith("/"):
                outputFolder += "/"
            if not Operation.folderExists(outputFolder):
                OS.mkdir(outputFolder)
            for f in Path.OUTPUT_FOLDERS:
                if not Operation.folderExists(outputFolder + f):
                    OS.mkdir(outputFolder + f)
            Path.setOutputPath(outputFolder)
    return


def loadModelConfiguration():
    resetModelConfig()
    modelConfigFile = Operation.readFile(Path.CONFIGS_PATH + Path.MODELS_CONFIG_FILE_NAME, None, False)
    if modelConfigFile is not None:
        newModelConfig = JSON.loads(modelConfigFile)
        for k, v in newModelConfig.items():
            setModelConfig(k, v)
    return


def setDefaultTextModel(modelNameIn):
    TypeCheck.enforce(modelNameIn, Types.STRING)
    global __defaultModelName
    __defaultModelName = modelNameIn
    return


def resetDefaultTextModel():
    setConfig("default_text_to_text_model", __defaultModelName)
    return


def setConfigurationFileName(configurationFileNameIn):
    TypeCheck.enforce(configurationFileNameIn, Types.STRING)
    global __configurationFileName
    __configurationFileName = configurationFileNameIn
    return


def getConfigurationFileName():
    return __configurationFileName
