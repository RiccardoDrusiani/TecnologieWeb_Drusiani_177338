from django.test import TestCase
from django.contrib.auth.models import User, Group
from .models import Auto, AutoVendita, AutoAffitto, AutoListaAffitto, AutoContrattazione, AutoPrenotazione
from .form import AddAutoForm, ModifyAutoForm
from .auto_utils import gestione_vendita_affitto, check_affittata_in_periodo
from datetime import datetime, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from apps.Utente.models import UserExtendModel
from django.utils import timezone


class AutoViewIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        UserExtendModel.objects.create(user=self.user)
        self.user_group, _ = Group.objects.get_or_create(name='utente')
        self.user.groups.add(self.user_group)
        self.client.login(username='testuser', password='testpass')

    def test_add_and_modify_auto_view(self):
        # 1. Aggiunta auto con vendita e affitto
        add_url = reverse('Auto:add_auto')
        form_data = {
            'marca': 'Toyota',
            'modello': 'Yaris',
            'cilindrata': 1200,
            'carburante': 0,
            'cambio': 0,
            'trazione': 0,
            'anno': 2022,
            'disponibilita': 2,  # vendita e affitto
            'chilometraggio': 10000,
            'prezzo_vendita': 10000,
            'prezzo_affitto': 50,
        }
        response = self.client.post(add_url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        auto = Auto.objects.last()
        self.assertIsNotNone(auto)
        self.assertIsNotNone(AutoVendita.objects.filter(auto=auto).first())
        self.assertIsNotNone(AutoAffitto.objects.filter(auto=auto).first())
        # 2. Modifica auto a solo affitto
        modify_url = reverse('Auto:modify_auto', kwargs={'pk': auto.pk})
        form_data_mod = {
            'marca': 'Toyota',
            'modello': 'Yaris',
            'cilindrata': 1200,
            'carburante': 0,
            'cambio': 0,
            'trazione': 0,
            'anno': 2022,
            'disponibilita': 1,  # solo affitto
            'chilometraggio': 10000,
            'prezzo_affitto': 60,
        }
        response = self.client.post(modify_url, form_data_mod, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(AutoVendita.objects.filter(auto=auto).first())
        affitto = AutoAffitto.objects.filter(auto=auto).first()
        self.assertIsNotNone(affitto)
        self.assertEqual(affitto.prezzo_affitto, 60)

class ContrattazioneCBVIntegrationTest(TestCase):
    def setUp(self):
        self.venditore = User.objects.create_user(username='venditore', password='testpass')
        UserExtendModel.objects.create(user=self.venditore)
        self.acquirente = User.objects.create_user(username='acquirente', password='testpass')
        UserExtendModel.objects.create(user=self.acquirente)
        self.venditore_group, _ = Group.objects.get_or_create(name='utente')
        self.acquirente_group, _ = Group.objects.get_or_create(name='utente')
        self.venditore.groups.add(self.venditore_group)
        self.acquirente.groups.add(self.acquirente_group)
        self.auto = Auto.objects.create(
            user_auto=self.venditore,
            id_possessore=self.venditore.id,
            tipologia_possessore='0',
            marca='Fiat',
            modello='Panda',
            cilindrata=1200,
            carburante=0,
            cambio=0,
            trazione=0,
            anno=2020,
            disponibilita=0,  # vendita
            chilometraggio=5000,
        )
        self.vendita = AutoVendita.objects.create(auto=self.auto, prezzo_vendita=8000, venditore=self.venditore.id)

    def test_flusso_contrattazione_cbv(self):
        # Login come acquirente
        self.client.login(username='acquirente', password='testpass')
        # 1. Avvia contrattazione
        url_contr = reverse('Auto:contrattazione_auto_inCorso', kwargs={'pk': self.auto.pk})
        data_contr = {'prezzo_attuale': 7800}
        response = self.client.post(url_contr, data_contr, follow=True)
        self.assertEqual(response.status_code, 200)
        contrattazione = AutoContrattazione.objects.filter(auto=self.auto).first()
        self.assertIsNotNone(contrattazione)
        self.assertEqual(contrattazione.prezzo_attuale, 7800)
        # 2. Invio offerta (contratta)
        url_offerta = reverse('Auto:contrattazione_offerta_update', kwargs={'pk': contrattazione.pk})
        data_offerta = {'prezzo_attuale': 7700}
        response = self.client.post(url_offerta, data_offerta, follow=True)
        self.assertEqual(response.status_code, 200)
        contrattazione.refresh_from_db()
        self.assertEqual(contrattazione.prezzo_attuale, 7700)
        # 3. Accetta la contrattazione (successo)
        url_successo = reverse('Auto:contrattazione_successo', kwargs={'pk': contrattazione.pk})
        response = self.client.post(url_successo, follow=True)
        self.assertEqual(response.status_code, 200)
        # Dopo il successo, la contrattazione deve essere eliminata e l'auto cambiata di possessore
        self.assertFalse(AutoContrattazione.objects.filter(pk=contrattazione.pk).exists())
        auto = Auto.objects.get(pk=self.auto.pk)
        self.assertEqual(auto.user_auto_id, self.acquirente.id)
        # 4. Riprova: crea nuova contrattazione e rifiuta (fallita)
        # Serve reimpostare l'auto come vendibile
        auto.user_auto = self.acquirente
        auto.id_possessore = self.acquirente.id
        auto.tipologia_possessore = '0'
        auto.disponibilita = 0
        auto.save()
        AutoVendita.objects.create(auto=auto, prezzo_vendita=7500, venditore=self.acquirente.id)
        url_contr2 = reverse('Auto:contrattazione_auto_inCorso', kwargs={'pk': auto.pk})
        data_contr2 = {'prezzo_attuale': 7400}
        response = self.client.post(url_contr2, data_contr2, follow=True)
        self.assertEqual(response.status_code, 200)
        contrattazione2 = AutoContrattazione.objects.filter(auto=auto).first()
        self.assertIsNotNone(contrattazione2)
        url_fallita = reverse('Auto:contrattazione_fallita', kwargs={'pk': contrattazione2.pk})
        response = self.client.post(url_fallita, follow=True)
        self.assertEqual(response.status_code, 200)
        # Dopo il fallimento, la contrattazione deve essere eliminata e l'auto tornare disponibile
        self.assertFalse(AutoContrattazione.objects.filter(pk=contrattazione2.pk).exists())
        auto.refresh_from_db()
        self.assertEqual(auto.disponibilita, 0)

    def test_affitto_e_prenotazione(self):
        # Crea due utenti
        user1 = User.objects.create_user(username='utente1', password='testpass')
        UserExtendModel.objects.create(user=user1)
        user2 = User.objects.create_user(username='utente2', password='testpass')
        UserExtendModel.objects.create(user=user2)
        group, _ = Group.objects.get_or_create(name='utente')
        user1.groups.add(group)
        user2.groups.add(group)

        # Crea un'auto disponibile per affitto (possessore user1)
        auto = Auto.objects.create(
            user_auto=user1,
            id_possessore=user1.id,
            tipologia_possessore='0',
            marca='Fiat',
            modello='500',
            cilindrata=1200,
            carburante=0,
            cambio=0,
            trazione=0,
            anno=2021,
            disponibilita=1,  # solo affitto
            chilometraggio=10000,
        )
        affitto = AutoAffitto.objects.create(auto=auto, prezzo_affitto=40, affittante=user1.id)

        # --- TEST AFFITTO ---
        # Primo utente NON possessore affitta l'auto in un periodo
        self.client.login(username='utente2', password='testpass')
        affitta_url = reverse('Auto:affitta_auto', kwargs={'pk': auto.pk})
        affitto_url = reverse('Auto:affitto_auto', kwargs={'pk': auto.pk})
        data_affitto = {
            'data_inizio': '2025-09-01',
            'data_fine': '2025-09-10',
        }
        response1_affitta = self.client.post(affitta_url, data_affitto, follow=True)
        self.assertEqual(response1_affitta.status_code, 200)
        response1_affitto = self.client.post(affitto_url, data_affitto, follow=True)
        self.assertEqual(response1_affitto.status_code, 200)
        self.assertTrue(AutoListaAffitto.objects.filter(lista_auto_affitto=affitto).exists())

        # Secondo utente (terzo utente) tenta di affittare nello stesso periodo
        user3 = User.objects.create_user(username='utente3', password='testpass')
        UserExtendModel.objects.create(user=user3)
        user3.groups.add(group)
        self.client.logout()
        self.client.login(username='utente3', password='testpass')
        response2 = self.client.post(affitta_url, data_affitto, follow=True)
        self.assertNotEqual(response2.status_code, 200)
        self.assertFalse(AutoListaAffitto.objects.filter(lista_auto_affitto=affitto, data_inizio__date=datetime(2025, 9, 1).date(), affittante=user3.id).exists())

        # Terzo utente affitta in un periodo diverso
        data_affitto2 = {
            'data_inizio': '2025-09-15',
            'data_fine': '2025-09-20',
        }
        response3_affitta = self.client.post(affitta_url, data_affitto2, follow=True)
        self.assertEqual(response3_affitta.status_code, 200)
        response3_affitto = self.client.post(affitto_url, data_affitto2, follow=True)
        self.assertEqual(response3_affitto.status_code, 200)
        self.assertTrue(AutoListaAffitto.objects.filter(lista_auto_affitto=affitto, data_inizio__date=datetime(2025, 9, 15).date(), affittante=user3.id).exists())

        # --- TEST PRENOTAZIONE ---
        # Primo utente prenota l'auto
        self.client.logout()
        self.client.login(username='utente2', password='testpass')
        prenota_url = reverse('Auto:prenota_auto', kwargs={'pk': auto.pk})
        response4 = self.client.post(prenota_url, follow=True)
        self.assertEqual(response4.status_code, 200)
        prenotazione = AutoPrenotazione.objects.filter(auto=auto, prenotante_id=user2.id).last()
        self.assertIsNotNone(prenotazione)
        # Verifica che la durata sia 24 ore
        durata = prenotazione.data_fine - prenotazione.data_inizio
        self.assertEqual(durata.total_seconds(), 24*3600)

        # Terzo utente tenta di prenotare durante la validità della prima
        self.client.logout()
        self.client.login(username='utente3', password='testpass')
        response5 = self.client.post(prenota_url, follow=True)
        self.assertEqual(response5.status_code, 200)
        self.assertFalse(AutoPrenotazione.objects.filter(auto=auto, prenotante_id=user3.id).exists())
