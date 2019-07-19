from django.contrib.auth import get_user_model
from rest_framework import status, test
from rest_framework.reverse import reverse as api_reverse
from oauth2_provider.models import get_application_model
from oauth2_provider.settings import oauth2_settings
from django.conf import settings

USER = get_user_model()
Application = get_application_model()


class BaseTest(test.APITestCase):
    def setUp(self):
        self.test_user = USER.objects.create_user(
            username='test_user',
            email='test@example.com',
            first_name='random',
            last_name='random',
        )
        self.test_user.set_password('123456')
        self.test_user.save()
        self.dev_user = USER.objects.create_user(
            username='dev_user',
            email='dev@example.com',
            first_name='random',
            last_name='random',
        )
        self.dev_user.set_password('123456')
        self.dev_user.save()

        self.application = Application(
            name='test',
            user=self.dev_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
        )
        self.application.save()

        oauth2_settings._SCOPES = ['read', 'write']
        oauth2_settings._DEFAULT_SCOPES = ['read', 'write']

    def tearDown(self):
        self.application.delete()
        self.test_user.delete()
        self.dev_user.delete()

    def login(self, username, password):
        url = api_reverse('api_auth:login')
        data = {
            'username': username,
            'password': password,
        }
        res = self.client.post(url, data, format='json')
        return res

