FROM python:3.12.9-alpine3.21

WORKDIR /app

RUN apk add --no-cache inotify-tools libmagic postgresql-dev curl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN chmod 500 cb.sh \
    && addgroup -S user \
    && adduser -S user -G user \
    && chown -R user:user /app

USER user

EXPOSE 8080

CMD ["./cb.sh", "start"]
