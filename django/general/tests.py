from django.test import TestCase
from django.urls import reverse


class TestWelcomeView(TestCase):
    """
    Test Welcome View
    """
    def test_welcome_empty_get(self):
        """
        Test the simple welcome page is returned
        """
        url = reverse('general:welcome')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome')

    def test_welcome_nonempty_get(self):
        """
        Test the welcome home page is returned
        """
        url = reverse('general:welcome')
        response = self.client.get(url, {'nonsense': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome')


class TestCookiesView(TestCase):
    """
    Test Cookies View
    """
    def test_cookies_empty_get(self):
        """
        Test the simple cookies page is returned
        """
        url = reverse('general:cookies')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cookies')

    def test_cookies_nonempty_get(self):
        """
        Test the cookies home page is returned
        """
        url = reverse('general:cookies')
        response = self.client.get(url, {'nonsense': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cookies')
