#!/bin/sh

set -e

# enviroment substitute
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
ngnix -g 'daemon off;'