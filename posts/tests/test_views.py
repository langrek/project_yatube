import shutil

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post


class ViewFunTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Тестовый текст',
            slug='test-slug',
            description='Описание'
        )
        cls.group = Group.objects.get(slug='test-slug')
        cls.user = get_user_model().objects.create_user(
            username='user'
        )
        cls.following = get_user_model().objects.create_user(
            username='following'
        )
        cls.follower = get_user_model().objects.create_user(
            username='follower'
        )
        cls.another_follower = get_user_model().objects.create_user(
            username='another_follower'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        for i in range(11):
            Post.objects.create(
                text='Тестовый текст',
                group=cls.group,
                author=cls.user,
                id=i,
                image=uploaded
            )
        cls.not_right_group = Group.objects.create(
            title='Неправильнон название',
            slug='wrong-slug',
            description='Описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
            id=11,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)
        self.authorized_another_follower = Client()
        self.authorized_follower.force_login(self.another_follower)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.templates_url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': 'test-slug'}),
            'new_post.html': reverse('new_post')
        }

        self.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        self.context_for_tests = {
            'response.context.get("page")[0].text': 'Тестовый текст',
            'str(response.context.get("page")[0].group)': 'Тестовый текст',
            'response.context.get("page")[0].author': 'user'

        }

    def test_pages_uses_correct_template(self):
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        post_text = response.context.get('page')[0].text
        post_group = response.context.get('page')[0].group
        post_author = response.context.get('page')[0].author
        post_image = response.context.get('page')[0].image
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.group)
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_image, self.post.image)

    def test_group_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse(
            'group', kwargs={'slug': 'test-slug'})
        )
        post_text = response.context.get('page')[0].text
        post_group = response.context.get('page')[0].group
        post_author = response.context.get('page')[0].author
        post_image = response.context.get('page')[0].image
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.group)
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_image, self.post.image)

    def test_new_post_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('post_edit', kwargs={
            'username': self.user,
            'post_id': self.group.id}))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'profile', kwargs={'username': self.user})
        )
        post_text = response.context.get('page')[0].text
        post_group = response.context.get('page')[0].group
        post_author = response.context.get('page')[0].author
        post_image = response.context.get('page')[0].image
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.group)
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_image, self.post.image)

    def test_post_context_create(self):
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст'
        }
        self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group.slug})
        )
        self.authorized_client.post(
            reverse('new_post'), data=form_data, follow=True
        )

        response_index_page = self.authorized_client.get(reverse('index'))
        post_text_index = response_index_page.context.get('page')[0].text
        self.assertEqual(post_text_index, form_data['text'])

        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(
            response.context.get('page')[0].text, form_data['text']
        )
        form_wrong_data = {
            'group': self.not_right_group.id,
            'text': 'Другой текст'
        }
        self.authorized_client.post(
            reverse('new_post'), data=form_wrong_data, follow=True
        )
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.not_right_group.slug})
        )
        self.assertNotEqual(
            response.context.get('page')[0].text, form_data['text']
        )

    def test_edit_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('post_edit', kwargs={
            'username': self.user,
            'post_id': self.group.id}))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_first_page_containse_ten_records(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_two_records(self):
        response = self.authorized_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 2)

    def test_cache(self):
        response = self.authorized_client.get(reverse('index'))
        cached_response_content = response.content
        instance = Post.objects.get(id=11)
        instance.delete()
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(cached_response_content, response.content)

    def test_follow_unfollow(self):
        self.authorized_client.get(reverse(
            'profile_follow', kwargs={'username': self.following})
        )
        self.assertEqual(Follow.objects.filter(user=self.user).count(), 1)
        self.authorized_client.get(reverse(
            'profile_unfollow', kwargs={'username': self.following}
        ))
        self.assertEqual(Follow.objects.filter(user=self.user).count(), 0)

    def test_posts_follow_index(self):
        self.authorized_follower.get(reverse(
            'profile_follow', kwargs={'username': self.user})
        )
        response = self.authorized_follower.get(reverse('follow_index'))
        author = response.context.get('page')[0].author
        self.assertEqual(author, self.user)
        another_response = self.authorized_another_follower.get(
            reverse('follow_index')
        )
        self.assertNotEqual(response, another_response)

    def test_authorized_comment(self):
        form_data = {
            'text': 'Тестовый текст'
        }
        self.authorized_client.post(reverse(
            'add_comment',
            kwargs={'username': self.user, 'post_id': self.post.id}),
            data=form_data, follow=True
        )
        self.assertEqual(Comment.objects.count(), 1)
