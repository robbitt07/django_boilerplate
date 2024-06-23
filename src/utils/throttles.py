from rest_framework.throttling import UserRateThrottle

from time import time


class EventRateThrottle(UserRateThrottle):
    rate = 2500
    duration = 86400

    def __init__(self):
        pass

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            user_key = request.user.pk
            day_ley = int(time() // 86400)
            return f"throttle_event:{day_ley}:{user_key}"

    def allow_request(self, request, view):
        """
        Implement the check to see if the request should be throttled.
        On success calls `throttle_success`.
        On failure calls `throttle_failure`.
        """
        if self.rate is None:
            return True

        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, {})
        self.history_count = self.history.get("count", 0)
        request.history_count = self.history_count
        
        # Set Headers
        if self.history_count > self.rate:
            return self.throttle_failure()
        return self.throttle_success()

    def throttle_success(self):
        """
        Inserts the current request"s timestamp along with the key
        into the cache.
        """
        self.history.update({"count": self.history.get("count", 0) + 1})
        self.cache.set(self.key, self.history, self.duration)
        return True

    def throttle_failure(self):
        """
        Called when a request to the API has failed due to throttling.
        """
        return False