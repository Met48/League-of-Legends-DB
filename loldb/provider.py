import collections
import os
import platform
import re
import sqlite3

import raf


def _get_highest_version(versions):
    versions = [(v, v.split('.')) for v in versions]

    def version_converter(version):
        try:
            parts = map(int, version[1])
        except ValueError:
            return None
        else:
            return [parts, version[0]]

    versions = map(version_converter, versions)
    versions = filter(lambda x: x is not None, versions)
    versions = sorted(versions)

    if not versions:
        raise RuntimeError("No valid version.")

    return versions[-1][1]


def _make_re_pattern(token_str, flags=None):
    """Converts spacing in token_str to variable-length, compiles."""
    return re.compile(r'\s*'.join(token_str.split()), flags)


def _build_path(
        base_path,
        project="lol_air_client",
        subdir='releases',
        version=None):
    """Generate path for most recent release of a project."""

    subdir = subdir.lower()
    path = [base_path, "RADS/projects", project, subdir]

    if subdir != 'filearchives':
        if version is None:
            current_base = os.path.join(*path)
            versions = os.listdir(current_base)
            versions = [v for v in versions if
                        os.path.isdir(os.path.join(current_base, v))]
            version = _get_highest_version(versions)

        path.append(version)

    return os.path.join(*path)


class ResourceProvider(object):
    def __init__(self, lol_path=None, language=None):
        if lol_path is None:
            lol_path = self._get_default_path()
        if language is None:
            language = 'en_US'
        self.base_path = lol_path
        self.language = language
        self.db = None
        self.raf = None
        self.font_config = None

    def _get_default_path(self):
        raise NotImplementedError()

    def _get_db_path(self):
        raise NotImplementedError()

    def _get_raf_path(self):
        return _build_path(
            self.base_path,
            'lol_game_client',
            'filearchives'
        )

    def get_db(self):
        """Get connection to gameStats database."""
        if self.db is None:
            self.db = sqlite3.connect(self._get_db_path())
        return self.db

    def get_db_query(self, query):
        """Get the rows from a gameStats database query."""
        connection = self.get_db()
        cursor = connection.cursor()
        # execute doesn't accept a parametrized table name
        rows = cursor.execute(query)

        # Get column names from cursor
        columns = [c[0] for c in cursor.description]
        row_class = collections.namedtuple('Row', columns)

        for row in rows:
            row = row_class(*row)
            yield row

    def get_db_rows(self, table):
        """Get the rows from a gameStats database table."""
        return self.get_db_query("SELECT * FROM `%s`" % table)

    def get_raf_master(self):
        """Get RAFMaster instance for game client."""
        if self.raf is None:
            self.raf = raf.RAFMaster(self._get_raf_path())
        return self.raf

    def get_font_config(self):
        """Get font_config dictionary."""
        if self.font_config is None:
            archive = self.get_raf_master()
            font_config = {}
            font_config_text = archive.find(name='fontconfig_en_US.txt').read()
            font_config_re = _make_re_pattern('^ tr "([^"]+)" = "(.+)" $', re.M)
            for match in font_config_re.finditer(font_config_text):
                font_config[match.group(1)] = match.group(2)
            self.font_config = font_config
        return self.font_config


class MacResourceProvider(ResourceProvider):
    def _get_default_path(self):
        return '/Applications/League of Legends.app/Contents/LOL'

    def _get_db_path(self):
        return os.path.join(
            _build_path(self.base_path),
            'deploy/bin/assets/data/gameStats',
            'gameStats_%s.sqlite' % self.language,
        )


class WindowsResourceProvider(ResourceProvider):
    def _get_default_path(self):
        return 'C:/Riot Games/League of Legends/'

    def _get_db_path(self):
        return os.path.join(
            _build_path(self.base_path),
            'deploy/assets/data/gameStats',
            'gameStats_%s.sqlite' % self.language,
        )


def get_provider_class(system=None):
    if system is None:
        system = platform.system()
        if system == 'Windows':
            system = 'win'
        elif system == 'Darwin':
            system = 'mac'
        else:
            system = None
    if system == 'win':
        return WindowsResourceProvider
    elif system == 'mac':
        return MacResourceProvider
    else:
        raise RuntimeError('Unable to determine operating system.')
