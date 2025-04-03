# modules.command


import os as OS


import modules.file.Operation as Operation
import modules.string.Path as Path
import modules.Configuration as Configuration
import modules.Print as Print
import modules.Util as Util


def commandExit():
    for conversation in OS.listdir(Path.CONVERSATIONS_FILE_PATH):
        if conversation.endswith(".convo"):
            if Util.checkEmptyString(Operation.readFile(Path.CONVERSATIONS_FILE_PATH + conversation, None, False)):
                Operation.deleteFile(Path.CONVERSATIONS_FILE_PATH + conversation)
                Util.printDebug("\nDeleted empty conversation file: " + conversation)

    if Configuration.getConfig("delete_output_files_exit"):
        foldersToClean = [Path.AUDIO_FILE_PATH, Path.IMAGE_FILE_PATH]
        for folder in foldersToClean:
            for outputFile in OS.listdir(folder):
                if not outputFile == ".keep":
                    Operation.deleteFile(folder + outputFile)
                    Util.printDebug("\nDeleted output file: " + folder + outputFile)

    Print.generic("")
    return
