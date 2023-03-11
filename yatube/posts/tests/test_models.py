from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Это текст поста",
        )

    def test_correct__str__(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        vals = ((str(post), post.text[:15]), (str(group), group.title))
        for value, expected in vals:
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test__str__(self):
        """значение поля verbose_name в объектах моделей"""
        post = PostModelTest.post
        context = {
            "text": "Текст поста",
            "group": "Название группы",
        }

        for value, expected in context.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name,
                    expected
                )
                self.assertEqual(
                    post._meta.get_field(value).verbose_name,
                    expected
                )
