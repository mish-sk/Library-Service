from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from books.models import Book
from books.serializers import BookSerializer


class BookTests(APITestCase):

    def setUp(self):
        self.book1 = Book.objects.create(
            title="Book one",
            author="Author One",
            cover="Hard",
            inventory=5,
            daily_fee=1.50,
        )
        self.book2 = Book.objects.create(
            title="Book two",
            author="Author Two",
            cover="Soft",
            inventory=3,
            daily_fee=2.00,
        )
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="admin1234pass"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

    def test_get_books(self):
        url = reverse("books:book-list")
        response = self.client.get(url, format="json")
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_book(self):
        url = reverse("books:book-list")
        data = {
            "title": "New book",
            "author": "New Author",
            "cover": "Soft",
            "inventory": 10,
            "daily_fee": 1.75,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)
        self.assertEqual(Book.objects.get(id=response.data["id"]).title, "New book")

    def test_get_single_book(self):
        url = reverse("books:book-detail", kwargs={"pk": self.book1.pk})
        response = self.client.get(url, format="json")
        book = Book.objects.get(pk=self.book1.pk)
        serializer = BookSerializer(book)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_book(self):
        url = reverse("books:book-detail", kwargs={"pk": self.book1.pk})
        data = {
            "title": "Updated book",
            "author": "Updated Author",
            "cover": "Hard",
            "inventory": 5,
            "daily_fee": 1.50,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, "Updated book")

    def test_partial_update_book(self):
        url = reverse("books:book-detail", kwargs={"pk": self.book1.pk})
        data = {"title": "Partially updated book"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, "Partially updated book")

    def test_delete_book(self):
        url = reverse("books:book-detail", kwargs={"pk": self.book1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 1)

    def test_filter_books_by_title(self):
        url = reverse("books:book-list")
        response = self.client.get(url, {"title": "Book One"}, format="json")
        books = Book.objects.filter(title__icontains="Book One")
        serializer = BookSerializer(books, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_books_by_author(self):
        url = reverse("books:book-list")
        response = self.client.get(url, {"author": "Author Two"}, format="json")
        books = Book.objects.filter(author__icontains="Author Two")
        serializer = BookSerializer(books, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
