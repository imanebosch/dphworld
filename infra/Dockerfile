# Infrastructure application image
#------------------------------------------------------------------------#

FROM python:3.13.2-slim-bullseye AS infra-app

RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

RUN npm install -g aws-cdk@2.161.1

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