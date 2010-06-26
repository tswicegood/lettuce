# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import sys
from StringIO import StringIO
from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.db import connections

old_names = []
mirrors = []

class LettuceDjangoEnvironment(DjangoTestSuiteRunner):
    def setup_databases(self, conns):
        for alias in conns:
            connection = conns[alias]
            if connection.settings_dict['TEST_MIRROR']:
                mirrors.append((alias, connection))
                mirror_alias = connection.settings_dict['TEST_MIRROR']
                conns._conns[alias] = conns[mirror_alias]
            else:
                name = (connection, connection.settings_dict['NAME'])
                old_names.append(name)
                connection.creation.create_test_db(
                    verbosity=0,
                    autoclobber=False
                )


        return old_names, mirrors

environ = LettuceDjangoEnvironment()
class Manager(object):
    def __init__(self, silenced=True):
        self.silenced = silenced

    def output(self, what, br=False):
        if self.silenced:
            sys.stdout.write(what)
            if br:
                print

    def run_django_command(self, command, **options):
        options['verbosity'] = 0
        old_stderr = sys.stderr
        old_stdout = sys.stdout

        sys.stderr = sys.stdout = StringIO()

        call_command(command, **options)

        sys.stderr = old_stderr
        sys.stdout = old_stdout

    def setup(self, connections=connections):
        environ.setup_test_environment()
        print old_names, mirrors
        try:

            self.output("Setting up a test database...")
            test_db = environ.setup_databases(connections)
            if 'south' in settings.INSTALLED_APPS:
                self.run_django_command('migrate')

            self.run_django_command('loaddata', verbosity=0)
            self.output("OK", True)

        except ImproperlyConfigured, e:
            if "You haven't set the database" in unicode(e):
                # lettuce will be able to test django projects that
                # does not have database
                test_db = None
                self.output(
                    "Ignored (you have not configured your database in setting.py)",
                    True
                )
            else:
                raise e

        return test_db

    def teardown(self, test_db):
        old_stderr = sys.stderr
        old_stdout = sys.stdout

        sys.stderr = sys.stdout = StringIO()

        if test_db:
            try:
                environ.teardown_databases(test_db)
            except:
                pass

        environ.teardown_test_environment()

        sys.stderr = old_stderr
        sys.stdout = old_stdout
