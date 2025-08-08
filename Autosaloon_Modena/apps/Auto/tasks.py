from celery import shared_task
from django.core.management import call_command
import logging

@shared_task
def check_auto_disponibilita_task():
    try:
        call_command('check_auto_disponibilita')
        logging.info("Disponibilità auto controllata e aggiornata.")
        call_command('check_auto_in_affitto')
        return "Disponibilità auto controllata e aggiornata."
    except Exception as e:
        logging.error(f"Errore nella task: {str(e)}")
        return f"Errore: {str(e)}"