

class Context(object):
    def __init__(self, user_id: int, customer_id: int, shipment_id: int = None):
        self.user_id = user_id
        self.customer_id = customer_id
        self.shipment_id = shipment_id