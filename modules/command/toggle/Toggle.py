# package modules.command.toggle


import modules.core.Print as Print
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types


def getMessage(leading, settingIn, ending):
    TypeCheck.enforce(leading, Types.STRING)
    TypeCheck.enforce(settingIn, Types.BOOLEAN)
    TypeCheck.enforce(ending, Types.STRING)
    func = Print.green if settingIn else Print.red
    s = "enabled" if settingIn else "disabled"
    yield from func(leading + s + ending)
