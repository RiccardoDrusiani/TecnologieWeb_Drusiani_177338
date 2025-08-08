# TecnologieWeb_Drusiani_177338
Project of Tecnologie Web. 

TEMPLATE: bootstrap, django
MEDIA: pillow
DATBASE: sqlite
FRAMEWORK: django-registration
PRIVACY: django-slugify
FILTRO-VER: django-filter
SCHEDULING: celery beat
            Comandi:
                celery -A Autosaloon_Modena beat --loglevel=info
                celery -A Autosaloon_Modena worker --loglevel=info --pool=solo #Avvio del worker celery, inserire 'solo' er il thread altrimenti su Windows da problemi
SERVER-SCHEDULING: redis
            Comandi:
                redis-server.exe #Avvio del server redis
                