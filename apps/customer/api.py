from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer


class CurrentUser(APIView):

    def get(self, *args, **kwargs):
        serializer = UserSerializer(self.request.user)
        return Response(serializer.data)