from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, User
from yatube.settings import COUNT
from posts.forms import PostForm


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="NoName")
        cls.group = Group.objects.create(
            title="Титул",
            slug="slug",
            description="описание",
        )
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
        cls.image = uploaded

        cls.post = Post.objects.create(
            author=cls.user,
            text="Текст",
            group=cls.group,
            image=cls.image,
        )

        cls.templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse("posts:group_progect", kwargs={"slug": cls.group.slug}):
                "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": cls.post.author}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": cls.post.id}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": cls.post.id}
            ): "posts/post_create.html",
            reverse("posts:post_create"): "posts/post_create.html",
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    def test_index(self):
        """index соответствует ожидаемому контексту"""
        response = self.guest_client.get(reverse("posts:index"))
        post_per = response.context['page_obj'][0]
        self.assertEqual(self.post, post_per)
        self.assertIsInstance(post_per, Post)

    def test_group(self):
        """group_progect соответствует ожидаемому контексту"""
        response = self.guest_client.get(
            reverse("posts:group_progect", kwargs={"slug": self.group.slug})
        )
        self.assertEqual(self.group, response.context['group'])
        post_per = response.context['page_obj'][0]
        self.assertEqual(self.post, post_per)
        self.assertIsInstance(post_per, Post)
        self.assertIsInstance(post_per.group, Group)

    def test_profile(self):
        """profile соответствует ожидаемому контексту"""
        response = self.guest_client.get(
            reverse("posts:profile", args=(self.post.author,))
        )
        post_per = response.context['page_obj'][0]
        self.assertEqual(self.user, response.context['author'])
        self.assertEqual(post_per, self.post)

    def test_post_detail(self):
        """post_detail соответствует ожидаемому контексту"""
        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        self.assertEqual(response.context.get("post").group, self.post.group)
        self.assertEqual(response.context.get("post").author, self.post.author)
        self.assertEqual(response.context.get("post").text, self.post.text)
        self.assertIsInstance(response.context.get("post"), Post)

    def test_post_edit(self):
        """post_edit соответствует ожидаемому контексту"""
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(response.context.get('form'), PostForm)
                self.assertIsInstance(form_field, expected)

    def test_create(self):
        """create соответствует ожидаемому контексту"""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(response.context.get('form'), PostForm)
                self.assertIsInstance(form_field, expected)

    def test_group_test(self):
        """Проверяем создание поста на страницах с выбранной группой"""
        form_fields = {
            reverse("posts:index"): self.post,
            reverse(
                "posts:profile", kwargs={"username": self.post.author}
            ): self.post,
            reverse(
                "posts:group_progect", kwargs={"slug": self.group.slug}
            ): self.post,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context["page_obj"]
                self.assertIn(expected, form_field)

    def test_group_not_in_post(self):
        """Проверка пост не попал в группу, для которой не был предназначен"""
        new_group = Group.objects.create(
            title='Другая группа',
            slug="sluggg",
            description="Другое описание",
        )
        post = Post.objects.create(
            author=self.user,
            text="Текст",
            group=self.group,
        )
        form_fields = {
            reverse(
                "posts:group_progect", kwargs={"slug": new_group.slug}
            ): post,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context["page_obj"]
                self.assertNotIn(expected, form_field)
   
    def test_index_show_correct_context(self):
        """Шаблон сформирован с правильным контекстом"""
        image = self.post.image
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context.get('page_obj')[0], self.post)
        self.assertEqual(response.context.get('page_obj')[0].image, image)

    def test_group_posts_show_correct_context(self):
        """Шаблон сформирован с правильным контекстом"""
        url = reverse('posts:group_progect', kwargs={'slug': self.group.slug})
        image = self.post.image
        response = self.authorized_client.get(url)
        self.assertEqual(response.context.get('group'), self.group)
        self.assertEqual(response.context.get('page_obj')[0].image, image)

    def test_profile_show_correct_context(self):
        """Шаблон сформирован с правильным контекстом"""
        url = reverse('posts:profile', kwargs={'username': self.user})
        image = self.post.image
        response = self.authorized_client.get(url)
        self.assertEqual(response.context.get('author'), self.user)
        self.assertEqual(response.context.get('page_obj')[0].image, image)

    def test_post_detail_show_correct_context(self):
        """Шаблон сформирован с правильным контекстом"""
        url = reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        image = self.post.image
        response = self.authorized_client.get(url)
        self.assertEqual(response.context.get('post').id, self.post.id)
        self.assertEqual(response.context.get('post').image, image)


class PaginatorViewsTest(TestCase):

    def setUp(self):
        FIRST_PAGE_AMOUNT = COUNT
        SECOND_PAGE_AMOUNT = 1
        SUM_PAGE = FIRST_PAGE_AMOUNT + SECOND_PAGE_AMOUNT
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        bilk_post: list = []
        for i in range(SUM_PAGE):
            bilk_post.append(Post(text=f'Тестовый текст {i}',
                                  group=self.group,
                                  author=self.user))
        Post.objects.bulk_create(bilk_post)

    def test_paginator(self):
        '''Проверка количества постов на страницах'''
        FIRST_PAGE_AMOUNT = COUNT
        SECOND_PAGE_AMOUNT = 1
        SUM_PAGE = FIRST_PAGE_AMOUNT + SECOND_PAGE_AMOUNT
        pages: tuple = (reverse('posts:index'),
                        reverse('posts:profile',
                                kwargs={'username': f'{self.user.username}'}),
                        reverse('posts:group_progect',
                                kwargs={'slug': f'{self.group.slug}'}))
        for page in pages:
            response1 = self.guest_client.get(page)
            response2 = self.guest_client.get(page + '?page=2')
            count_posts1 = len(response1.context['page_obj'])
            count_posts2 = len(response2.context['page_obj'])
            error_name1 = (f'Ошибка: {count_posts1} постов,'
                           f' должно {FIRST_PAGE_AMOUNT}')
            error_name2 = (f'Ошибка: {count_posts2} постов,'
                           f'должно {SUM_PAGE - FIRST_PAGE_AMOUNT}')
            self.assertEqual(count_posts1,
                             FIRST_PAGE_AMOUNT,
                             error_name1)
            self.assertEqual(count_posts2,
                             SUM_PAGE - FIRST_PAGE_AMOUNT,
                             error_name2)
