from django.contrib.auth import get_user_model
from rest_framework import status, test
from rest_framework.reverse import reverse as api_reverse

USER = get_user_model()


class AnonymousAPITestCase(test.APITestCase):
    def setUp(self) -> None:
        user = USER.objects.create(
            username='hxt365testing',
            email='hxt365testing@gmail.com'
        )
        user.set_password('matkhaubatky')
        user.save()

    def test_login_true(self):
        url = api_reverse('api_auth:login')
        data = {
            'username': 'hxt365testing',
            'password': 'matkhaubatky'
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_when_password_is_incorrect_then_return_200_OK(self):
        url = api_reverse('api_auth:login')
        data = {
            'username': 'hxt365testing',
            'password': 'matkhausai'
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_signup_true(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365testing2',
            'password': 'matkhaudung',
            'password_2': 'matkhaudung',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'email': 'hxt365signup@gmail.com',
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_signup_false_1(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365false',
            'password': 'matkhaudung',
            'password_2': 'matkhausai',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'email': 'hxt365@gmail.com',
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_false_2(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365testing',
            'password': 'matkhausai',
            'password_2': 'matkhausai',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'email': 'hxt365abc@gmail.com',
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_true(self):
        url = api_reverse('api_auth:reset_password')
        data = {
            'username': 'hxt365testing',
            'email': 'hxt365testing@gmail.com',
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_reset_password_false(self):
        url = api_reverse('api_auth:reset_password')
        data = {
            'username': 'hxt365test',
            'email': 'hxt365signup@gmail.com',
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


# class AuthenticatedAPITestCase(test.APITestCase):
#     def setUp(self) -> None:
#         user = USER.objects.create(
#             username='hxt365testing',
#             email='hxt365testing@gmail.com'
#         )
#         user.set_password('matkhaubatky')
#         user.save()

    # def test_logout(self):
    #     url = api_reverse('api_auth:login')
    #     data = {
    #         'username': 'hxt365testing',
    #         'password': 'matkhaubatky'
    #     }
    #     res = self.client.post(url, data)
    #     url = api_reverse('api_auth:logout')
    #     res = self.client.post(url)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     AccessTokenModel = get_access_token_model()
    #     qs = AccessTokenModel.objects.filter(user__username='hxt365testing')
    #     self.assertEqual(qs.exists(), False)
#
#     def test_change_password(self):
#         url = api_reverse('api_auth:change_password')
#         data = {
#             'old_pass': 'matkhaubatky',
#             'new_pass': 'okokokok',
#             'new_pass_2': 'okokokok',
#         }
#         res = self.client.post(url, data)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)