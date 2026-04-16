# -*- coding: UTF-8 -*-

import unittest

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch

from migasfree_sdk.api import ApiToken


class TestApiToken(unittest.TestCase):
    """Test suite for ApiToken class."""

    def setUp(self):
        """Set up test environment."""
        self.server = 'migasfree.example.com'
        self.user = 'admin'

    @patch('migasfree_sdk.api.ApiPublic._ui_prompt')
    @patch('os.path.exists')
    @patch('os.chmod')
    @patch('requests.Session.post')
    def test_token_acquisition(self, mock_post, mock_chmod, mock_exists, mock_prompt):
        """Test token acquisition from server."""
        # Scenario: Token doesn't exist locally, must fetch from server
        mock_exists.return_value = False
        mock_prompt.side_effect = ['admin', 'secure_password']

        token_data = {'token': 'secret_token_123'}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = token_data
        mock_post.return_value = mock_response

        with patch('migasfree_sdk.api.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value = MagicMock()

            api = ApiToken(server=self.server, save_token=True)

            self.assertEqual(api.user, 'admin')
            self.assertEqual(
                api.session.headers['authorization'], 'Token secret_token_123'
            )

    @patch('os.path.exists')
    def test_token_from_file(self, mock_exists):
        """Test token loading from local file."""
        # Scenario: Token exists locally
        mock_exists.return_value = True

        with patch('migasfree_sdk.api.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = (
                'cached_token_456'
            )

            api = ApiToken(server=self.server, user='admin')

            self.assertEqual(
                api.session.headers['authorization'], 'Token cached_token_456'
            )

    def test_url_building_token(self):
        """Test URL building for authenticated requests."""
        # Authenticated URL must use /token/ instead of /public/
        with patch('migasfree_sdk.api.ApiToken._manage_token'):
            api = ApiToken(server=self.server, token='test')
            url = api.url('computers')
            self.assertEqual(
                url, 'http://migasfree.example.com/api/v1/token/computers/'
            )


if __name__ == '__main__':
    unittest.main()
