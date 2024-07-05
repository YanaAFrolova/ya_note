from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Artur')
        cls.reader = User.objects.create(username='Vasya')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author
        )

    def test_home_availability_for_all_user(self):
        """
        Главная страница, страницы регистрации пользователей,
        входа и выхода из учётной записи доступны всем пользователям.
        """
        urls = (
            ('notes:home', 'users:login', 'users:logout', 'users:signup')

        )
        for url in urls:
            with self.subTest():
                url = reverse(url)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_home_availability_for_auth_user(self):
        """
        Страницы списка заметок, добавления новой заметки,
        успешного добавления заметки доступны
        авторизованному пользователю.
        """
        urls = (
            ('notes:list', 'notes:add', 'notes:success')

        )
        self.client.force_login(self.reader)
        for url in urls:
            with self.subTest():
                url = reverse(url)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """
        Страницы отдельной заметки, удаления и редактирования заметки доступны
        только автору заметки. Если на эти страницы попытается зайти
        другой пользователь — вернётся ошибка 404.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            ('notes:detail'),
            ('notes:edit'),
            ('notes:delete'),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        """
        Анонимный пользователь перенаправляется на страницу авторизации
        при попытке перейти на страницу списка заметок, редактирования
        или удаления, добавления, успешнго добавления заметок.
        """
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        login_url = reverse('users:login')
        for name, args in urls:
            url = reverse(name, args=args)
            expected_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, expected_url)
