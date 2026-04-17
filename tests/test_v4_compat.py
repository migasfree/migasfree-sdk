# -*- coding: UTF-8 -*-

import unittest
try:
    from unittest.mock import MagicMock, patch, PropertyMock
except ImportError:
    from mock import MagicMock, patch, PropertyMock

from migasfree_sdk.api import ApiPublic

class TestV4Compat(unittest.TestCase):
    """Test suite for legacy v4 compatibility behavior."""

    def setUp(self):
        self.api = ApiPublic(server="migasfree.example.com")

    @patch("migasfree_sdk.api.ApiPublic.is_v5", new_callable=PropertyMock)
    @patch("requests.Session.get")
    def test_get_v4_unwrap(self, mock_get, mock_v5):
        """Test that get() unwraps results in v4 mode."""
        mock_v5.return_value = False
        
        record = {"id": 1, "name": "PC 1"}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"count": 1, "results": [record]}
        mock_get.return_value = mock_response

        # In v4, it should return the record directly
        result = self.api.get("computers")
        self.assertEqual(result, record)

    @patch("migasfree_sdk.api.ApiPublic.is_v5", new_callable=PropertyMock)
    @patch("requests.Session.get")
    def test_get_v4_not_found(self, mock_get, mock_v5):
        """Test that get() raises 'Not found' in v4 mode when count is 0."""
        mock_v5.return_value = False
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"count": 0, "results": []}
        mock_get.return_value = mock_response

        with self.assertRaises(RuntimeError) as cm:
            self.api.get("computers")
        
        # Check message (localized or English)
        self.assertTrue("Not found" in str(cm.exception) or "encontrado" in str(cm.exception))

    @patch("migasfree_sdk.api.ApiPublic.is_v5", new_callable=PropertyMock)
    @patch("requests.Session.get")
    def test_get_v4_multiple(self, mock_get, mock_v5):
        """Test that get() raises 'Multiple records found' in v4 mode when count > 1."""
        mock_v5.return_value = False
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"count": 2, "results": [{"id": 1}, {"id": 2}]}
        mock_get.return_value = mock_response

        with self.assertRaises(RuntimeError) as cm:
            self.api.get("computers")
        
        self.assertTrue("Multiple" in str(cm.exception) or "múltiples" in str(cm.exception))

    @patch("migasfree_sdk.api.ApiPublic.is_v5", new_callable=PropertyMock)
    @patch("requests.Session.get")
    def test_get_v5_raw(self, mock_get, mock_v5):
        """Verify that v5 still returns raw data."""
        mock_v5.return_value = True
        
        data = {"count": 2, "results": [{"id": 1}, {"id": 2}]}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = data
        mock_get.return_value = mock_response

        # In v5, it should return the raw dict
        result = self.api.get("computers")
        self.assertEqual(result, data)
