from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from books.models import Book


class Borrowing(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} borrowed {self.book}: {self.borrow_date}"

    @property
    def is_active(self):
        return self.actual_return_date is None

    def clean(self):
        if self.expected_return_date < self.borrow_date:
            raise ValidationError(
                {
                    "expected_return_date": _(
                        "Expected return date cannot be earlier than borrowing date."
                    )
                }
            )

    def save(self, *args, **kwargs):
        if not self.borrow_date:
            self.borrow_date = date.today()
        self.clean()
        super().save(*args, **kwargs)
