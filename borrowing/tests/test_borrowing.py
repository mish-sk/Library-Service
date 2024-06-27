from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase, APIClient
from books.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer
from datetime import date


class BorrowingTests(APITestCase):

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

        user = get_user_model()
        self.admin_user = user.objects.create_superuser(
            email="admin@admin.com", password="admin1234pass"
        )
        self.regular_user = user.objects.create_user(
            email="user@user.com", password="user1234pass"
        )

        self.borrowing1 = Borrowing.objects.create(
            user=self.regular_user,
            book=self.book1,
            expected_return_date=date(2024, 12, 31),
        )
        self.borrowing2 = Borrowing.objects.create(
            user=self.regular_user,
            book=self.book2,
            expected_return_date=date(2024, 12, 31),
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

    def test_list_borrowings(self):
        url = reverse("borrowing:borrowing-list")
        response = self.client.get(url, format="json")
        borrowings = Borrowing.objects.all()
        serializer = BorrowingSerializer(borrowings, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_borrowing(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("borrowing:borrowing-list")
        data = {"book": self.book1.id, "expected_return_date": "2024-12-31"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 3)
        self.assertEqual(Borrowing.objects.get(id=response.data["id"]).book, self.book1)

    def test_get_single_borrowing(self):
        url = reverse("borrowing:borrowing-detail", kwargs={"pk": self.borrowing1.pk})
        response = self.client.get(url, format="json")
        borrowing = Borrowing.objects.get(pk=self.borrowing1.pk)
        serializer = BorrowingSerializer(borrowing)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_borrowing(self):
        url = reverse("borrowing:borrowing-detail", kwargs={"pk": self.borrowing1.pk})
        data = {"book": self.book1.id, "expected_return_date": "2024-12-30"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.borrowing1.refresh_from_db()
        self.assertEqual(self.borrowing1.expected_return_date, date(2024, 12, 30))

    def test_partial_update_borrowing(self):
        url = reverse("borrowing:borrowing-detail", kwargs={"pk": self.borrowing1.pk})
        data = {"expected_return_date": "2024-12-29"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.borrowing1.refresh_from_db()
        self.assertEqual(self.borrowing1.expected_return_date, date(2024, 12, 29))

    def test_delete_borrowing(self):
        url = reverse("borrowing:borrowing-detail", kwargs={"pk": self.borrowing1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Borrowing.objects.count(), 1)

    def test_return_borrowing(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("borrowing:borrowing-return", kwargs={"pk": self.borrowing1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.borrowing1.refresh_from_db()
        self.assertIsNotNone(self.borrowing1.actual_return_date)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.inventory, 6)

    def test_create_borrowing_out_of_stock(self):
        self.client.force_authenticate(user=self.regular_user)
        self.book1.inventory = 0
        self.book1.save()
        url = reverse("borrowing:borrowing-list")
        data = {"book": self.book1.id, "expected_return_date": "2024-12-31"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_error = {
            "book": ErrorDetail(string="Book one is out of stock", code="invalid")
        }
        self.assertEqual(response.data, expected_error)
