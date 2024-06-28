from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token_obtain_pair")
ME_URL = reverse("user:manage")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class UserApiTests(APITestCase):

    def test_create_user_success(self):
        payload = {
            "email": "user@user.com",
            "password": "user1234pass",
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", response.data)

    def test_create_user_with_existing_email_fails(self):
        payload = {
            "email": "user@user.com",
            "password": "user1234pass",
        }
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        payload = {
            "email": "user@user.com",
            "password": "user1234pass",
        }
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        create_user(email="user@user.com", password="user1234pass")
        payload = {
            "email": "user@user.com",
            "password": "wrong",
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_unauthorized(self):
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_profile_success(self):
        user = create_user(email="user@user.com", password="user1234pass")
        self.client.force_authenticate(user=user)

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": user.id,
                "email": user.email,
                "is_staff": user.is_staff,
            },
        )

    def test_post_me_not_allowed(self):
        user = create_user(email="user@user.com", password="user1234pass")
        self.client.force_authenticate(user=user)
        response = self.client.post(ME_URL, {})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        user = create_user(email="user@user.com", password="user1234pass")
        self.client.force_authenticate(user=user)
        payload = {"password": "newpassword1234"}

        response = self.client.patch(ME_URL, payload)
        user.refresh_from_db()
        self.assertTrue(user.check_password(payload["password"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
