from django.shortcuts import reverse
from django.test import TestCase, Client

from .models import Post, User


class TestScriptUser(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="sarah",
                                             email="connor.s@skynet.com",
                                             password="12345")
        self.client.login(username="sarah", password="12345")

    def test_profile(self):
        response = self.client.get(
            reverse("profile", args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page"]), 0)
        self.assertIsInstance(response.context["requested_user"], User)
        self.assertEqual(response.context["requested_user"].username,
                         self.user.username)

    def test_new_post(self):
        response = self.client.post(reverse('new_post'),
                                    {'text': 'Привет ревьюерам!'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_new_post(self):
        self.client.logout()
        response = self.client.post(reverse('new_post'),
                                    {'text': 'Привет ревьюерам!'},
                                    follow=True)
        self.assertRedirects(response, '/auth/login/')
        self.client.login(username="sarah", password="12345")

    def test_post_appears(self):
        self.post = Post.objects.create(text="Hello, World!", author=self.user)
        response = self.client.get(
            reverse('post', args=[self.user.username, self.post.id]))
        self.assertEqual(response.context["post"].id, self.post.id)
        response_index = self.client.get(reverse('index'))
        self.assertIn(self.post, response_index.context['page'])
        response_profile = self.client.get(
            reverse('profile', args=[self.user.username]))
        self.assertIn(self.post, response_profile.context['page'])

    def test_post_edit(self):
        new_text = 'Привет ревьюерам!'
        self.post = Post.objects.create(text="Hello, Nika", author=self.user)
        response = self.client.post(reverse(
            'post_edit', args=[self.user.username, self.post.id]),
                                    {'text': new_text},
                                    follow=True)
        self.assertEqual(Post.objects.get(id=self.post.id).text, new_text)
        # Мы убедились, что обновлённый текст попал в базу данных, а это означает,
        # что все соответствующие view будут отображать обновлённый текст.
