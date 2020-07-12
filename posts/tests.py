from collections.abc import Iterable
from time import sleep

from django.shortcuts import reverse
from django.test import TestCase, Client

from .models import Post, User, Group, Follow


class TestScriptUser(TestCase):
    def setUp(self):
        self.not_logged_in_client = Client()
        self.sarah = User.objects.create_user(username="sarah",
                                              email="connor.s@skynet.com",
                                              password="12345")
        self.jack = User.objects.create_user(username="jack",
                                             email="ceo@twitter.com",
                                             password="12345")
        self.mark = User.objects.create_user(username="zuck",
                                             email="ceo@facebook.com",
                                             password="12345")
        self.group = Group.objects.create(title='Women', slug='women')
        self.sarah_client = Client()
        self.sarah_client.force_login(self.sarah)
        self.mark_client = Client()
        self.mark_client.force_login(self.mark)

    def test_profile(self):
        response = self.sarah_client.get(
            reverse("profile", args=[self.sarah.username]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page"]), 0)
        self.assertIsInstance(response.context["profile"], User)
        self.assertEqual(response.context["profile"].username,
                         self.sarah.username)

    def test_new_post(self):
        post_text = 'Привет ревьюерам!'
        response = self.sarah_client.post(reverse('new_post'),
                                          {'text': post_text},
                                          follow=True)
        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(text=post_text)
        urls_with_ctx_key = [
            ('post', reverse('post', args=[self.sarah.username, post.id])),
            ('page', reverse('profile', args=[self.sarah.username]))
        ]
        for ctx_key, url in urls_with_ctx_key:
            self.check_post_in_response_context(self.sarah_client, url,
                                                ctx_key, post)

    def test_unauthorized_new_post(self):
        response = self.not_logged_in_client.post(
            reverse('new_post'), {'text': 'Привет ревьюерам!'}, follow=True)
        self.assertRedirects(response, '/auth/login/')

    def check_post_in_response_context(self, client, url, ctx_key, post):
        """
        Asserts that after `client` gets `response` from `url`
        its `response.context[ctx_key]` contains `post`.
        """
        response = client.get(url)
        ctx_value = response.context[ctx_key]
        if not isinstance(ctx_value, Iterable):
            ctx_value = [ctx_value]
        self.assertIn(post, ctx_value)

    def test_post_appears(self):
        post = Post.objects.create(text="Hello, World!", author=self.sarah)
        urls_with_ctx_key = [
            ('post', reverse('post', args=[self.sarah.username, post.id])),
            ('page', reverse('index')),
            ('page', reverse('profile', args=[self.sarah.username]))
        ]
        for ctx_key, url in urls_with_ctx_key:
            self.check_post_in_response_context(self.sarah_client, url,
                                                ctx_key, post)

    def test_404_not_found(self):
        response = self.sarah_client.get('empty/url')
        self.assertEqual(response.status_code, 404)

    def test_post_edit(self):
        new_text = 'Привет ревьюерам!'
        post = Post.objects.create(text="Hello, Nika", author=self.sarah)
        response = self.sarah_client.post(reverse(
            'post_edit', args=[self.sarah.username, post.id]),
                                          {'text': new_text},
                                          follow=True)
        self.assertEqual(Post.objects.get(id=post.id).text, new_text)
        urls_with_ctx_key = [
            ('post', reverse('post', args=[self.sarah.username, post.id])),
            ('page', reverse('index')),
            ('page', reverse('profile', args=[self.sarah.username]))
        ]
        for ctx_key, url in urls_with_ctx_key:
            self.check_post_in_response_context(self.sarah_client, url,
                                                ctx_key, post)

    def test_follow_unfollow(self):
        author_username = self.jack.username

        follow_response = self.sarah_client.post(reverse(
            'profile_follow', args=[author_username]),
                                                 follow=True)
        self.assertEqual(follow_response.status_code, 200)
        self.assertEqual(
            Follow.objects.filter(user=self.sarah, author=self.jack).count(),
            1)

        unfollow_response = self.sarah_client.post(reverse(
            'profile_unfollow', args=[author_username]),
                                                   follow=True)
        self.assertEqual(unfollow_response.status_code, 200)
        self.assertEqual(
            Follow.objects.filter(user=self.sarah, author=self.jack).count(),
            0)

    def test_follow_index(self):
        post = Post.objects.create(
            text="There is no fate, but what we create.", author=self.jack)

        response = self.sarah_client.post(reverse('profile_follow',
                                                  args=[self.jack.username]),
                                          follow=True)
        self.assertEqual(response.status_code, 200)

        sarah_response = self.sarah_client.get(reverse('follow_index'))
        self.assertIn(post, sarah_response.context['page'])

        mark_response = self.mark_client.get(reverse('follow_index'))
        self.assertEqual(len(mark_response.context['page']), 0)

    def test_logged_in_comment(self):
        post = Post.objects.create(text="People should own their data.",
                                   author=self.jack)
        add_comment_url = reverse('add_comment',
                                  args=[self.jack.username, post.id])

        self.assertEqual(len(post.comments.all()), 0)
        self.mark_client.post(add_comment_url,
                              {'text': 'I strongly disagree!'})
        self.assertEqual(len(post.comments.all()), 1)

        response = self.not_logged_in_client.post(add_comment_url,
                                                  {'text': 'LOL'},
                                                  follow=True)
        self.assertRedirects(response,
                             f'/auth/login/?next={add_comment_url}',
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)
        self.assertEqual(len(post.comments.all()), 1)

    def test_thumbnail(self):
        post_text = 'Margaret Hamilton developed on-board flight software for NASA\'s Apollo program.'

        with open('tests/data/Margaret_Hamilton.jpg', 'rb') as img:
            self.sarah_client.post(reverse('new_post'), {
                'text': post_text,
                'image': img,
                'group': self.group.id
            },
                                   follow=True)
        post = Post.objects.get(text=post_text)

        post_response = self.sarah_client.get(
            reverse('post', args=[self.sarah.username, post.id]))
        self.assertContains(post_response, text='img', count=2)

        profile_response = self.sarah_client.get(
            reverse('profile', args=[self.sarah.username]))
        self.assertContains(profile_response, text='img', count=2)

        group_response = self.sarah_client.get(
            reverse('group_posts', args=[self.group.slug]))
        self.assertContains(group_response, text='img', count=2)

        sleep(20)  # let cache become stale

        index_response = self.sarah_client.get(reverse('index'))
        self.assertContains(index_response, text='img', count=2)

    def test_non_img_file(self):
        with open('README.md', 'rb') as file:
            self.sarah_client.post(reverse('new_post'), {
                'text': 'test_non_img',
                'image': file,
                'group': self.group.id
            },
                                   follow=True)
        self.assertRaises(Post.DoesNotExist,
                          Post.objects.get,
                          text='test_non_img')
