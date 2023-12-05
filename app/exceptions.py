class PreparedException(Exception):
    message: str = None
    data: dict

    def __init__(self, **data):
        super().__init__(self.message)
        self.data = data


class WSHandlerException(PreparedException):
    pass


class WSHandlerUnknownEventException(WSHandlerException):
    message = 'Unknown event'


class WSHandlerDataNotValidException(WSHandlerException):
    message = 'Data is not valid'


class WSHandlerRecipientNotFoundException(WSHandlerException):
    message = 'Recipient not found'


class WSHandlerRecipientIsMeException(WSHandlerException):
    message = 'You cannot be the recipient'


class WSHandlerInvalidStatusException(WSHandlerException):
    message = 'Status does not exist'


class PermissionDenied(PreparedException):
    message = 'You cannot perform the operation'


class NotInWhitelist(PreparedException):
    message = 'Not allowed to play. Need to be in whitelist'


class SelectedDeckIsNotPlayable(PreparedException):
    message = 'Unplayable deck selected. Remove any ‘Coming soon’ cards &/or your deck must have 30 cards.'


class OpponentSelectedDeckIsNotPlayable(PreparedException):
    message = "The opponent's selected deck is not playable"


class CardAbilityNotFound(PreparedException):
    message = 'Card ability not found'
