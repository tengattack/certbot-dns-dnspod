"""DNS Authenticator for DNSPod DNS."""
import logging

from requests.exceptions import HTTPError
from lexicon.providers import dnspod

from certbot import errors
from certbot.plugins import dns_common
from certbot.plugins import dns_common_lexicon

logger = logging.getLogger(__name__)

ACCOUNT_URL = 'https://www.dnspod.cn/console/user/security'


class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for DNSPod DNS

    This Authenticator uses the DNSPod DNS API to fulfill a dns-01 challenge.
    """

    description = 'Obtain certificates using a DNS TXT record (if you are using DNSPod for DNS).'
    ttl = 600

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=30)
        add('credentials', help='DNSPod credentials INI file.')

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'the DNSPod API.'

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'DNSPod credentials INI file',
            {
                'api-id': 'API ID for DNSPod account, obtained from {0}'.format(ACCOUNT_URL),
                'api-token': 'API Token for DNSPod account, obtained from {0}'
                              .format(ACCOUNT_URL)
            }
        )

    def _perform(self, domain, validation_name, validation):
        self._get_dnspod_client().add_txt_record(domain, validation_name, validation)

    def _cleanup(self, domain, validation_name, validation):
        self._get_dnspod_client().del_txt_record(domain, validation_name, validation)

    def _get_dnspod_client(self):
        return _DNSPodLexiconClient(self.credentials.conf('api-id'),
                                    self.credentials.conf('api-token'),
                                    self.ttl)


class _DNSPodLexiconClient(dns_common_lexicon.LexiconClient):
    """
    Encapsulates all communication with the DNSPod via Lexicon.
    """

    def __init__(self, api_id, api_token, ttl):
        super(_DNSPodLexiconClient, self).__init__()

        self.provider = dnspod.Provider({
            'auth_username': api_id,
            'auth_token': api_token,
            'ttl': ttl,
        })

    def _find_domain_id(self, domain):
        """
        Find the domain_id for a given domain.
        Rewrite certbot/plugins/dns_common_lexicon.py to ensure compatibility
        for Lexicon 2.x and 3.x

        :param str domain: The domain for which to find the domain_id.
        :raises errors.PluginError: if the domain_id cannot be found.
        """

        domain_name_guesses = dns_common.base_domain_name_guesses(domain)

        for domain_name in domain_name_guesses:
            try:
                if hasattr(self.provider, 'options'):
                    # For Lexicon 2.x
                    self.provider.options['domain'] = domain_name
                else:
                    # For Lexicon 3.x
                    self.provider.domain = domain_name

                self.provider.authenticate()

                return  # If `authenticate` doesn't throw an exception, we've found the right name
            except HTTPError as e:
                result = self._handle_http_error(e, domain_name)

                if result:
                    raise result
            except Exception as e:  # pylint: disable=broad-except
                result = self._handle_general_error(e, domain_name)

                if result:
                    raise result

        raise errors.PluginError('Unable to determine zone identifier for {0} using zone names: {1}'
                                 .format(domain, domain_name_guesses))

    def _handle_http_error(self, e, domain_name):
        hint = None
        if str(e).startswith('400 Client Error:'):
            hint = 'Are your API ID and API Token values correct?'
            return errors.PluginError('Error determining zone identifier for {0}: {1}.{2}'
                                  .format(domain_name, e, ' ({0})'.format(hint) if hint else ''))

    def _handle_general_error(self, e, domain_name):
        if not (str(e).startswith('Domain name invalid') or str(e).find('当前域名未添加') >= 0):
            return errors.PluginError('Unexpected error determining zone identifier for {0}: {1}'
                                      .format(domain_name, e))
