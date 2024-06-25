from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
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
        queryset = Borrowing.objects.all().select_related("book", "user")

        if user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user=user)
        else:
            queryset = queryset.filter(user=user)

        is_active = self.request.query_params.get("is_active")
        if is_active:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        if book.inventory < 1:
            raise ValidationError({"book": f"{book.title} is out of stock"})
        book.inventory -= 1
        book.save()

        serializer.save(user=self.request.user)
