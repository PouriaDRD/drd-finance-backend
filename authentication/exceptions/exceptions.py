class InvalidOTPError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class WrongEmailOrPasswordError(Exception):
    pass


class OTPExistsError(Exception):
    pass
