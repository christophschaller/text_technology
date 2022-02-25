FROM python:3.10-bullseye as python

FROM python as python_builder

RUN apt-get update &&\
    apt-get install libmariadb3 libmariadb-dev

WORKDIR /usr/src/app

RUN python -m venv /usr/src/app/venv
ENV PATH="/usr/src/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python as app

RUN apt-get update &\
    apt-get install libmariadb3 libmariadb-dev

WORKDIR /usr/src/app
COPY --from=python_builder /usr/src/app/venv /usr/src/app/venv
ENV PATH="/usr/src/app/venv/bin:$PATH"

COPY . .

EXPOSE 5000

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]