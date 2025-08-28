from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import UserExtendModel

class UtenteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.group, _ = Group.objects.get_or_create(name='utente')
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123', first_name='Mario', last_name='Rossi')
        self.user.groups.add(self.group)
        self.user_extend = UserExtendModel.objects.create(user=self.user, slug='testuser-slug')

    def test_user_create_view(self):
        url = reverse('Utente:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'Luca',
            'last_name': 'Verdi',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserExtendModel.objects.filter(user__username='newuser').exists())

    def test_user_update_view(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('Utente:modifica_utente', kwargs={'slug': self.user_extend.slug})
        data = {
            'email': 'nuovo@email.com',
            'first_name': 'Giovanni',
            'last_name': 'Bianchi',
            'data_nascita': '1990-01-01',
            'indirizzo': 'Via Nuova 1',
            'telefono': '3331234567',
        }
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [200, 302])
        self.user.refresh_from_db()
        self.user_extend.refresh_from_db()
        self.assertEqual(self.user.email, 'nuovo@email.com')
        self.assertEqual(self.user.first_name, 'Giovanni')
        self.assertEqual(self.user_extend.indirizzo, 'Via Nuova 1')
        self.assertEqual(self.user_extend.telefono, '3331234567')

    def test_user_delete_view(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('Utente:elimina_utente', kwargs={'slug': self.user_extend.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username='testuser').exists())
        self.assertFalse(UserExtendModel.objects.filter(slug='testuser-slug').exists())

    def test_user_settings_view(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('Utente:impostazioni_utente')
        data = {
            'email': 'settings@email.com',
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'data_nascita': '1985-05-05',
            'indirizzo': 'Via delle Rose',
            'telefono': '3200000000',
        }
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [200, 302])
        self.user.refresh_from_db()
        self.user_extend.refresh_from_db()
        self.assertEqual(self.user.email, 'settings@email.com')
        self.assertEqual(self.user_extend.indirizzo, 'Via delle Rose')
        self.assertEqual(self.user_extend.telefono, '3200000000')
