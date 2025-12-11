DISABLED = "disabled"
ENABLED = "enabled"


def getCommandToggleString(toggleType, statusIn, descIn):
    return f"{toggleType} is now {statusIn} for {descIn}."
