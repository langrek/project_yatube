import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый текст',
            slug='test-slug',
            description='Описание'
        )

        cls.user = get_user_model().objects.create_user(username='user')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse('index'))

    def test_post_edit(self):
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
        )
        count = Post.objects.count()
        form_data_edit = {
            'text': 'Другой текст',
            'group': self.group.id
        }
        response = self.authorized_client.post(reverse('post_edit', kwargs={
            'username': self.user,
            'post_id': post.id}),
            data=form_data_edit,
            follow=True)
        post.refresh_from_db()
        self.assertEqual(Post.objects.count(), count)
        self.assertEqual(str(post), form_data_edit['text'])
        self.assertRedirects(response, reverse('post', kwargs={
            'username': self.user,
            'post_id': post.id
        }))
