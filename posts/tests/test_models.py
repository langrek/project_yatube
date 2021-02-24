from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


class ModelTest(TestCase):
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
            author=cls.user
        )

    def test_group_verbose_name(self):
        group = ModelTest.group
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Слаг',
            'description': 'Описание'
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_group_help_text(self):
        group = ModelTest.group
        field_help_texts = {
            'title': 'Введите название группы',
            'description': 'Укажите описание'
        }

        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_post_verbose_name(self):
        post = ModelTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа'
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_post_help_text(self):
        post = ModelTest.post
        field_help_texts = {
            'text': 'Введите текст',
        }

        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_group_object_name_is_title_field(self):
        group = ModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_post_text_field(self):
        post = ModelTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))
