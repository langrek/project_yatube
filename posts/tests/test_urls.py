from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый текст',
            slug='test-slug',
            description='Описание'
        )
        cls.user = get_user_model().objects.create_user(username='user')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
            id=1
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.templates_urls_names_authorized = {
            '/': 'index.html',
            f'/group/{self.group.slug}/': 'group.html',
            '/new/': 'new_post.html',
            f'/{self.user.username}/': 'profile.html',
            f'/{self.user.username}/{self.post.id}/edit/': 'new_post.html',
        }
        self.urls_for_guest = [
            '/',
            f'/group/{self.group.slug}/',
            f'/{self.user.username}/',
            f'/{self.user.username}/{self.post.id}/',
            f'/{self.user.username}/{self.post.id}/edit/',
            '/new/'
        ]
        self.urls_for_guest_redirect = [
            '/new/',
            f'/{self.user.username}/{self.post.id}/edit/']
        self.templates_urls_names_guest = {
            'index.html': '/',
            'group.html': f'/group/{self.group.slug}/',
        }

    def test_authorized_url_exists_at_desired_location(self):
        for url in self.templates_urls_names_authorized.keys():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_authorized_url_uses_correct_templates(self):
        for url, template in self.templates_urls_names_authorized.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_guest_url_exists_at_desired_location(self):
        for url in self.urls_for_guest:
            with self.subTest():
                response = self.guest_client.get(url)
                if url in self.urls_for_guest_redirect:
                    self.assertEqual(response.status_code, 302)
                else:
                    self.assertEqual(response.status_code, 200)

    def test_guest_url_uses_correct_templates(self):
        for template, url in self.templates_urls_names_guest.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_guest_correct_redirect(self):
        redirect = '/auth/login/'
        url = f'/{self.user.username}/{self.post.id}/edit/'
        response = self.guest_client.get(url)
        self.assertRedirects(response, redirect)

    def test_404(self):
        response = self.authorized_client.get('/not_exist/')
        self.assertEqual(response.status_code, 404)
