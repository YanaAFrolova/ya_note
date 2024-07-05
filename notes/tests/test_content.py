from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

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

    def test_notes_list_for_different_users(self):
        """
        В список заметок одного пользователя
        не попадают заметки другого пользователя.
        Отдельная заметка передаётся на страницу
        со списком заметок в списке object_list в словаре context.
        """
        users_statuses = (
            (self.author, True),
            (self.reader, False),
        )
        url = reverse('notes:list')
        for user, status in users_statuses:
            self.client.force_login(user)
            with self.subTest(user=user):
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, status)

    def test_pages_contains_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest():
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
