# DNSPod DNS Authenticator plugin for Certbot

A certbot dns plugin to obtain certificates using dnspod.


## Obtain API Token
[https://www.dnspod.cn/console/user/security](https://www.dnspod.cn/console/user/security)


## Install

```bash
git clone https://github.com/tengattack/certbot-dns-dnspod
cd certbot-dns-dnspod
sudo python setup.py install
```

If you are using `certbot-auto`, you should run `virtualenv` first:

```bash
# CentOS 7
virtualenv --no-site-packages --python "python2.7" "/opt/eff.org/certbot/venv"
/opt/eff.org/certbot/venv/bin/python2.7 setup.py install
```

## Credentials File
Use your DNSPod account email, use double quoted "ID,Token" as api_token:

```ini
dns_dnspod_email = someone@example.com
dns_dnspod_api_token = "12345,abcdef1234567890abcdef"
```

```bash
chmod 600 /path/to/credentials.ini
```


## Obtain Certificates

```bash
certbot certonly -a dns-dnspod \
    --dns-dnspod-credentials /path/to/credentials.ini \
    -d example.com \
    -d "*.example.com"
```
