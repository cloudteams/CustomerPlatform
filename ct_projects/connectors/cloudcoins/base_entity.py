"""
Generic CloudCoins API Entity
"""


class CloudCoinsApiEntity(object):

    def __init__(self, resp):
        payload = resp['payload']

        for key in payload:
            if type(payload[key]) == dict:
                val = CloudCoinsApiEntity({
                    'payload': payload[key]
                })
            else:
                val = payload[key]

            setattr(self, key, val)

