from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class ViewFunTests(TestCase):
    def setUp(self):
        self.authorized_client = Client()
        self.user = get_user_model().objects.create_user(username='user')
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_page_names = {
            'about/tech.html': reverse('about:tech'),
            'about/author.html': reverse('about:author'),
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
