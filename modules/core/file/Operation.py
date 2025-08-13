# package modules.core.file


import glob as Glob
import os as OS
import pathlib as PathLib
import urllib as URLLib


import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.string.Path as Path


def fileExists(fileNameIn):
    TypeCheck.check(fileNameIn, Types.STRING)
    return PathLib.Path(fileNameIn).is_file()


def folderExists(folderNameIn):
    TypeCheck.check(folderNameIn, Types.STRING)
    return PathLib.Path(folderNameIn).is_dir()


def readFile(fileNameIn, splitter, writeIfNonexistent):
    TypeCheck.check(fileNameIn, Types.STRING)
    TypeCheck.checkList(splitter, [Types.STRING, Types.NONE])
    TypeCheck.check(writeIfNonexistent, Types.BOOLEAN)

    if not fileExists(fileNameIn) and not folderExists(fileNameIn):
        if writeIfNonexistent:
            writeFile(fileNameIn)
        else:
            return None
    with open(fileNameIn, "r") as f:
        theFile = f.read()
    if splitter is not None:
        theFile = theFile.split(splitter)
    return theFile


def readFileBinary(fileNameIn):
    TypeCheck.check(fileNameIn, Types.STRING)
    theFile = None
    if fileExists(fileNameIn):
        with open(fileNameIn, "rb") as f:
            theFile = f.read()
    return theFile


def writeFile(fileNameIn):
    TypeCheck.check(fileNameIn, Types.STRING)
    if not fileExists(fileNameIn):
        open(fileNameIn, "w").close()
    return


def writeFileBinary(fileNameIn, dataIn):
    TypeCheck.check(fileNameIn, Types.STRING)
    TypeCheck.check(dataIn, Types.BYTE)
    if not fileExists(fileNameIn):
        with open(fileNameIn, "wb") as f:
            f.write(dataIn)
    return


def appendFile(fileNameIn, dataIn):
    TypeCheck.check(fileNameIn, Types.STRING)
    TypeCheck.check(dataIn, Types.STRING)
    if not fileExists(fileNameIn):
        writeFile(fileNameIn)
    with open(fileNameIn, "a") as f:
        f.write(dataIn)
    return


def deleteFile(fileNameIn, disableDeleteFunctions):
    TypeCheck.check(fileNameIn, Types.STRING)
    TypeCheck.check(disableDeleteFunctions, Types.BOOLEAN)
    if not disableDeleteFunctions:
        if fileExists(fileNameIn):
            OS.remove(fileNameIn)
    return


def deleteFilesWithPrefix(filePathIn, fileNamePrefixIn, disableDeleteFunctions):
    TypeCheck.check(filePathIn, Types.STRING)
    TypeCheck.check(fileNamePrefixIn, Types.STRING)
    Typecheck.check(disableDeleteFunctions, Types.BOOLEAN)
    if not disableDeleteFunctions:
        files = OS.listdir(filePathIn)
        for f in files:
            if f.startswith(fileNamePrefixIn):
                OS.remove(filePathIn + f)
    return


def getFileFromURL(urlIn, folderIn):
    TypeCheck.check(urlIn, Types.STRING)
    TypeCheck.check(folderIn, Types.STRING)
    if len(urlIn) > 0:
        split = urlIn.split("/")
        fileName = split[len(split) - 1]
        fileName = Path.OUTPUT_PATH + folderIn + "/" + fileName
        try:
            URLLib.request.urlretrieve(urlIn, fileName)
            return fileName
        except Exception as e:
            Util.printError(f'\nCould not fetch file from: {urlIn}\n')
            Util.printError(str(e))
    return None


def getPathTree(pathIn):
    TypeCheck.check(pathIn, Types.STRING)
    fileTree = []
    for fileName in Glob.glob(pathIn + "/**", recursive=True):
        if not folderExists(fileName) and fileExists(fileName):
            fileTree.append(fileName)
    return fileTree
