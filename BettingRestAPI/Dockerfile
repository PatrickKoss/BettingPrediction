FROM python:3.7

WORKDIR /usr/src/BettingRestAPI

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/usr/src/BettingRestAPI
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

EXPOSE 8000
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000"]

# WORKDIR /usr/src/BettingRestAPI/CSGOCrawler/CSGOCrawler/spiders
# CMD [ "python", "MatchesSpider.py" ]
# CMD [ "python", "StatsSpider.py" ]
