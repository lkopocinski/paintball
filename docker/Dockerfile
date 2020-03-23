FROM python:3.8-buster
LABEL maintainer="Łukasz Kopocinski <lkopocinski@gmail.com>"


# installing graph tool
RUN echo "deb http://downloads.skewed.de/apt/buster buster main" >> /etc/apt/sources.list && \
    echo "deb-src http://downloads.skewed.de/apt/buster buster main" >> /etc/apt/sources.list && \
    apt-key adv --keyserver keys.openpgp.org --recv-key 612DEFB798507F25 && \
    apt update && apt install -y python3-graph-tool


ENV PIP_EXTRA_INDEX_URL "https://pypi.clarin-pl.eu/"
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
