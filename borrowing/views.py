from datetime import date

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingCreateSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type={"type": "string"},
                description="Filter by active status (ex. ?is_active=true/false)",
                required=False,
            ),
            OpenApiParameter(
                "user_id",
                type={"type": "string"},
                description="Filter by user id (ex. ?user_id=1)",
                required=False,
            ),
        ],
        description="Retrieve a list of all borrowings",
    ),
    retrieve=extend_schema(description="Retrieve a borrowing by id"),
    create=extend_schema(description="Create a new borrowing"),
    update=extend_schema(description="Update an existing borrowing"),
    partial_update=extend_schema(description="Partially update an existing borrowing"),
    destroy=extend_schema(description="Delete a borrowing"),
)
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
                queryset = queryset.filter(user_id=user_id)
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

    @extend_schema(
        responses={200: "Book returned successfully."},
        description="Return a borrowed book",
    )
    @action(detail=True, methods=["post"], url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()

        if not borrowing.is_active:
            return Response(
                {"error": "The book has already been returned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        book = borrowing.book
        book.inventory += 1
        book.save()

        borrowing.actual_return_date = date.today()
        borrowing.save()

        return Response(
            {"message": "Book returned successfully"}, status=status.HTTP_200_OK
        )
