DNSPod DNS Authenticator plugin for Certbot
-------------------------------------------

A certbot dns plugin to obtain certificates using dnspod.


Obtain API Token
================
https://www.dnspod.cn/console/user/security


Install
=======

.. code-block:: bash

    git clone https://github.com/tengattack/certbot-dns-dnspod
    cd certbot-dns-dnspod
    sudo python setup.py install


Credentials File
================

.. code-block:: ini

    certbot_dns_dnspod:dns_dnspod_api_id = 12345
    certbot_dns_dnspod:dns_dnspod_api_token = 1234567890abcdef1234567890abcdef

.. code-block:: bash

    chmod 600 /path/to/credentials.ini


Obtain Certificates
===================

.. code-block:: bash

    certbot certonly -a certbot-dns-dnspod:dns-dnspod \
        --certbot-dns-dnspod:dns-dnspod-credentials /path/to/credentials.ini \
        -d example.com \
        -d "*.example.com"
