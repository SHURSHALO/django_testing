from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestCommentEditDelete(TestCase):
    NOTE_TEXT = 'пам'
    NOTE_TITLE = 'парам'
    NOTE_SLUG = '1'

    NOTE_TITLE_NEW = 'Текст комментария'
    NOTE_TEXT_NEW = 'Обновлённый комментарий'
    NOTE_SLUG_NEW = '4'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.id,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.id,))
        cls.add_url = reverse('notes:add')
        cls.form_data = {
            'title': cls.NOTE_TITLE_NEW,
            'text': cls.NOTE_TEXT_NEW,
            'slug': cls.NOTE_SLUG_NEW,
        }
        cls.url_to_success = '/done/'

    def test_author_can_delete_comment(self):
        response = self.author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_cant_delete_comment_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 1)

    def test_author_can_edit_comment(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT_NEW)
        self.assertEqual(self.note.title, self.NOTE_TITLE_NEW)
        self.assertEqual(self.note.slug, self.NOTE_SLUG_NEW)

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)

    def test_logged_in_user_can_create_note(self):
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_success)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)

    def test_anonymous_user_cannot_create_note(self):
        response = self.client.post(self.add_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_cannot_create_note_with_duplicate_slug(self):
        bad_note = {
            'title': self.NOTE_TITLE_NEW,
            'text': self.NOTE_TEXT_NEW,
            'slug': self.NOTE_SLUG,
        }
        response = self.author_client.post(self.add_url, data=bad_note)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.note.slug + WARNING,
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class NoteCreationTestCase(TestCase):
    NOTE_TEXT = 'Новый текст'
    NOTE_TITLE = 'Новый заголовок'

    def setUp(self):
        self.author = User.objects.create(username='Автор')
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_create_note_with_auto_slug(self):
        form_data = {'text': self.NOTE_TEXT, 'title': self.NOTE_TITLE}
        response = self.author_client.post(
            reverse('notes:add'), data=form_data
        )
        self.assertRedirects(response, '/done/')
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.latest('id')
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_empty_slug(self):
        form_data = {
            'text': self.NOTE_TEXT,
            'title': self.NOTE_TITLE,
            'slug': '',
        }
        response = self.author_client.post(
            reverse('notes:add'), data=form_data
        )
        self.assertRedirects(response, '/done/')

        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.latest('id')
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
