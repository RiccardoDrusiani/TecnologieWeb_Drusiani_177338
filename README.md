# TecnologieWeb_Drusiani_177338
Project of Tecnologie Web. 

TEMPLATE: bootstrap
MEDIA: pillow
DATBASE: sqlite
FRAMEWORK: django-registration
PRIVACY: django-slugify
FILTRO-VER: django-filter
SCHEDULING: celery beat
            Comandi:
                celery-server.exe
                celery -A Autosaloon_Modena beat --loglevel=info
                celery -A Autosaloon_Modena worker --loglevel=info --pool=solo 
                    Quest'ultimo bisogna farlo così perchè altrimendi da problemi