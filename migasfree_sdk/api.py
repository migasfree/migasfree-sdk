#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2018-2019 Jose Antonio Chavarría <jachavar@gmail.com>
# Copyright (c) 2018-2019 Alberto Gacías <alberto@migasfree.org>
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

import os
import json
import csv
import platform
import subprocess
import requests

import gettext
_ = gettext.gettext

APP_NAME = 'Migasfree SDK'


class ApiToken(object):
    _ok_codes = [
        requests.codes.ok, requests.codes.created,
        requests.codes.moved, requests.codes.found,
        requests.codes.temporary_redirect, requests.codes.resume
    ]
    server = ''
    user = ''
    headers = {'content-type': 'application/json'}
    protocol = 'http'
    proxies = {'http': '', 'https': ''}
    version = 1

    def __init__(self, server='', user='', token='', save_token=False, version=1):
        self.server = server
        if not self.server:
            try:
                from migasfree_client.utils import get_config
                from migasfree_client import settings as client_settings
                config = get_config(client_settings.CONF_FILE, 'client')
                self.server = config.get('server', 'localhost')
            except ImportError:
                self.server = self.get_server()

        self.user = user
        self.version = version
        if token:
            self.set_token(token)
        else:
            if not self.user:
                self.user = self.get_user()

            _token_file = self.token_file()
            if not os.path.exists(_token_file):
                password = self.get_password()
                if password:
                    data = {'username': self.user, 'password': password}
                    r = requests.post(
                        '{0}://{1}/token-auth/'.format(self.protocol, self.server),
                        headers=self.headers,
                        data=json.dumps(data),
                        proxies=self.proxies
                    )
                    if r.status_code in self._ok_codes:
                        self.set_token(r.json()['token'])
                        if save_token:
                            with open(_token_file, 'w') as handle:
                                handle.write(r.json()['token'])
                            if os.name == 'posix':
                                os.chmod(_token_file, 0o400)
                    else:
                        raise Exception(_('Status code {0}').format(r.status_code))
                else:
                    raise Exception(_('Can not continue without password'))
            else:
                with open(_token_file) as handle:
                    self.set_token(handle.read())

    def set_token(self, token):
        self.headers['authorization'] = 'Token {0}'.format(token)

    def url(self, endpoint):
        return '{0}://{1}/api/v{2}/token/{3}/'.format(
            self.protocol, self.server, self.version, endpoint
        )

    def url_id(self, endpoint, id_):
        return '{0}{1}/'.format(self.url(endpoint), id_)

    def paginate(self, endpoint, params=None):
        """GET"""
        return requests.get(
            self.url(endpoint),
            headers=self.headers,
            params=params if params else {},
            proxies=self.proxies
        ).json()

    def post(self, endpoint, data):
        """POST"""
        return requests.post(
            self.url(endpoint),
            headers=self.headers,
            data=json.dumps(data),
            proxies=self.proxies
        )

    def delete(self, endpoint, id_):
        """DELETE (by ID)"""
        return requests.delete(
            self.url_id(endpoint, id_),
            headers=self.headers,
            proxies=self.proxies
        )

    def patch(self, endpoint, id_, data):
        """PATCH (by ID)"""
        return requests.patch(
            self.url_id(endpoint, id_),
            headers=self.headers,
            data=json.dumps(data),
            proxies=self.proxies
        )

    def put(self, endpoint, id_, data):
        """PUT (by ID)"""
        return requests.put(
            self.url_id(endpoint, id_),
            headers=self.headers,
            data=json.dumps(data),
            proxies=self.proxies
        )

    def get(self, endpoint, param=None):
        """
        param can be 'id' or '{}'
        return only one object or exception
        """
        if not param:
            param = {}

        if isinstance(param, int):  # GET ID
            r = requests.get(
                self.url_id(endpoint, param),
                headers=self.headers,
                params={},
                proxies=self.proxies
            )
            if r.status_code in self._ok_codes:
                return r.json()
            else:
                raise Exception(_('Status code {0}').format(r.status_code))
        else:
            r = requests.get(
                self.url(endpoint),
                headers=self.headers,
                params=param,
                proxies=self.proxies
            )
            if r.status_code in self._ok_codes:
                data = r.json()
                if isinstance(data, (list,)) or 'count' not in data:
                    return data
                if data['count'] == 1:
                    return data['results'][0]
                elif data['count'] == 0:
                    raise Exception(_('Not found'))
                else:
                    raise Exception(_('Multiple records found'))
            else:
                raise Exception(_('Status code {0}').format(r.status_code))

    def filter(self, endpoint, params=None):
        """iterator"""
        url = self.url(endpoint)
        while url:
            r = requests.get(
                url,
                headers=self.headers,
                params=params if params else {},
                proxies=self.proxies
            )
            if r.status_code in self._ok_codes:
                data = r.json()
                for element in data['results']:
                    yield element
                url = data['next']

    def add(self, endpoint, data):
        r = self.post(endpoint, data=data)
        if r.status_code == requests.codes.created:
            return r.json()['id']
        else:
            raise Exception(_('Status code {0}').format(r.status_code))

    @staticmethod
    def is_ok(status):
        return status == requests.codes.ok

    @staticmethod
    def is_created(status):
        return status == requests.codes.created

    @staticmethod
    def is_forbidden(status):
        return status == requests.codes.forbidden

    @staticmethod
    def is_zenity():
        cmd = 'which zenity'
        try:
            ret = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, shell=True
            )
        except subprocess.CalledProcessError:
            return False

        return True if ret else False

    @staticmethod
    def is_tty():
        return os.environ.get('DISPLAY', '') == ''

    def id(self, endpoint, params):
        return self.get(endpoint, params)['id']

    @staticmethod
    def get_user_path():
        _platform = platform.system()
        _env = 'HOME'
        if _platform == 'Windows':
            _env = 'USERPROFILE'

        return os.getenv(_env)

    def token_file(self):
        list_server = self.server.split(":")
        server = "_{0}".format(list_server[0])
        if len(list_server) == 2:
            port = "_{0}".format(list_server[1])
        else:
            port = ""

        return os.path.join(
            self.get_user_path(),
            '.migasfree-token_{0}{1}{2}'.format(self.user, server, port)
        )

    def get_server(self):
        cmd = "zenity --title '{0}' --entry --text='{1}:' --entry-text='localhost' 2>/dev/null".format(
            APP_NAME,
            _('Server')
        )
        if self.is_tty() or not self.is_zenity():
            cmd = "dialog --title '{0}' --inputbox '{1}:' 0 0 'localhost' --stdout".format(
                APP_NAME,
                _('Server')
            )
        try:
            server = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, shell=True
            )
        except subprocess.CalledProcessError:
            server = 'localhost'

        return server.replace("\n", "")

    def get_user(self):
        cmd = "zenity --title '{0} @ {1}' --entry --text='{2}:' 2>/dev/null".format(
            APP_NAME,
            self.server,
            _('User')
        )
        if self.is_tty() or not self.is_zenity():
            cmd = "dialog --title '{0} @ {1}' --inputbox '{2}:' 0 0 --stdout".format(
                APP_NAME,
                self.server,
                _('User')
            )
        try:
            user = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, shell=True
            )
        except subprocess.CalledProcessError:
            user = ''

        return user.replace("\n", "")

    def get_password(self):
        title = "{0} {1}".format(APP_NAME, _('Password'))
        text = "{0} {1}@{2}".format(_('Password'), self.user, self.server)
        cmd = "zenity --title '{0}' --entry --hide-text --text '{1}' 2>/dev/null".format(
            title,
            text
        )
        if self.is_tty() or not self.is_zenity():
            cmd = "dialog --title '{0}' --passwordbox '{1}:' 0 0 --stdout".format(
                title,
                text
            )
        try:
            password = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, shell=True
            )
        except subprocess.CalledProcessError:
            password = ''

        return password.replace("\n", "")

    def export_csv(self, endpoint, params=None, fields=None, output='output.csv'):
        def render_line(element_, fields_=None):
            if not fields_:
                fields_ = []
            line = {}
            for keys in fields_:
                x = element_
                for key in keys.split('.'):
                    x = x[key]
                    line[keys] = x

            return line

        writer = None
        with open(output, 'wb') as csv_file:
            if fields:
                writer = csv.DictWriter(csv_file, fieldnames=fields)
                writer.writeheader()
            for element in self.filter(endpoint, params):
                if not fields:
                    fields = element.keys()
                    writer = csv.DictWriter(csv_file, fieldnames=fields)
                    writer.writeheader()
                if writer:
                    writer.writerow(render_line(element, fields))
