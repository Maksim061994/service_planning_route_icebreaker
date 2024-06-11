#Запуск и работа с системой (ТРЕБУЕТСЯ ТЕСТИРОВАНИЕ)

1. Отредактировать файл `.env` под свои нужды
2. Отредактировать конфигурационные файлы `config.py`,`gunicorn.conf.py`,`redict.conf`
3. Запустить команду `docker-compose up -d` дождаться запуска всех контейнеров
4. Подключиться к PosgtreSQL используя данные из файла `.env`, создать базу данных `ship_tracking` и загрузить в неё дамп `dump-ship_tracking.dump` (формат custom)
5. Ввести отредактировав под свои нужды команду:
docker exec -it ui_superset superset fab create-admin \
               --username admin \
               --firstname Admin \
               --lastname Admin \
               --email admin@company.ru \
               --password hfFdmID53CJF; \
docker exec -it ui_superset superset db upgrade; \
docker exec -it ui_superset superset init;
6. Ссылки для работы в системе:
 - ip_host:8088 - Superset (логин и пароль в пункте 5 текущего документа)
 - ip_host:3025/docs - API
 - ip_host:5555/dashboard - Flower (отслеживание работы Celery)