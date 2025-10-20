# Dbt transfomration application image
#------------------------------------------------------------------------#

FROM python:3.13.2-slim-bullseye AS dbt-app

#: dbt requires git or there is a warning
RUN apt-get update && apt-get install -y git

COPY requirements.txt /tmp/base.txt

RUN set -x \
	&& pip install --upgrade pip \
	&& pip install -r /tmp/base.txt -f packages \
	&& rm -rf packages \
	&& rm -rf /root/.cache

# TODO: Avoid uisng the root user for safety
RUN mkdir -p home/appuser
WORKDIR /home/appuser/app

COPY ./ ./

CMD ["bash"]