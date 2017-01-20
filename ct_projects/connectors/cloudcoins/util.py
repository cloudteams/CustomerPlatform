"""
Defines CloudCoins API exception types & util functions
"""


class CloudCoinsRequestException(Exception):
    pass


class CloudCoinsCustomerError(CloudCoinsRequestException):
    pass


class CloudCoinsProjectManagerError(CloudCoinsRequestException):
    pass


class CloudCoinsProjectError(CloudCoinsRequestException):
    pass


class CloudCoinsCampaignError(CloudCoinsRequestException):
    pass


class CloudCoinsAnswerAlreadyExistsError(CloudCoinsCampaignError):
    pass


class CloudCoinsCommissionError(CloudCoinsRequestException):
    pass


def timeformat(t):
    # DD-MM-YYYY HH:MM
    return t.strftime('%d-%m-%Y %H:%M')
