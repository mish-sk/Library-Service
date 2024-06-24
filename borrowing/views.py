from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingCreateSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BorrowingSerializer
        return BorrowingCreateSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Borrowing.objects.all()
        return Borrowing.objects.filter(user_id=user.id)
