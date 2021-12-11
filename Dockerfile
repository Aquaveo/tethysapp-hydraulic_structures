# Use our Tethyscore base docker image as a parent image
FROM aquaveollc/tethysext-atcore:latest

###############################
# DEFAULT ENVIRONMENT VARIABLES
###############################
ENV TETHYS_CLUSTER_IP 172.17.0.1
ENV TETHYS_CLUSTER_USERNAME condor
ENV TETHYS_CLUSTER_PKEY_FILE ${TETHYS_PERSIST}/keys/condorkey
ENV TETHYS_CLUSTER_PKEY_PASSWORD please_dont_use_default_passwords
ENV TETHYS_GS_PROTOCOL http
ENV TETHYS_GS_HOST 172.17.0.1
ENV TETHYS_GS_PORT 8181
ENV TETHYS_GS_PROTOCOL_PUB https
ENV TETHYS_GS_HOST_PUB 172.17.0.1
ENV TETHYS_GS_PORT_PUB 443
ENV TETHYS_GS_USERNAME admin
ENV TETHYS_GS_PASSWORD geoserver
ENV APP_DB_HOST ${TETHYS_DB_HOST}
ENV APP_DB_PORT ${TETHYS_DB_PORT}
ENV APP_DB_USERNAME ${TETHYS_DB_USERNAME}
ENV APP_DB_PASSWORD ${TETHYS_DB_PASSWORD}
ENV CONDORPY_HOME ${TETHYS_HOME}/tethys

#########
# SETUP #
#########
# Speed up APT installs
RUN echo "force-unsafe-io" > /etc/dpkg/dpkg.cfg.d/02apt-speedup \
 && echo "Acquire::http {No-Cache=True;};" > /etc/apt/apt.conf.d/no-cache \
 && echo "Acquire::Check-Valid-Until false;" > /etc/apt/apt.conf.d/no-check-valid
# Install APT Package
RUN apt-get update -qq && apt-get -yqq install gcc libgdal-dev g++ libhdf5-dev > /dev/null
# Quiet pip installs
RUN mkdir -p $HOME/.config/pip && echo "[global]\nquiet = True" > $HOME/.config/pip/pip.conf

###########
# INSTALL #
###########
ADD --chown=www:www tethysapp ${TETHYSAPP_DIR}/tethysapp-hydraulic_structures/tethysapp
ADD --chown=www:www *.py ${TETHYSAPP_DIR}/tethysapp-hydraulic_structures/
ADD *.ini ${TETHYSAPP_DIR}/tethysapp-hydraulic_structures/
ADD *.sh ${TETHYSAPP_DIR}/tethysapp-hydraulic_structures/
ADD install.yml ${TETHYSAPP_DIR}/tethysapp-hydraulic_structures/

RUN /bin/bash -c ". ${CONDA_HOME}/bin/activate tethys \
  ; cd ${TETHYSAPP_DIR}/tethysapp-hydraulic_structures \
  ; python setup.py install"

#########
# CHOWN #
#########
RUN export NGINX_USER=$(grep 'user .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}') \
  ; groupadd -g 2020 hydraulic_structures \
  ; usermod -g 2020 -G ${NGINX_USER} ${NGINX_USER} \
  ; find ${TETHYSAPP_DIR} ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {} \
  ; find ${WORKSPACE_ROOT} ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {} \
  ; find ${STATIC_ROOT} ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {} \
  ; find ${TETHYS_PERSIST}/keys ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {} \
  ; find ${TETHYS_HOME}/tethys ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {}


#########################
# CONFIGURE ENVIRONMENT #
#########################
EXPOSE 80


################
# COPY IN SALT #
################
ADD docker/salt/ /srv/salt/


#######
# RUN #
#######
CMD bash run.sh
