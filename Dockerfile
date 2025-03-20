FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PORT=${PORT}

RUN python manage.py migrate

CMD exec python manage.py runserver 0.0.0.0:$PORT