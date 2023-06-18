

class Context(object):
    """
    General Context Class to pass relevant information easily between processes

    Purpose is to pass importmation like tenant, user, parameters and source of
    request from API to Services to Background Tasks and back.
    """

    def __init__(self, user_id: int = None, tenant_id: int = None):
        self.user_id = user_id
        self.tenant_id = tenant_id

    def set(self, key, val):
        setattr(self, key, val)
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)
