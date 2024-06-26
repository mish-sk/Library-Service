from datetime import date
from rest_framework import serializers

from books.serializers import BookSerializer
from borrowing.models import Borrowing
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "is_active",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book",
            "expected_return_date",
        ]

    def validate_expected_return_date(self, expected_return_date):
        if expected_return_date < date.today():
            raise serializers.ValidationError(
                "Expected return date cannot be earlier than borrowing date."
            )
        return expected_return_date
