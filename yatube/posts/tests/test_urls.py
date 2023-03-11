from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group, User

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="NoName")
        cls.author_1 = User.objects.create_user(username="yes")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Описание",
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая пост",
            group=cls.group,
        )

        cls.templates_url_names = [
            ("/", "posts/index.html"),
            (f"/group/{cls.group.slug}/", "posts/group_list.html"),
            (f"/profile/{cls.user.username}/", "posts/profile.html"),
            (f"/posts/{cls.post.id}/", "posts/post_detail.html"),
            (f"/posts/{cls.post.id}/edit/", "posts/post_create.html"),
            ("/create/", "posts/post_create.html"),
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(PostURLTests.author_1)
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_open_pages_available_to_everyone(self):
        """Страницы open_pages доступны любому пользователю."""
        field_response_urls_code = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
        }
        for url, response_code in field_response_urls_code.items():
            with self.subTest(url=url):
                status_code = self.guest_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_merged_dict_available_to_autorizate(self):
        """Страницы closed_pages доступны авторизованному пользователю."""
        field_response_urls_code = {
            '/create/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.OK,
        }
        for url, response_code in field_response_urls_code.items():
            with self.subTest(url=url):
                status_code = self.authorized_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_urls(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, tmplate in PostURLTests.templates_url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK,)
        self.assertTemplateUsed(response, tmplate)

    def test_uknown_page(self):
        """Тест на несуществующую страницу"""
        response = self.authorized_client.get("/unknown/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_testss(self):
        """Проверяем переадресацию для авторизованного
        пользователя при редактировании чужого поста"""
        response = self.authorized_user.post(
            f"/posts/{self.post.id}/edit/", follow=True
        )
        self.assertRedirects(response, f"/posts/{self.post.id}/")
        self.assertEqual(response.status_code, 200)
