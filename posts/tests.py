from django.shortcuts import reverse
from django.test import TestCase, Client

from .models import Post, User, Group


class TestScriptUser(TestCase):
    def setUp(self):
        self.unauth_client = Client()
        self.auth_client = Client()
        self.user = User.objects.create_user(username="sarah",
                                             email="connor.s@skynet.com",
                                             password="12345")
        self.group = Group.objects.create(title='Cats', slug='cats')
        self.auth_client.force_login(self.user)

    def test_profile(self):
        response = self.auth_client.get(
            reverse("profile", args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page"]), 0)
        self.assertIsInstance(response.context["requested_user"], User)
        self.assertEqual(response.context["requested_user"].username,
                         self.user.username)

    def test_new_post(self):
        post_text = 'Привет ревьюерам!'
        response = self.auth_client.post(reverse('new_post'),
                                         {'text': post_text},
                                         follow=True)
        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(text=post_text)
        # если поста нет в БД, то будет выкинуто исключение и тест провалится

    def test_unauthorized_new_post(self):
        response = self.unauth_client.post(reverse('new_post'),
                                           {'text': 'Привет ревьюерам!'},
                                           follow=True)
        self.assertRedirects(response, '/auth/login/')

    def check_post_in_page(self, client, post, username):
        response_post = client.get(reverse('post', args=[username, post.id]))
        self.assertEqual(response_post.context["post"].id, post.id)
        response_index = client.get(reverse('index'))
        self.assertIn(post, response_index.context['page'])
        response_profile = client.get(reverse('profile', args=[username]))
        self.assertIn(post, response_profile.context['page'])

    def test_post_appears(self):
        post = Post.objects.create(text="Hello, World!", author=self.user)
        self.check_post_in_page(self.auth_client, post, self.user.username)

    def test_post_edit(self):
        new_text = 'Привет ревьюерам!'
        post = Post.objects.create(text="Hello, Nika", author=self.user)
        response = self.auth_client.post(reverse(
            'post_edit', args=[self.user.username, post.id]),
                                         {'text': new_text},
                                         follow=True)
        self.assertEqual(Post.objects.get(id=post.id).text, new_text)
        # Мы убедились, что обновлённый текст попал в базу данных, а это означает,
        # что все соответствующие view будут отображать обновлённый текст.
        self.check_post_in_page(self.auth_client, post, self.user.username)
