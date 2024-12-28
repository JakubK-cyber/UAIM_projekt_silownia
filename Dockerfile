FROM python:3.14-rc-slim-bookworm

WORKDIR /silownia_api

COPY . /silownia_api

RUN apt-get update && apt-get install -y build-essential libffi-dev libpq-dev

RUN pip install -r requirements.txt
RUN chmod +x /silownia_api/start.sh

EXPOSE 5000

ENTRYPOINT ["sh", "/silownia_api/start.sh"]