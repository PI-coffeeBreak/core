FROM python:3.12.9-alpine3.21

WORKDIR /app

RUN apk add --no-cache postgresql-dev inotify-tools libmagic

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY cb.sh /cb.sh
RUN chmod +x /cb.sh

EXPOSE 8080

CMD ["/cb.sh", "start"]
