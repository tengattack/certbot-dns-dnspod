"""Tests for certbot_dns_dnspod.dns_dnspod."""

import os
import unittest

import mock
from requests.exceptions import HTTPError, RequestException

from certbot.plugins import dns_test_common
from certbot.plugins import dns_test_common_lexicon
from certbot.tests import util as test_util

DOMAIN_NOT_FOUND = Exception('No domain found')
GENERIC_ERROR = RequestException
LOGIN_ERROR = HTTPError('400 Client Error: ...')

API_ID = '123'
API_TOKEN = 'bar'


class AuthenticatorTest(test_util.TempDirTestCase,
                        dns_test_common_lexicon.BaseLexiconAuthenticatorTest):

    def setUp(self):
        super(AuthenticatorTest, self).setUp()

        from certbot_dns_dnspod.dns_dnspod import Authenticator

        path = os.path.join(self.tempdir, 'file.ini')
        dns_test_common.write({"dnspod_api_id": API_ID, "dnspod_api_token": API_TOKEN}, path)

        self.config = mock.MagicMock(dnspod_credentials=path,
                                     dnspod_propagation_seconds=0)  # don't wait during tests

        self.auth = Authenticator(self.config, "dnspod")

        self.mock_client = mock.MagicMock()
        # _get_dnspod_client | pylint: disable=protected-access
        self.auth._get_dnspod_client = mock.MagicMock(return_value=self.mock_client)


class DNSPodLexiconClientTest(unittest.TestCase, dns_test_common_lexicon.BaseLexiconClientTest):

    def setUp(self):
        from certbot_dns_dnspod.dns_dnspod import _DNSPodLexiconClient

        self.client = _DNSPodLexiconClient(API_ID, API_TOKEN, 0)

        self.provider_mock = mock.MagicMock()
        self.client.provider = self.provider_mock


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
