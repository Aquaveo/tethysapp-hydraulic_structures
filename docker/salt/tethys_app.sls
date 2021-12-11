{% set ALLOWED_HOST = salt['environ.get']('ALLOWED_HOST') %}
{% set CONDA_HOME = salt['environ.get']('CONDA_HOME') %}
{% set CONDA_ENV_NAME = salt['environ.get']('CONDA_ENV_NAME') %}
{% set TETHYS_HOME = salt['environ.get']('TETHYS_HOME') %}
{% set TETHYS_BIN_DIR = [CONDA_HOME, "/envs/", CONDA_ENV_NAME, "/bin"]|join %}
{% set TETHYS_PERSIST = salt['environ.get']('TETHYS_PERSIST') %}
{% set TETHYSAPP_DIR = salt['environ.get']('TETHYSAPP_DIR') %}
{% set APP_DB_HOST = salt['environ.get']('APP_DB_HOST') %}
{% set APP_DB_PASSWORD = salt['environ.get']('APP_DB_PASSWORD') %}
{% set APP_DB_PORT = salt['environ.get']('APP_DB_PORT') %}
{% set APP_DB_USERNAME = salt['environ.get']('APP_DB_USERNAME') %}

{% set TETHYS_GS_HOST = salt['environ.get']('TETHYS_GS_HOST') %}
{% set TETHYS_GS_PASSWORD = salt['environ.get']('TETHYS_GS_PASSWORD') %}
{% set TETHYS_GS_PORT = salt['environ.get']('TETHYS_GS_PORT') %}
{% set TETHYS_GS_USERNAME = salt['environ.get']('TETHYS_GS_USERNAME') %}
{% set TETHYS_GS_PROTOCOL = salt['environ.get']('TETHYS_GS_PROTOCOL') %}
{% set TETHYS_GS_HOST_PUB = salt['environ.get']('TETHYS_GS_HOST_PUB') %}
{% set TETHYS_GS_PORT_PUB = salt['environ.get']('TETHYS_GS_PORT_PUB') %}
{% set TETHYS_GS_PROTOCOL_PUB = salt['environ.get']('TETHYS_GS_PROTOCOL_PUB') %}
{% set TETHYS_CLUSTER_IP = salt['environ.get']('TETHYS_CLUSTER_IP') %}
{% set TETHYS_CLUSTER_USERNAME = salt['environ.get']('TETHYS_CLUSTER_USERNAME') %}
{% set TETHYS_CLUSTER_PKEY_FILE = salt['environ.get']('TETHYS_CLUSTER_PKEY_FILE') %}
{% set TETHYS_CLUSTER_PKEY_PASSWORD = salt['environ.get']('TETHYS_CLUSTER_PKEY_PASSWORD') %}
{% set FILE_UPLOAD_MAX_MEMORY_SIZE = salt['environ.get']('FILE_UPLOAD_MAX_MEMORY_SIZE') %}

{% set PS_SERVICE_NAME = 'tethys_postgis' %}
{% set GS_SERVICE_NAME = 'tethys_geoserver' %}


Pre_HYDRAULICSTRUCTURES_Settings:
  cmd.run:
    - name: cat {{ TETHYS_HOME }}/portal_config.yml
    - shell: /bin/bash

Generate_Tethys_Settings_HYDRAULICSTRUCTURES:
  cmd.run:
    - name: >
        {{ TETHYS_BIN_DIR }}/tethys settings
        --set FILE_UPLOAD_MAX_MEMORY_SIZE {{ FILE_UPLOAD_MAX_MEMORY_SIZE }}
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/hydraulic_structures_setup_complete" ];"

