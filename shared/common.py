import re
import decimal
import uuid
import time

import jsonpickle

##########
# Errors #
##########

class ErrorType():
    def __init__(self, returncode, err_message):
        self.returncode  = returncode
        self.err_message = err_message

class Errors():
    # NOTE: do not change the return code of these variables

    # DB Errors
    UNCAUGHT_EXCEPTION      = ErrorType(1, "The server encountered an internel error")
    DATA_NOT_PRESENT        = ErrorType(2, "The request was missing required data")
    CUSTOMER_DOES_NOT_EXIST = ErrorType(3, "The specified uuid is not linked to a customer")
    CUSTOMER_ALREADY_EXISTS = ErrorType(4, "The specified customer already exists")
    VOTES_DOES_NOT_EXIST    = ErrorType(5, "The specified uuid is not linked to a vote")
    VOTES_ALREADY_EXISTS    = ErrorType(6, "The specified vote already exists")
    INVALID_DATA_PRESENT    = ErrorType(7, "The request contained inconsistent or superfluous data")
    INVALID_TOKEN           = ErrorType(8, "The authentication token is not valid")
    PERMISSION_DENIED       = ErrorType(9, "You do not have the access rights for that resource")
    CONSISTENCY_ERROR       = ErrorType(10, "The request could not be completed due to a consistency issue")
    INVALID_EMAIL           = ErrorType(11, "The email address is invalid")
    INVALID_PHONE_NUMBER    = ErrorType(13, "The phone number is invalid")
    UNSUPORTED_VERSION      = ErrorType(14, "The specified version is no longer supported")
    STALE_API_VERSION       = ErrorType(15, "The API is not up to date with the latest version")

    # API Errors
    DATA_NOT_FOUND          = ErrorType(16, "The client cannot find your request")


def error_to_json(error):
    return jsonpickle.encode({
            "result": error.returncode,
            "error_message": error.err_message
        })

class PolitiHackException(Exception):
    def __init__(self, error_type, message=None, data=None):
        self.message = error_type.err_message if message is None else message
        self.error_type = error_type
        self.data = data
        Exception.__init__(self, self.message)

    def __str__(self):
        return type(self).__name__ + " - " + str(self.error_type.returncode) + " - " + self.message


############################
# Pickle/Unpickle Handlers #
############################

class BotoDecimalHandler(jsonpickle.handlers.BaseHandler):
    """
    Automatically convert Decimal types (returned by DynamoDB) to ints
    """
    def flatten(self, obj, data):
        data = int(obj)
        return data

jsonpickle.handlers.register(decimal.Decimal, BotoDecimalHandler)

##############
# Validators #
##############

EMAIL_REGEX = re.compile("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile("^\+?[0-9]{11}$")

def validate_email(email):
    if EMAIL_REGEX.match(email) is None:
        raise GatorException(Errors.INVALID_EMAIL, data={"email": email})

def validate_phonenumber(phonenumber):
    if PHONE_REGEX.match(phonenumber) is None:
        raise GatorException(Errors.INVALID_PHONE_NUMBER, data={"phone": phonenumber})

####################
# Helper Functions #
####################

def get_current_timestamp():
    return int(time.time() * 10**6)

def convert_query(cls, query):
    for item in query:
        yield cls(item)
