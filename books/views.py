from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from books.models import Book
from books.serializers import BookSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                description="Filter by book title (ex. ?title=book)",
                required=False,
                type={"type": "string"},
            ),
            OpenApiParameter(
                name="author",
                description="Filter by book author(ex. ?author=name)",
                required=False,
                type={"type": "string"},
            ),
        ],
        description="Retrieve a list of all books with filtering by title and/or author",
    ),
    retrieve=extend_schema(
        description="Retrieve a specific book by id",
    ),
    create=extend_schema(
        description="Create a new book",
    ),
    update=extend_schema(
        description="Update an existing book",
    ),
    partial_update=extend_schema(
        description="Partially update an existing book",
    ),
    destroy=extend_schema(
        description="Delete a book",
    ),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Book.objects.all()
        title = self.request.query_params.get("title")
        author = self.request.query_params.get("author")

        if title:
            queryset = queryset.filter(title__icontains=title)
        if author:
            queryset = queryset.filter(author__icontains=author)

        return queryset
