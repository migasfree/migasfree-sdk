# -*- coding: UTF-8 -*-

# Copyright (c) 2018-2026 Jose Antonio Chavarría <jachavar@gmail.com>
# Copyright (c) 2018-2026 Alberto Gacías <alberto@migasfree.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import csv
import gettext
import json
import os
import platform
import subprocess
import sys

import requests

_ = gettext.gettext

APP_NAME = 'Migasfree SDK'


class ApiPublic(object):
    """Client for interacting with the public Migasfree REST API.

    Attributes:
        session (requests.Session): Persistent session for HTTP requests.
        server (str): Migasfree server hostname.
        version (int): API version to use.
        protocol (str): Protocol (http/https).
    """

    _ok_codes = [
        requests.codes.ok, requests.codes.created,
        requests.codes.moved, requests.codes.found,
        requests.codes.temporary_redirect, requests.codes.resume
    ]
    protocol = 'http'
    version = 1

    def __init__(self, server='', version=1, cert=None, verify=True, debug=False):
        """Initializes the ApiPublic instance.

        Args:
            server (str): Server hostname. If empty, tries to auto-discover.
            version (int): API version. Defaults to 1.
            cert (str/tuple): Path to mTLS cert or (cert, key) tuple.
            verify (bool/str): SSL verification or path to CA bundle.
        """
        self.session = requests.Session()
        self.debug = debug
        self.session.headers.update({'content-type': 'application/json'})
        self.session.proxies = {'http': '', 'https': ''}

        if '://' in server:
            self.protocol, self.server = server.split('://')
        else:
            self.server = server

        if not self.server:
            try:
                from migasfree_client import settings as client_settings
                from migasfree_client.utils import get_config
                config = get_config(client_settings.CONF_FILE, 'client')
                self.server = config.get('server', 'localhost')
            except ImportError:
                self.server = self.get_server()

        if self.debug:
            print('Server: {0}'.format(self.server))

        # mTLS discovery and setup
        if cert is None:
            cert = self._discover_mtls_cert()

        if cert:
            self.session.cert = cert
            self.protocol = 'https'

        if verify is True:
            ca = self._discover_mtls_ca()
            self.session.verify = ca if ca else True
        else:
            self.session.verify = verify

        self.version = version

    def _get_mtls_base_path(self):
        if platform.system() == 'Windows':
            prog_data = os.environ.get('PROGRAMDATA', 'C:\\ProgramData')
            return os.path.join(prog_data, 'migasfree-client', 'mtls')
        return '/var/migasfree-client/mtls'

    def _discover_mtls_cert(self):
        if not self.server:
            return None
        # Sanitize server name for directory
        srv_dir = self.server.replace(':', '_').replace('/', '_')
        base = os.path.join(self._get_mtls_base_path(), srv_dir)
        cert = os.path.join(base, 'cert.pem')
        key = os.path.join(base, 'key.pem')

        if os.path.exists(cert) and os.path.exists(key):
            try:
                # Check readability
                with open(cert, 'r'), open(key, 'r'):
                    return (cert, key)
            except (OSError, IOError):
                pass
        return None

    def _discover_mtls_ca(self):
        if not self.server:
            return None
        srv_dir = self.server.replace(':', '_').replace('/', '_')
        ca = os.path.join(self._get_mtls_base_path(), srv_dir, 'ca.pem')
        if os.path.exists(ca):
            try:
                with open(ca, 'r'):
                    return ca
            except (OSError, IOError):
                pass
        return None

    def _ui_prompt(self, title, text, entry_text='', hide_text=False):
        """Displays an interactive prompt using Zenity or Dialog.

        Args:
            title (str): Window/Box title.
            text (str): Prompt message.
            entry_text (str): Default input value.
            hide_text (bool): If True, mask input (for passwords).

        Returns:
            str: User input or empty string if cancelled.
        """
        if not self._is_tty() and self._is_zenity():
            args = ['zenity', '--title', title, '--entry', '--text', text]
            if entry_text:
                args.extend(['--entry-text', entry_text])
            if hide_text:
                args.append('--hide-text')
        elif platform.system() == 'Windows':
            # Windows fallback using PowerShell + VisualBasic InputBox
            ps_command = (
                "Add-Type -AssemblyName Microsoft.VisualBasic; "
                "[Microsoft.VisualBasic.Interaction]::InputBox('{0}', '{1}', '{2}')"
            ).format(text, title, entry_text)
            args = ['powershell', '-Command', ps_command]
        else:
            args = ['dialog', '--title', title]
            if hide_text:
                args.extend(['--passwordbox', text, '0', '0'])
            else:
                args.extend(['--inputbox', text, '0', '0', entry_text])
            args.append('--stdout')

        try:
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = p.communicate()
            return output.decode('utf-8').strip() if output else ''
        except (OSError, IOError):
            return entry_text

    @staticmethod
    def _is_zenity():
        """Checks if Zenity is installed and available."""
        try:
            p = subprocess.Popen(['zenity', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.communicate()
            return p.returncode == 0
        except (OSError, IOError):
            return False

    @staticmethod
    def _is_tty():
        """Checks if the process is running in a TTY or headless environment."""
        return os.environ.get('DISPLAY', '') == ''

    def url(self, endpoint, id_=None):
        """Builds a complete API URL.

        Args:
            endpoint (str): API resource name (e.g., 'computers').
            id_ (int/str): Optional record ID.

        Returns:
            str: The full URL for the request.
        """
        base = '{0}://{1}/api/v{2}/{3}/{4}/'.format(
            self.protocol, self.server, self.version,
            'token' if isinstance(self, ApiToken) else 'public',
            endpoint
        )
        return '{0}{1}/'.format(base, id_) if id_ is not None else base

    def get(self, endpoint, param=None):
        """Performs a GET request to the API.

        Args:
            endpoint (str): API resource.
            param (int/str/dict): Optional ID for a single record or dict for filters.

        Returns:
            dict/list: The parsed JSON data.

        Raises:
            Exception: If the request fails or returns an error status code.
        """
        params = param if isinstance(param, dict) else {}
        url = self.url(endpoint, id_=param if isinstance(param, int) else None)

        if self.debug:
            print('GET {0}'.format(url))

        try:
            r = self.session.get(url, params=params)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(_('Network error connecting to {0}: {1}').format(url, str(e)))

        if r.status_code in self._ok_codes:
            data = r.json()
            if isinstance(param, int) or isinstance(data, list) or 'count' not in data:
                return data

            if data['count'] == 1:
                return data['results'][0]
            elif data['count'] == 0:
                raise RuntimeError(_('Not found'))
            raise RuntimeError(_('Multiple records found'))

        msg = _('Status code: {0}').format(r.status_code)
        if 'text/html' not in r.headers.get('content-type', ''):
            msg += _(', text: {0}').format(r.text)
        raise RuntimeError(msg)

    def filter(self, endpoint, params=None):
        """Generator for filtered and paginated API requests.

        Args:
            endpoint (str): API resource.
            params (dict): Filters to apply.

        Yields:
            dict: Individual record from the results.
        """
        url = self.url(endpoint)
        while url:
            try:
                r = self.session.get(url, params=params or {})
                if r.status_code not in self._ok_codes:
                    break
                data = r.json()
            except requests.exceptions.RequestException:
                break

            for element in data['results']:
                yield element
            url = data.get('next')
            params = {}  # Clear params for subsequent pages

    def add(self, endpoint, data):
        """Creates a new record (POST).

        Args:
            endpoint (str): API resource.
            data (dict): Data for the new record.

        Returns:
            int/str: The ID of the created record.

        Raises:
            Exception: If creation fails.
        """
        if self.debug:
            print('POST {0}'.format(self.url(endpoint)))
        r = self.session.post(self.url(endpoint), data=json.dumps(data))
        if r.status_code == requests.codes.created:
            return r.json().get('id')
        raise RuntimeError(_('Status code: {0}, text: {1}').format(r.status_code, r.text))

    def post(self, endpoint, data):
        """Performs a generic POST request.

        Args:
            endpoint (str): API resource.
            data (dict): Payload.

        Returns:
            requests.Response: The response object.
        """
        if self.debug:
            print('POST {0}'.format(self.url(endpoint)))
        return self.session.post(self.url(endpoint), data=json.dumps(data))

    def delete(self, endpoint, id_):
        """Deletes a record (DELETE).

        Args:
            endpoint (str): API resource.
            id_ (int/str): Record ID.

        Returns:
            requests.Response: The response object.
        """
        if self.debug:
            print('DELETE {0}'.format(self.url(endpoint, id_=id_)))
        return self.session.delete(self.url(endpoint, id_=id_))

    def patch(self, endpoint, id_, data):
        """Partially updates a record (PATCH).

        Args:
            endpoint (str): API resource.
            id_ (int/str): Record ID.
            data (dict): Partial data to update.

        Returns:
            requests.Response: The response object.
        """
        if self.debug:
            print('PATCH {0}'.format(self.url(endpoint, id_=id_)))
        return self.session.patch(self.url(endpoint, id_=id_), data=json.dumps(data))

    def put(self, endpoint, id_, data):
        """Fully updates a record (PUT).

        Args:
            endpoint (str): API resource.
            id_ (int/str): Record ID.
            data (dict): Full data for the record.

        Returns:
            requests.Response: The response object.
        """
        if self.debug:
            print('PUT {0}'.format(self.url(endpoint, id_=id_)))
        return self.session.put(self.url(endpoint, id_=id_), data=json.dumps(data))

    def get_server(self):
        """Interactive prompt for the server hostname.

        Returns:
            str: Sanitized server hostname.
        """
        return self._ui_prompt(APP_NAME, _('Server'), 'localhost')

    def export_csv(self, endpoint, params=None, fields=None, output='output.csv'):
        """Exports API results to a CSV file.

        Args:
            endpoint (str): API resource.
            params (dict): Filters to apply.
            fields (list): List of field names to include.
            output (str): Path to the output file.
        """
        mode = 'w' if sys.version_info[0] >= 3 else 'wb'
        with open(output, mode) as csv_file:
            writer = None
            for element in self.filter(endpoint, params):
                if not fields:
                    fields = list(element.keys())
                if not writer:
                    writer = csv.DictWriter(csv_file, fieldnames=fields)
                    writer.writeheader()

                row = {}
                for f in fields:
                    val = element
                    for part in f.split('.'):
                        if isinstance(val, dict):
                            val = val.get(part, '')
                        else:
                            val = ''
                            break
                    row[f] = val
                writer.writerow(row)


class ApiToken(ApiPublic):
    """Client for authenticated interactions using Token Authentication."""

    def __init__(self, server='', user='', token='', save_token=False, version=1, debug=False):
        """Initializes ApiToken and handles authentication.

        Args:
            user (str): Username.
            token (str): Direct API token.
            save_token (bool): If True, persist token locally.
            ... (other args inherited)
        """
        super(ApiToken, self).__init__(server, version, debug=debug)
        self.user = user or self._ui_prompt(APP_NAME, _('User'))

        if token:
            self.set_token(token)
        else:
            self._manage_token(save_token)

    def _manage_token(self, save_token):
        """Handles token loading, acquisition, and persistence."""
        token = self.get_token_from_file()

        if token:
            self.set_token(token)
        else:
            password = self._ui_prompt(APP_NAME, _('Password'), hide_text=True)
            if not password:
                raise RuntimeError(_('Can not continue without password'))

            url = '{0}://{1}/token-auth/'.format(self.protocol, self.server)
            payload = json.dumps({'username': self.user, 'password': password})
            try:
                r = self.session.post(url, data=payload)
                if r.status_code in self._ok_codes:
                    token = r.json()['token']
                    self.set_token(token)
                    if save_token:
                        self.save_token_to_file(token)
                else:
                    raise RuntimeError(_('Auth failed: {0}').format(r.text))
            except requests.exceptions.RequestException as e:
                raise RuntimeError(_('Error requesting token: {0}').format(str(e)))

    def set_token(self, token):
        """Sets the authorization header in the session."""
        self.session.headers.update({'authorization': 'Token {0}'.format(token)})

    def get_token_from_file(self):
        """Reads the token from disk with basic error handling."""
        path = self.token_file()
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return f.read().strip()
            except (OSError, IOError):
                return None
        return None

    def save_token_to_file(self, token):
        """Saves the token to disk and sets secure permissions."""
        path = self.token_file()
        try:
            with open(path, 'w') as f:
                f.write(token)
            if os.name == 'posix':
                os.chmod(path, 0o400)
        except (OSError, IOError):
            pass

    def token_file(self):
        """Calculates the absolute path for the token file."""
        srv = self.server.replace(':', '_')
        name = '.migasfree-token_{0}_{1}'.format(self.user, srv)
        home = os.getenv('USERPROFILE' if platform.system() == 'Windows' else 'HOME')
        return os.path.join(home, name)
