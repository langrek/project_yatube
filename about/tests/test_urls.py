from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class UrlTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = get_user_model().objects.create_user(username='user')
        self.authorized_client.force_login(self.user)

    def test_guest_url_exists_at_desired_location(self):
        templates_urls_names = [
            '/about/author/',
            '/about/author/'
        ]
        for url in templates_urls_names:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'about/tech.html': '/about/tech/',
            'about/author.html': '/about/author/'
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
