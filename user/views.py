from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer


@extend_schema_view(
    post=extend_schema(
        description="Register a new user with an email and password",
        responses={201: UserSerializer},
    ),
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


@extend_schema_view(
    get=extend_schema(
        description="Retrieve the authenticated user's details",
        responses={200: UserSerializer},
    ),
    put=extend_schema(
        description="Update the authenticated user's details",
        responses={200: UserSerializer},
    ),
    patch=extend_schema(
        description="Partially update the authenticated user's details",
        responses={200: UserSerializer},
    ),
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
