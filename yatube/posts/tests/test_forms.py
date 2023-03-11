from http import HTTPStatus

from django.test import Client
from django.urls import reverse

from posts.models import Comment, Group, Post, User
from django.test import TestCase


class PostFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="NoName")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()
        self.group = Group.objects.create(
            title="Титул",
            slug="slug",
            description="описание",
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        form_data = {"text": "Текст на русском",
                     "group": self.group.id,
                     }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse("posts:profile", kwargs={"username": self.user.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            text="Текст на русском",
            group=self.group.id
        ).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        """Валидная форма изменяет запись в Post."""
        self.group = Group.objects.create(
            title="Титул",
            slug="Slug",
            description="Описание",
        )

        post = Post.objects.create(
            author=self.user,
            text="Тестовый текст",
        )
        posts_count = Post.objects.count()
        form_data = {"text": "Изменяем текст", "group": self.group.id}
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=(post.id, )),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": post.id})
        )
        self.assertTrue(Post.objects.filter(
            text="Изменяем текст",
            group=self.group.id,
        ).exists())
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_comment(self):
        """
        Авторизованный пользователь может оставлять комментарии
        и он появится на странице поста
        """
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый коммент',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                post=self.post,
                text='Тестовый коммент',
                author=self.user,
            ).exists())

    def test_not_authorized_comment(self):
        """Не авторизованный пользователь не может оставлять комментарии"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый коммент',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertNotEqual(Comment.objects.count(), comments_count + 1)