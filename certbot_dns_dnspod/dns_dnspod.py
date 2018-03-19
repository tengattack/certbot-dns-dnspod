"""DNS Authenticator for DNSPod DNS."""
import logging

import zope.interface
from lexicon.providers import dnspod
from tld import get_tld

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common
from certbot.plugins import dns_common_lexicon

logger = logging.getLogger(__name__)

ACCOUNT_URL = 'https://www.dnspod.cn/console/user/security'


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
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
        tld_domain = get_tld(domain, fix_protocol=True)
        self._get_dnspod_client().add_txt_record(tld_domain, validation_name, validation)

    def _cleanup(self, domain, validation_name, validation):
        tld_domain = get_tld(domain, fix_protocol=True)
        self._get_dnspod_client().del_txt_record(tld_domain, validation_name, validation)

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

    def _handle_http_error(self, e, domain_name):
        hint = None
        if str(e).startswith('400 Client Error:'):
            hint = 'Are your API ID and API Token values correct?'

        return errors.PluginError('Error determining zone identifier for {0}: {1}.{2}'
                                  .format(domain_name, e, ' ({0})'.format(hint) if hint else ''))
