# Autosaloon Modena

Gestione autosalone online sviluppata per il corso di Tecnologie Web.

## Tecnologie e Dipendenze

- **Backend:** Django
- **Frontend:** Bootstrap
- **Database:** SQLite
- **Registrazione utenti:** django-registration
- **Filtri di ricerca:** django-filter
- **Gestione immagini:** Pillow
- **Slug:** django-slugify
- **Task scheduling:** Celery + Redis
- **Messaggistica:** DJango Channels
- **Websockets:** Daphne
- **Gestione /static e /media:** WhiteNoise

## Installazione

1. **Clona il repository**
   ```bash
   git clone <url-repo>
   cd Autosaloon_Modena
   ```

2. **Crea e attiva un ambiente virtuale**
   ```bash
   python -m venv venv
   venv\\Scripts\\activate  # Windows
   # oppure
   source venv/bin/activate  # Linux/Mac
   ```

3. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

4. **Applica le migrazioni**
   ```bash
   python manage.py migrate
   ```

5. **Crea un superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Avvia il server di sviluppo**
   ```bash
   daphne Autosaloon_Modena.asgi:application
   ```

## Task Scheduling

Per la gestione di task periodici (es. scadenze affitti/prenotazioni):

- **Avvia Redis**  
  ```bash
  redis-server.exe
  ```
- **Avvia Celery Beat**  
  ```bash
  celery -A Autosaloon_Modena beat --loglevel=info
  ```
- **Avvia Celery Worker**  
  ```bash
  celery -A Autosaloon_Modena worker --loglevel=info --pool=solo
  ```
  > Su Windows è necessario il parametro `--pool=solo`.

## Struttura del progetto

- `apps/Auto/` — Gestione auto, affitti, vendite, contrattazioni
- `apps/Chat/` — Funzionalità di chat in tempo reale
- `apps/Concessionaria/` — Funzionalità per concessionarie
- `apps/Utente/` — Funzionalità per utenti privati
- `media/` — Cartella per immagini caricate
- `static/` — File statici (CSS, JS, immagini)
- `templates/` — Template HTML

## Note

- Per la privacy e la gestione degli slug viene usato `django-slugify`.
- Per la gestione delle immagini è necessario Pillow.
- Per la registrazione utenti è usato `django-registration`.
- Per i filtri avanzati nelle liste viene usato `django-filter`.

## Autore

- Drusiani (Matricola 177338)

---


