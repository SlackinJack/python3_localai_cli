# modules.command


import modules.command.CommandMap as CommandMap
import modules.Configuration as Configuration
import modules.Print as Print
import modules.PromptHandler as PromptHandler
import modules.Trigger as Trigger
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types
import modules.Util as Util


def checkPromptForCommandsAndTriggers(promptIn, disableSeed=False):
    TypeCheck.check(promptIn, Types.STRING)
    if Util.checkStringHasCommand(promptIn):
        for func, value in CommandMap.getCommandMap().items():
            if promptIn == value[0]:
                func()
                return
        Print.error("\nUnknown command.\n")
        return
    else:
        Util.printDebug("\nNo commands detected.")
        if Configuration.getConfig("allow_setting_text_seeds") and not disableSeed:
            Print.generic("")
            seed = Util.setOrPresetValue(
                "Enter a seed (eg. 1234567890)",
                Util.getRandomSeed(),
                Util.intVerifier,
                "random",
                "Using a random seed",
                "The seed you entered is invalid - using a random seed!"
            )
        else:
            Util.printDebug("\nUsing random text seed.")
            seed = Util.getRandomSeed()
        promptWithData = Trigger.checkTriggers(promptIn)
        Util.startTimer(0)
        PromptHandler.handlePrompt(promptWithData, seed)
        Util.endTimer(0)
    return
