from django.test import TestCase
from django.urls import reverse
from apps.Auto.models import Auto
from apps.Auto.models import AutoContrattazione
from apps.Chat.models import ChatRoom, Message
from apps.Utente.models import UserExtendModel
from django.contrib.auth.models import User

class FlussoCompletoViewTest(TestCase):
    def setUp(self):
        self.client = self.client_class()
        self.user1_data = {
            'username': 'utente1',
            'email': 'utente1@email.it',
            'password': 'pass1',
            'first_name': 'Mario',
            'last_name': 'Rossi'
        }
        self.user2_data = {
            'username': 'utente2',
            'email': 'utente2@email.it',
            'password': 'pass2',
            'first_name': 'Luigi',
            'last_name': 'Bianchi'
        }
        self.auto1_data = {
            'marca': 'Fiat',
            'modello': 'Panda',
            'cilindrata': 1200,
            'carburante': 0,
            'cambio': 0,
            'trazione': 0,
            'anno': 2020,
            'disponibilita': 2,
            'chilometraggio': 10000,
            'descrizione': 'Auto di utente1',
            'prezzo_vendita': 8000,
            'prezzo_affitto': 50
        }
        self.auto2_data = {
            'marca': 'Toyota',
            'modello': 'Yaris',
            'cilindrata': 1000,
            'carburante': 1,
            'cambio': 1,
            'trazione': 1,
            'anno': 2021,
            'disponibilita': 2,
            'chilometraggio': 5000,
            'descrizione': 'Auto di utente2',
            'prezzo_vendita': 12000,
            'prezzo_affitto': 60
        }

    def test_flusso_completo_view(self):
        # 1. Registrazione utente1
        response = self.client.post('/Utente/register/', self.user1_data)
        print(response.status_code)
        self.assertEqual(response.status_code, 302, "Registrazione utente1 fallita")
        # 2. Login utente1
        response = self.client.post('/Utente/login/', {'username': 'utente1', 'password': 'pass1'})
        print(response.status_code)
        self.assertIn(response.status_code, [200, 302], "Login utente1 fallito")
        # 3. Creazione auto utente1
        response = self.client.post('/Auto/add/', self.auto1_data)
        print(response.status_code)
        self.assertIn(response.status_code, [200, 302], "Creazione auto utente1 fallita")
        # 4. Logout utente1
        response = self.client.post('/Utente/logout/')
        print(response.status_code)
        self.assertIn(response.status_code, [200, 302], "Logout utente1 fallito")
        # 5. Registrazione utente2
        response = self.client.post('/Utente/register/', self.user2_data)
        print(response.status_code)
        self.assertEqual(response.status_code, 302, "Registrazione utente2 fallita")
        # 6. Login utente2
        response = self.client.post('/Utente/login/', {'username': 'utente2', 'password': 'pass2'})
        print(response.status_code)
        self.assertIn(response.status_code, [200, 302], "Login utente2 fallito")
        # 7. Creazione auto utente2
        response = self.client.post('/Auto/add/', self.auto2_data)
        print(response.status_code)
        self.assertIn(response.status_code, [200, 302], "Creazione auto utente2 fallita")
        # 8. Logout utente2
        response = self.client.post('/Utente/logout/')
        print(response.status_code)
        self.assertIn(response.status_code, [200, 302], "Logout utente2 fallito")
        # 9. Login utente1
        response = self.client.post('/Utente/login/', {'username': 'utente1', 'password': 'pass1'})
        print(response.status_code)
        self.assertIn(response.status_code, [200, 302], "Login utente1 fallito dopo logout")
        # 10. Contrattazione auto di utente2 (4/5 offerte)
        auto2_pk = Auto.objects.filter(modello='Yaris').first().pk
        contrattazione_pk = None
        response = self.client.post(f'/Auto/{auto2_pk}/contrattazione/', {'prezzo_attuale': 100, 'stato': 1})
        print(response.status_code)
        self.assertIn(response.status_code, [200, 302], f"INizio contrattazione auto2 fallita")
        # Recupera la contrattazione appena creata/aggiornata
        contrattazione_obj = AutoContrattazione.objects.filter(auto_id=auto2_pk).order_by('-id').first()
        contrattazione_pk = contrattazione_obj.pk if contrattazione_obj else None
        response = self.client.post('/Utente/logout/')
        print(response.status_code)
        for i in range(5):
            response = self.client.post('/Utente/login/', {'username': 'utente2', 'password': 'pass2'})
            print(response.status_code)
            self.assertIn(response.status_code, [200, 302], f"Login utente2 step {i} fallito")
            # Usa il pk della contrattazione per l'update
            if contrattazione_pk:
                response = self.client.post(f'/Auto/offerta/{contrattazione_pk}/update/', {'prezzo_attuale': 20000 - i, 'stato': 2})
                print(response.status_code)
                self.assertIn(response.status_code, [200, 302], f"Offerta update contrattazione step {i} fallita")
            response = self.client.post('/Utente/logout/')
            print(response.status_code)
            response = self.client.post('/Utente/login/', {'username': 'utente1', 'password': 'pass1'})
            print(response.status_code)
            self.assertIn(response.status_code, [200, 302], f"Login utente1 step {i} fallito")
            if contrattazione_pk:
                response = self.client.post(f'/Auto/offerta/{contrattazione_pk}/update/', {'prezzo_attuale': 100 - i, 'stato': 2})
                print(response.status_code)
                self.assertIn(response.status_code, [200, 302], f"Offerta update contrattazione step {i} fallita")
            response = self.client.post('/Utente/logout/')
            print(response.status_code)
        # 11. Annulla contrattazione
        contrattazione_obj = AutoContrattazione.objects.filter(auto_id=auto2_pk).first()
        if contrattazione_obj:
            response = self.client.post(f'/Auto/{contrattazione_obj.pk}/contrattazione/fallita/')
            print(response.status_code)
            self.assertIn(response.status_code, [200, 302], "Annulla contrattazione fallita")
        response = self.client.post('/Utente/logout/')
        print(response.status_code)
        # 12. Login utente2
        response = self.client.post('/Utente/login/', {'username': 'utente2', 'password': 'pass2'})
        print(response.status_code)
        self.assertIn(response.status_code, [200, 302], "Login utente2 dopo contrattazione fallito")
        # 13. Prenotazione auto di utente1
        auto1_pk = Auto.objects.filter(modello='Panda').first().pk
        response = self.client.post(f'/Auto/{auto1_pk}/prenota/', {'data_inizio': '2025-09-11', 'data_fine': '2025-09-12'})
        print(response.status_code)
        self.assertIn(response.status_code, [200, 302], "Prenotazione auto1 fallita")
        # 14. Annulla prenotazione
        response = self.client.post(f'/Auto/{auto1_pk}/annulla-prenotazione/')
        print(response.status_code)
        self.assertIn(response.status_code, [200, 302], "Annulla prenotazione auto1 fallita")
        response = self.client.post('/Utente/logout/')
        print(response.status_code)
        # 15. Login utente1
        response = self.client.post('/Utente/login/', {'username': 'utente1', 'password': 'pass1'})
        print(response.status_code)
        self.assertIn(response.status_code, [200, 302], "Login utente1 dopo prenotazione fallito")
        # 16. Affitta auto di utente2
        response = self.client.post(f'/Auto/{auto2_pk}/affitto/', {'data_inizio': '2025-09-13', 'data_fine': '2025-09-14'})
        print(response.status_code)
        self.assertIn(response.status_code, [200, 302], "Affitto auto2 fallito")
        # 17. Verifica che entrambi abbiano almeno un'auto
        response = self.client.get('/Auto/user-autos/')
        print(response.status_code)
        self.assertIn(response.status_code, [200, 302], "Visualizzazione auto utente fallita")
        self.assertEqual(Auto.objects.filter(user_auto__username='utente1').count(), 1, "Utente1 non ha un'auto")
        self.assertEqual(Auto.objects.filter(user_auto__username='utente2').count(), 1, "Utente2 non ha un'auto")
        # 18. Verifica che esistano chat tra i due utenti
        response = self.client.get('/chat/')
        print(response.status_code)
        self.assertFalse(response.status_code in [301, 302], "La view Chat ha restituito un redirect invece di una pagina.")
        self.assertIsNotNone(getattr(response, 'context', None), "La risposta non ha un contesto.")
        self.assertIn('chats', response.context, "La chiave 'chats' non è presente nel contesto della view Chat.")
        chat_list = response.context['chats']
        self.assertTrue(any((c.user_1.username == 'utente1' and c.user_2.username == 'utente2') or (c.user_1.username == 'utente2' and c.user_2.username == 'utente1') for c in chat_list), "Non esistono chat tra utente1 e utente2")
