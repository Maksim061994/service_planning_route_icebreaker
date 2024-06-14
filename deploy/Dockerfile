FROM apache/superset:3.1.2
USER root

RUN apt-get update && \
	apt-get install -y wget zip unzip tar nano telnet curl mc lsof htop firefox-esr
ENV GECKODRIVER_VERSION=0.34.0
RUN wget -q https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    tar -x geckodriver -zf geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz -O > /usr/bin/geckodriver && \
    chmod 755 /usr/bin/geckodriver && \
    rm geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
	wget -q https://mirror.cs.uchicago.edu/google-chrome/pool/main/g/google-chrome-stable/google-chrome-stable_102.0.5005.115-1_amd64.deb && \
    apt-get install -y --no-install-recommends ./google-chrome-stable_102.0.5005.115-1_amd64.deb && \
    rm -f google-chrome-stable_102.0.5005.115-1_amd64.deb && \
    wget -q https://chromedriver.storage.googleapis.com/102.0.5005.61/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/bin && \
    chmod 755 /usr/bin/chromedriver && \
    rm -f chromedriver_linux64.zip && \
    pip install --no-cache --upgrade pip setuptools && \
    pip install --no-cache --no-deps clickhouse-connect clickhouse-driver clickhouse-sqlalchemy flower==2.0.1 prometheus-client==0.20.0 tornado==6.4.0 lz4 zstandard asynch tzlocal google celery[redis] leb128 zstd ciso8601
USER superset