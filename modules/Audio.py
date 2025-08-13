# package modules


import pydub as PyDub
import queue as Queue
import sounddevice as SoundDevice
import soundfile as SoundFile
import threading as Threading
import time as Time


import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.string.Path as Path


def getMicrophoneInput(timerIn):
    TypeCheck.check(timerIn, Types.INTEGER)

    Util.setShouldInterruptCurrentOutputProcess(False)
    filePath = Path.MICROPHONE_FILE_PATH + Util.getDateTimeString() + ".wav"
    if timerIn <= 0:
        Print.green("\nUse [" + Util.getKeybindStopName() + "] to exit and save recording.\n")

    while True:
        try:
            if not Util.getShouldInterruptCurrentOutputProcess():
                recordAudioToFile(filePath, timerIn)
                if timerIn > 0:
                    Print.generic("\nStopping recording")
                    return filePath
            else:
                Print.green("\nRecording finished.")
                return filePath
        except:
            Print.generic("\nStopping recording")
            return filePath


def recordAudioToFile(filePathIn, timerIn):
    TypeCheck.check(filePathIn, Types.STRING)
    TypeCheck.check(timerIn, Types.INTEGER)

    q = Queue.Queue()
    stopWorker = False
    device = Configuration.getConfig("audio_device")
    channels = 1
    subtype = Configuration.getConfig("audio_device_subtype")
    samplerate = int(SoundDevice.query_devices(device, "input")["default_samplerate"])

    def callback(indata, frames, time, status):
        q.put(indata.copy())

    with SoundFile.SoundFile(filePathIn, mode="x", samplerate=samplerate, channels=channels, subtype=subtype) as file:
        with SoundDevice.InputStream(samplerate=samplerate, device=device, channels=channels, callback=callback):
            if timerIn <= 0:
                while True:
                    file.write(q.get())
                    if Util.getShouldInterruptCurrentOutputProcess():
                        return
            else:
                def timer(workerThreadIn):
                    nonlocal stopWorker
                    Time.sleep(timerIn)
                    stopWorker = True
                    workerThreadIn.join()

                def worker():
                    nonlocal stopWorker
                    while True:
                        file.write(q.get())
                        if stopWorker:
                            return

                stopWorker = False
                workerThread = Threading.Thread(target=worker)
                workerThread.start()
                timerThread = Threading.Thread(target=timer, args=(workerThread,))
                timerThread.start()
                timerThread.join()

    return


def combineAudio(path1, path2):
    TypeCheck.check(path1, Types.STRING)
    TypeCheck.check(path2, Types.STRING)
    combined_sounds = PyDub.AudioSegment.from_wav(path1)[-500:] + PyDub.AudioSegment.from_wav(path2)
    combinedPath = Path.MICROPHONE_FILE_PATH + "combined_" + Util.getDateTimeString() + ".wav"
    combined_sounds.export(combinedPath, format="wav")
    return combinedPath