class AuthAPITestCase(BaseTest):
    def test_login_then_200_OK(self):
        res = self.login('test_user', '123456')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_with_wrong_username_then_400_bad_request(self):
        res = self.login('wrongusername', '123456')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_wrong_password_then_400_bad_request(self):
        res = self.login('test_user', 'wrongpassword')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_unverified_user_then_403_forbiden(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365',
            'email': 'hxt365@gmail.com',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'password': '123456',
            'password_2': '123456',
        }
        self.client.post(url, data, format='json')
        res = self.login('hxt365', '123456')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_refresh_then_200_OK(self):
        self.login('test_user', '123456')
        url = api_reverse('api_auth:refresh')
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_refresh_then_400_bad_request(self):
        self.login('wrong', 'wrong')
        url = api_reverse('api_auth:refresh')
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_then_200_OK(self):
        url = api_reverse('api_auth:reset_password')
        data = {
            'username': 'test_user',
            'email': 'test@example.com',
        }
        self.client.post(url, data, format='json')
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_reset_password_with_wrong_username_then_400_bad_request(self):
        url = api_reverse('api_auth:reset_password')
        data = {
            'username': 'wrong_user',
            'email': 'test@example.com',
        }
        self.client.post(url, data, format='json')
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_with_wrong_email_then_400_bad_request(self):
        url = api_reverse('api_auth:reset_password')
        data = {
            'username': 'test_user',
            'email': 'wrong@example.com',
        }
        self.client.post(url, data, format='json')
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_then_201_created(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365',
            'email': 'hxt365@gmail.com',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'password': '123456',
            'password_2': '123456',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_signup_with_username_less_than_6_characters_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': '123',
            'email': 'hxt365@gmail.com',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'password': '123456',
            'password_2': '123456',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_username_more_than_150_characters_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': '1' * 200,
            'email': 'hxt365@gmail.com',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'password': '123456',
            'password_2': '123456',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_username_contains_invalid_characters_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt!@#$%^&*(',
            'email': 'hxt365@gmail.com',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'password': '123456',
            'password_2': '123456',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_password_less_than_6_characters_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'test_user',
            'email': 'hxt365@gmail.com',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'password': '123',
            'password_2': '123',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_password_more_than_150_characters_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365',
            'email': 'hxt365@gmail.com',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'password': '1' * 200,
            'password_2': '1' * 200,
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_empty_password_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365',
            'email': 'hxt365@gmail.com',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'password': '',
            'password_2': '123456',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_passwords_unmatched_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365',
            'email': 'hxt365@gmail.com',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'password': 'rightpass',
            'password_2': 'wrongpass',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_taken_username_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'test_user',
            'email': 'hxt365@gmail.com',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'password': '123456',
            'password_2': '123456',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_taken_email_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365',
            'email': 'test@example.com',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'password': '123456',
            'password_2': '123456',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_wrong_email_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365',
            'email': 'hxt365gmail.com',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'password': '123456',
            'password_2': '123456',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_empty_email_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365',
            'email': '',
            'first_name': 'Truong',
            'last_name': 'Hoang',
            'password': '123456',
            'password_2': '123456',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_wrong_first_name_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365',
            'email': 'hxt365@gmail.com',
            'first_name': 'N4m',
            'last_name': 'Hoang',
            'password': '123456',
            'password_2': '123456',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_empty_first_name_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365',
            'email': 'hxt365@gmail.com',
            'first_name': '0',
            'last_name': 'Hoang',
            'password': '123456',
            'password_2': '123456',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_wrong_last_name_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365',
            'email': 'hxt365@gmail.com',
            'first_name': 'Truong',
            'last_name': 'H0ang',
            'password': '123456',
            'password_2': '123456',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_signup_with_empty_last_name_then_400_bad_request(self):
        url = api_reverse('api_auth:signup')
        data = {
            'username': 'hxt365',
            'email': 'hxt365@gmail.com',
            'first_name': 'Truong',
            'last_name': '',
            'password': '123456',
            'password_2': '123456',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_then_200_OK(self):
        self.login('test_user', '123456')
        url = api_reverse('api_auth:change_password')
        data = {
            'old_pass': '123456',
            'new_pass': 'newpass',
            'new_pass_2': 'newpass',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_change_password_with_new_password_more_than_150_characters_then_400_bad_request(self):
        self.login('test_user', '123456')
        url = api_reverse('api_auth:change_password')
        data = {
            'old_pass': '123456',
            'new_pass': '1'*200,
            'new_pass_2': '1'*200,
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_with_new_password_less_than_6_characters_then_400_bad_request(self):
        self.login('test_user', '123456')
        url = api_reverse('api_auth:change_password')
        data = {
            'old_pass': '123456',
            'new_pass': '123',
            'new_pass_2': '123',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_with_new_empty_password_then_400_bad_request(self):
        self.login('test_user', '123456')
        url = api_reverse('api_auth:change_password')
        data = {
            'old_pass': '123456',
            'new_pass': '',
            'new_pass_2': '',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_with_new_unmatched_passwords_then_400_bad_request(self):
        self.login('test_user', '123456')
        url = api_reverse('api_auth:change_password')
        data = {
            'old_pass': '123456',
            'new_pass': 'rightpass',
            'new_pass_2': 'wrongpass',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_with_wrong_old_password_then_400_bad_request(self):
        self.login('test_user', '123456')
        url = api_reverse('api_auth:change_password')
        data = {
            'old_pass': 'wrongpass',
            'new_pass': 'newpass',
            'new_pass_2': 'newpass',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_with_empty_old_password_then_400_bad_request(self):
        self.login('test_user', '123456')
        url = api_reverse('api_auth:change_password')
        data = {
            'old_pass': '',
            'new_pass': 'newpass',
            'new_pass_2': 'newpass',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_then_refresh_then_400_bad_request(self):
        self.login('test_user', '123456')
        url = api_reverse('api_auth:change_password')
        data = {
            'old_pass': '123456',
            'new_pass': 'newpass',
            'new_pass_2': 'newpass',
        }
        self.client.post(url, data, format='json')
        url = api_reverse('api_auth:refresh')
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_of_unauthenticated_user_then_401_unauthorized(self):
        url = api_reverse('api_auth:change_password')
        data = {
            'old_pass': '123456',
            'new_pass': 'newpass',
            'new_pass_2': 'newpass',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_with_new_password_same_to_5th_last_password_then_400_bad_request(self):
        self.login('test_user', '123456')
        old_pass = '123456'
        for i in range(5):
            url = api_reverse('api_auth:change_password')
            new_pass = 'newpass' + str(i)
            data = {
                'old_pass': old_pass,
                'new_pass': new_pass,
                'new_pass_2': new_pass,
            }
            old_pass = 'newpass' + str(i)
            self.client.post(url, data, format='json')
            self.login('test_user', new_pass)
        url = api_reverse('api_auth:change_password')
        data = {
            'old_pass': 'newpass4',
            'new_pass': 'newpass0',
            'new_pass_2': 'newpass0',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_with_new_password_differs_from_5_last_password_then_200_OK(self):
        self.login('test_user', '123456')
        old_pass = '123456'
        for i in range(6):
            url = api_reverse('api_auth:change_password')
            new_pass = 'newpass' + str(i)
            data = {
                'old_pass': old_pass,
                'new_pass': new_pass,
                'new_pass_2': new_pass,
            }
            old_pass = 'newpass' + str(i)
            self.client.post(url, data, format='json')
            self.login('test_user', new_pass)
        url = api_reverse('api_auth:change_password')
        data = {
            'old_pass': 'newpass5',
            'new_pass': 'newpass0',
            'new_pass_2': 'newpass0',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_logout_then_200_OK(self):
        self.login('test_user', '123456')
        url = api_reverse('api_auth:logout')
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_logout_unauthenticated_user_then_401_unauthorized(self):
        url = api_reverse('api_auth:logout')
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)