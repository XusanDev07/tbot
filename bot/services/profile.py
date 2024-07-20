from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from bot.models.auth import User
from bot.serializers import UserSerializer


class ProfileAPIView(GenericAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        tg_user_id = self.kwargs.get('tg_user_id')
        if tg_user_id is None:
            return User.objects.none()
        return User.objects.filter(tg_user_id=tg_user_id)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset.first())
            return Response(serializer.data)
        return Response({"detail": "User not found"}, status=404)
