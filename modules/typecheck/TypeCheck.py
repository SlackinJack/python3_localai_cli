# modules.typecheck


import modules.typecheck.Types as Types


def softcheck(obj1In, obj2In):
    return type(obj1In) is type(obj2In)


def check(obj1In, obj2In):
    if not softcheck(obj1In, obj2In):
        assert False, "Input type " + str(type(obj1In)) + " is not the expected type " + str(type(obj2In))
    return True


def checkList(obj1In, acceptableTypesIn):
    check(acceptableTypesIn, Types.LIST)
    for obj in acceptableTypesIn:
        if softcheck(obj1In, obj):
            return True
    assert False, "Input type " + str(type(obj1In)) + " is not any of the expected types " + str(type(o) for o in acceptableTypesIn)
