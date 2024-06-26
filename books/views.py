from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from books.models import Book
from books.serializers import BookSerializer


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
