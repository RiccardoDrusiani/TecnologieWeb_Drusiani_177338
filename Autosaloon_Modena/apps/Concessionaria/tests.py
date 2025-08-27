from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import Concessionaria, HistoryVendute, HistoryAffittate
from ..Auto.models import Auto, AutoContrattazione

class ConcessionariaViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.group, _ = Group.objects.get_or_create(name='concessionaria')
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.user.groups.add(self.group)
        self.concessionaria = Concessionaria.objects.create(
            user=self.user,
            partita_iva='12345678901',
            codice_fiscale='RSSMRA80A01H501U',
            slug='testuser-slug'
        )

    def test_concessionaria_create_view(self):
        url = reverse('Concessionaria:concessionaria-create')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'conferma_password': 'newpass123',
            'partita_iva': '10987654321',
            'codice_fiscale': 'VRDLGI80A01H501U',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect dopo creazione
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(Concessionaria.objects.filter(partita_iva='10987654321').exists())

    def test_concessionaria_update_and_settings_view(self):
        self.client.login(username='testuser', password='testpass123')
        # UpdateView
        url = reverse('Concessionaria:concessionaria-update', kwargs={'slug': self.concessionaria.slug})
        response = self.client.post(url, {'partita_iva': '12345678901', 'codice_fiscale': 'RSSMRA80A01H501U'})
        self.assertIn(response.status_code, [200, 302])
        # Impostazioni (FullUpdateForm)
        url = reverse('Concessionaria:impostazioni_concessionaria')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'partita_iva': '12345678901',
            'codice_fiscale': 'RSSMRA80A01H501U',
            'telefono': '0591234567',
            'indirizzo': 'Via Roma 1',
        }
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [200, 302])
        self.concessionaria.refresh_from_db()
        self.assertEqual(self.concessionaria.telefono, '0591234567')
        self.assertEqual(self.concessionaria.indirizzo, 'Via Roma 1')

    def test_concessionaria_delete_view(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('Concessionaria:concessionaria-delete', kwargs={'slug': self.concessionaria.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username='testuser').exists())
        self.assertFalse(Concessionaria.objects.filter(partita_iva='12345678901').exists())

    def test_contrattazioni_auto_vendute_affittate_views(self):
        self.client.login(username='testuser', password='testpass123')
        # Contrattazioni
        url = reverse('Concessionaria:contrattazioni')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Auto vendute
        url = reverse('Concessionaria:auto_vendute')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Auto affittate
        url = reverse('Concessionaria:auto_affittate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
