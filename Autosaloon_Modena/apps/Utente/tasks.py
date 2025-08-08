from celery import shared_task
from django.core.management import call_command
import logging

@shared_task
def check_utenti_bannati_task():
    try:
        call_command('check_utente_ban')
        logging.info("Utenti bannati controllati e aggiornati.")
        return "Finito controllo utenti bannati."
    except Exception as e:
        logging.error(f"Errore nella task: {str(e)}")
        return f"Errore: {str(e)}"