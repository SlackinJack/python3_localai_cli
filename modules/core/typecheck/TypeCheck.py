# package modules.core.typecheck


import modules.core.typecheck.Types as Types


def check(obj1In, obj2In):
    return type(obj1In) is type(obj2In)


def enforce(obj1In, obj2In):
    if not check(obj1In, obj2In):
        assert False, "Input type " + str(type(obj1In)) + " is not the expected type " + str(type(obj2In))
    return True


def enforceList(obj1In, acceptableTypesIn):
    enforce(acceptableTypesIn, Types.LIST)
    for obj in acceptableTypesIn:
        if check(obj1In, obj):
            return True
    assert False, "Input type " + str(type(obj1In)) + " is not any of the expected types " + str(type(o) for o in acceptableTypesIn)
