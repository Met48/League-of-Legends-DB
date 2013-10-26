# Quick hack
from copy import deepcopy
import json
import os
import pickle

import yaml

from .file_transactions import FileTransaction
from . import league_sql
from . import league_raf
from . import league_ability
from . import util


def get_db_path(base_path, language='en_US'):
    """Get gameStats database path."""

    return os.path.join(
        util.build_path(base_path),
        "deploy/bin/assets/data/gameStats",  # TODO: Is /bin used on Windows?
        'gameStats_%s.sqlite' % language,
    )


def get_raf_path(base_path):
    return util.build_path(base_path, 'lol_game_client', 'filearchives')


def get_fontconfig_path(base_path, language='en_US'):
    return os.path.join(
        util.build_path(
            base_path,
            'lol_game_client_' + language,
            'managedfiles',
        ),
        "data/menu/fontconfig_%s.txt" % language,
    )


def generate(
        corrections_map,
        db_path,
        raf_path,
        fontconfig_path):
    # Generate new contents
    league = league_sql.generate(db_path, corrections_map)
    league = util.merge(
        league,
        league_raf.generate(
            league,
            raf_path,
            fontconfig_path,
            corrections_map,
        ))
    league = league_ability.fix(league)
    return league


def dump_json(obj):
    return json.dumps(obj, allow_nan=False, separators=(',', ':'))


def dump_pretty_json(obj):
    return json.dumps(obj, sort_keys=True, indent=2, separators=(',', ':'))


def main(
        corrections_path,
        base_path,
        output_name,
        archives_path):
    with FileTransaction(archives_path=archives_path) as transaction:
        # Load corrections
        corrections_file = transaction.open(corrections_path)
        corrections_json = transaction.read(corrections_path)
        if not corrections_json.strip():
            print "No corrections file. Continue?"
            if not util.get_answer():
                return
            corrections_map = {}
        else:
            corrections_map = json.loads(corrections_json)

        league = generate(
            corrections_map=corrections_map,
            db_path=get_db_path(base_path),
            raf_path=get_raf_path(base_path),
            fontconfig_path=get_fontconfig_path(base_path),
        )

        # Create the desired varieties
        league_no_dups = util.fix_aliases(deepcopy(league), remove=True)
        league_with_dups = util.fix_aliases(deepcopy(league), remove=False)

        league_yaml = yaml.safe_dump(league_with_dups)
        league_json_small = dump_json(league_no_dups)
        league_json_full = dump_json(league_with_dups)

        # Open all output files at once
        pickle_file = transaction.open(
            output_name + '.pickle', diff=False, binary=True)
        json_file = transaction.open(output_name + '.part.json')
        json_full_file = transaction.open(output_name + '.full.json')
        yaml_file = transaction.open(output_name + '.yaml')

        # Output changes
        corrections_file.write(dump_pretty_json(corrections_map))
        pickle_file.write(pickle.dumps(league_with_dups))
        json_file.write(league_json_small)
        json_full_file.write(league_json_full)
        yaml_file.write(league_yaml)

        # Confirm with user diff is acceptable
        transaction.diff()
        print "Are diffs acceptable?"
        if not util.get_answer():
            return

        # Write changes
        transaction.complete()
