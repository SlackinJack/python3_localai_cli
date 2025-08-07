# modules.string


# output paths
OUTPUT_PATH = "output/"
AUDIO_FILE_PATH = OUTPUT_PATH + "audio/"
CONVERSATIONS_FILE_PATH = OUTPUT_PATH + "conversations/"
IMAGE_FILE_PATH = OUTPUT_PATH + "image/"
OTHER_FILE_PATH = OUTPUT_PATH + "other/"
MICROPHONE_FILE_NAME = "microphone_input_"
MICROPHONE_FILE_TRANSCRIPTION_NAME = "microphone_transcription_"
MICROPHONE_FILE_PATH = AUDIO_FILE_PATH + MICROPHONE_FILE_NAME


# configs paths
MODELS_CONFIG_FILE_NAME = "models.json"
CONFIGS_FILE_NAME = "config.json"
CONFIGS_PATH = "config/"
CONFIGS_ADVANCED_PATH = CONFIGS_PATH + "advanced/"
CONFIGS_READER_FILE_NAME = CONFIGS_ADVANCED_PATH + "config_reader.json"
CONFIGS_TRIGGER_FILE_NAME = CONFIGS_ADVANCED_PATH + "config_trigger.json"
CONFIGS_WEB_FILE_NAME = CONFIGS_ADVANCED_PATH + "config_web.json"


# test file paths
TESTS_FILE_PATH = [
    "tests/test.docx",
    "tests/test.pdf",
    "tests/test.png",
    "tests/test.pptx",
    "tests/test.txt",
    "tests/test.wav"
]
