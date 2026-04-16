# -*- coding: UTF-8 -*-

import unittest

try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock

from migasfree_sdk.api import ApiPublic


class TestApiPublic(unittest.TestCase):
    def setUp(self):
        self.server = "migasfree.example.com"
        self.api = ApiPublic(server=self.server)

    def test_url_building(self):
        # Public URL
        url = self.api.url("projects")
        self.assertEqual(url, "http://migasfree.example.com/api/v1/public/projects/")

        # Public URL with ID
        url = self.api.url("projects", id_=123)
        self.assertEqual(
            url, "http://migasfree.example.com/api/v1/public/projects/123/"
        )

    @patch("requests.Session.get")
    def test_get_list(self, mock_get):
        mock_data = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"id": 1, "name": "Project 1"}],
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        result = self.api.get("projects")
        self.assertEqual(result, mock_data["results"][0])

    @patch("os.path.exists")
    @patch("platform.system")
    def test_mtls_discovery(self, mock_system, mock_exists):
        mock_system.return_value = "Linux"

        def side_effect(path):
            return any(x in path for x in ["cert.pem", "key.pem", "ca.pem"])

        mock_exists.side_effect = side_effect

        with patch("migasfree_sdk.api.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value = MagicMock()

            api = ApiPublic(server=self.server)

            self.assertEqual(api.protocol, "https")
            self.assertIsNotNone(api.session.cert)
            self.assertTrue(api.session.verify.endswith("ca.pem"))

    @patch("subprocess.Popen")
    def test_safe_ui_prompt(self, mock_popen):
        mock_p = MagicMock()
        mock_p.communicate.return_value = (b"user_input\n", b"")
        mock_popen.return_value = mock_p

        result = self.api._ui_prompt("Title", "Text", entry_text="default")

        self.assertEqual(result, "user_input")
        args, kwargs = mock_popen.call_args
        self.assertIsInstance(args[0], list)
        self.assertNotIn("shell", kwargs)

    @patch("migasfree_sdk.api.ApiPublic.filter")
    def test_export_csv(self, mock_filter):
        mock_filter.return_value = iter(
            [
                {"id": 1, "name": "PC 1", "project": {"name": "P1"}},
                {"id": 2, "name": "PC 2", "project": {"name": "P2"}},
            ]
        )

        output_file = "test_output.csv"
        fields = ["id", "name", "project.name"]

        with patch("migasfree_sdk.api.open", create=True) as mock_open:
            self.api.export_csv("computers", fields=fields, output=output_file)
            mock_open.assert_called_once()

    @patch("requests.Session.get")
    def test_error_404(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_get.return_value = mock_response

        with self.assertRaises(Exception) as cm:
            self.api.get("projects", param=999)
        # Check for error code 404, agnostic to translation
        self.assertIn("404", str(cm.exception))
        self.assertIn("Not found", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
