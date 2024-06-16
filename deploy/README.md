#Запуск и работа с системой (ТРЕБУЕТСЯ ТЕСТИРОВАНИЕ)

1. Отредактировать файл `.env` под свои нужды
2. Отредактировать конфигурационные файлы `config.py`,`gunicorn.conf.py`
3. Запустить команду `docker-compose up -d` дождаться запуска всех контейнеров
4. Подключиться к PosgtreSQL используя данные из файла `.env`, создать базу данных `ship_tracking` и загрузить в неё дамп `dump-ship_tracking.dump` из каталога `dump` (формат custom)
5. Ввести отредактировав под свои нужды команду:
docker exec -it ui_ss superset fab create-admin \
               --username admin \
               --firstname Admin \
               --lastname Admin \
               --email admin@company.ru \
               --password hfFdmID53CJF; \
docker exec -it ui_ss superset db upgrade; \
docker exec -it ui_ss superset init;
6. Ссылки для работы в системе:
 - ip_host:9100 - Superset (логин и пароль в пункте 5 текущего документа)
 - ip_host:9101 - Flower (UI)
 - ip_host:9103 - PostgreSQL
 - ip_host:9104/docs - API
 - ip_host:9105 - Flower (отслеживание работы Celery)
7. Авторизоваться в системе используя данные из пункта 4, в меню «Настройки» выбрать пункт “Database connections” и добавить базу данных “ship_tracking” (PostgreSQL)
7. Перейти в раздел “Datasets” и импортировать из каталога dump датасеты из архива dataset_export_*.zip
8. Перейти в раздел “Charts” и импортировать из каталога dump графики из архива chart_export_*.zip
10. Перейти в раздел “Dashboard” и импортировать из каталога dump дашборд из архива dashboard_export_*.zip