Sync_Apps:
  cmd.run:
    - name: . {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && tethys db sync
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/hydraulic_structures_setup_complete" ];"

Remove_Persistent_Stores_Database:
  cmd.run:
    - name: . {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && tethys services remove persistent {{ PS_SERVICE_NAME }} -f
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/hydraulic_structures_setup_complete" ];"

Create_Persistent_Stores_Database:
  cmd.run:
    - name: ". {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && tethys services create persistent -n {{ PS_SERVICE_NAME }} -c {{ APP_DB_USERNAME }}:{{ APP_DB_PASSWORD }}@{{ APP_DB_HOST }}:{{ APP_DB_PORT }}"
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/hydraulic_structures_setup_complete" ];"

Remove_Schedulers:
  cmd.run:
    - name: ". {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && tethys schedulers remove -f remote_cluster"
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/hydraulic_structures_setup_complete" ];"

Create_Schedulers:
  cmd.run:
    - name: ". {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && tethys schedulers create-condor -n remote_cluster -e ${TETHYS_CLUSTER_IP} -u ${TETHYS_CLUSTER_USERNAME} -f ${TETHYS_CLUSTER_PKEY_FILE} -k ${TETHYS_CLUSTER_PKEY_PASSWORD}"
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/hydraulic_structures_setup_complete" ];"

Remove_Spatial_Dataset_Service:
  cmd.run:
    - name: . {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && tethys services remove spatial {{ GS_SERVICE_NAME }} -f
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/hydraulic_structures_setup_complete" ];"

Create_Spatial_Dataset_Service:
  cmd.run:
    - name: ". {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && tethys services create spatial -n {{ GS_SERVICE_NAME }} -c {{ TETHYS_GS_USERNAME }}:{{ TETHYS_GS_PASSWORD }}@{{ TETHYS_GS_PROTOCOL }}://{{ TETHYS_GS_HOST }}:{{ TETHYS_GS_PORT }} -p {{ TETHYS_GS_PROTOCOL_PUB }}://{{ TETHYS_GS_HOST_PUB }}:{{ TETHYS_GS_PORT_PUB }}"
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/hydraulic_structures_setup_complete" ];"

Link_Persistent_Stores_Database:
  cmd.run:
    - name: ". {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && tethys link persistent:{{ PS_SERVICE_NAME }} hydraulic_structures:ps_database:primary_db"
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/hydraulic_structures_setup_complete" ];"

Link_Spatial_Dataset_Service:
  cmd.run:
    - name: ". {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && tethys link spatial:{{ GS_SERVICE_NAME }} hydraulic_structures:ds_spatial:primary_geoserver"
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/hydraulic_structures_setup_complete" ];"

Sync_App_Persistent_Stores:
  cmd.run:
    - name: . {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && tethys syncstores all
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/hydraulic_structures_setup_complete" ];"

Init_HYDRAULICSTRUCTURES:
  cmd.run:
    - name: ". {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && hydraulic_structures init {{ TETHYS_GS_PROTOCOL }}://{{ TETHYS_GS_USERNAME }}:{{ TETHYS_GS_PASSWORD }}@{{ TETHYS_GS_HOST }}:{{ TETHYS_GS_PORT }}/geoserver/rest/"
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/hydraulic_structures_setup_complete" ];"

Make_Key_Directory:
  cmd.run:
    - name: mkdir -p {{ TETHYS_PERSIST }}/keys
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/hydraulic_structures_setup_complete" ];"

Copy_Condor_Key:
  cmd.run:
    - name: ls /tmp/keys && cp /tmp/keys/condorkey-root ${TETHYS_CLUSTER_PKEY_FILE} && chown www ${TETHYS_CLUSTER_PKEY_FILE}
    - shell: /bin/bash
    - onlyif: /bin/bash -c "[ -f "/tmp/keys/condorkey-root" ];"
    - unless: /bin/bash -c "[ -f "${TETHYS_CLUSTER_PKEY_FILE}" ];"

Set_Tethys_Persist_Permissions:
  cmd.run:
    - name: chown -R :2020 {{ TETHYS_PERSIST }} && chmod -R g+rwx {{ TETHYS_PERSIST }}
    - shell: /bin/bash
    - unless: /bin/bash -c "[ $(find "${TETHYS_PERSIST}" -maxdepth 1 -group 2020 | wc -l) -ne 0 ];"

Flag_Complete_Setup:
  cmd.run:
    - name: touch ${TETHYS_PERSIST}/hydraulic_structures_setup_complete
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "${TETHYS_PERSIST}/hydraulic_structures_setup_complete" ];"