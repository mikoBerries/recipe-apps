# used for proxy server nginx

FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="mikoberries.com"


COPY ./default.conf.tlp /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

# env for proxy
ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

# as root user
USER root
RUN mkdir -p /vol/static && \
    chmod 755 /vol/static && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /rn.sh

VOLUME [ "/vol/static" ]

# as nginx user
USER nginx
CMD [ "/run.sh" ]