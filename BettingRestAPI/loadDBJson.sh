docker-compose exec bettingrestapi python manage.py flush
docker-compose exec bettingrestapi python manage.py migrate
docker-compose exec bettingrestapi python BettingRestAPI/DeleteAllObjects.py
docker-compose exec bettingrestapi python manage.py loaddata db_linux.json
# docker-compose exec bettingrestapi python manage.py loaddata db.json
