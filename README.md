# DNSPod DNS Authenticator plugin for Certbot

A certbot dns plugin to obtain certificates using dnspod.

## Obtain API Token
[https://www.dnspod.cn/console/user/security](https://www.dnspod.cn/console/user/security)

## Install

Pip:

```bash
sudo pip install git+https://github.com/tengattack/certbot-dns-dnspod.git
```

Snap:

```bash
sudo snap install certbot-dns-dnspod
sudo snap set certbot trust-plugin-with-root=ok
sudo snap connect certbot:plugin certbot-dns-dnspod
```

## Credentials File

```ini
dns_dnspod_api_id = 12345
dns_dnspod_api_token = 1234567890abcdef1234567890abcdef
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
