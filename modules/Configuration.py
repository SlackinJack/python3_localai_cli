# modules.util


import json as JSON


import modules.file.Operation as Operation
import modules.Print as Print
import modules.string.Path as Path
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types


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
    "always_yes_to_yn":                     Types.BOOLEAN,
    "write_output_params":                  Types.BOOLEAN,
    "dump_text_color":                      Types.STRING,
    "debug_text_color":                     Types.STRING,

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

    # text_to_text
    "default_text_to_text_model":           Types.STRING,
    "system_prompt":                        Types.STRING,
    "print_delay":                          Types.FLOAT,
    "allow_setting_text_seeds":             Types.BOOLEAN,

    # text_to_image
    "default_text_to_image_model":          Types.STRING,
    "image_size":                           Types.STRING,
    "image_step":                           Types.INTEGER,
    "image_clipskip":                       Types.INTEGER,

    # image_to_text
    "default_image_to_text_model":          Types.STRING,
    "image_to_text_prompt":                 Types.STRING,

    # image_to_image
    "default_image_to_image_model":         Types.STRING,

    # image_to_video
    "default_image_to_video_model":         Types.STRING,
    "video_format":                         Types.STRING,

    # audio_to_text
    "default_audio_to_text_model":          Types.STRING,
    "audio_device":                         Types.STRING,
    "audio_device_subtype":                 Types.STRING,
    "live_transcription_delay":             Types.INTEGER,

    # text_to_audio
    "default_text_to_audio_model":          Types.STRING,
    "read_outputs":                         Types.BOOLEAN

}


def getConfig(keyIn):
    TypeCheck.check(keyIn, Types.STRING)
    return __configs[keyIn]


def setConfig(keyIn, settingIn):
    TypeCheck.check(keyIn, Types.STRING)
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
    TypeCheck.check(keyIn, Types.STRING)
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
                    if TypeCheck.check(v, __expected_config_types.get(k)):
                        setConfig(k, v)
                else:
                    Print.generic("\nIgnoring unrecognized configuration key/value pair: [" + k + "]: " + v)
                    continue
        if not getConfig("address").endswith("/v1"):
            newAddress = getConfig("address")
            if not newAddress.endswith("/"):
                newAddress += "/"
            setConfig("address", newAddress + "v1")
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
    TypeCheck.check(modelNameIn, Types.STRING)
    global __defaultModelName
    __defaultModelName = modelNameIn
    return


def resetDefaultTextModel():
    setConfig("default_text_to_text_model", __defaultModelName)
    return


def setConfigurationFileName(configurationFileNameIn):
    TypeCheck.check(configurationFileNameIn, Types.STRING)
    global __configurationFileName
    __configurationFileName = configurationFileNameIn
    return


def getConfigurationFileName():
    return __configurationFileName
