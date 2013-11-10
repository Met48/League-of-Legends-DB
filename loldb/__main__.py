"""
Usage:
  loldb stats --path=<path> [options]
  loldb --help
  loldb --version

Options:
  -p, --path=<path>      Location of LoL installation.
  -j, --json=<path>      Location to write json representation to.
  -y, --yaml=<path>      Location to write yaml representation to.

  -f, --force            Continue automatically on warnings.
  -n, --no               Abort automatically on warnings.

  --skip-corrections     Debug option, does not correct champions.
  --skip-validation      Debug option, does not validate output.

  --lang=<language>      Language to output [default: en_US].

  -h, --help             Display this message.
  --version              Display version number.

"""
import os
import sys

import docopt

from . import __version__
from .champion import get_champions
from .convert import (
    format_champion,
    format_item,
    to_json,
    to_yaml,
)
from .correct import correct_champions
from .item import get_items
from .provider import ResourceProvider
from .validate import validate_champions


if sys.version[0] == '3':
    raw_input = input


def main(args):
    if not args['stats']:
        return

    # Validate input path
    path = args['--path']
    if not os.path.isdir(path):
        print('Invalid directory "%s"' % path)
        exit(1)
    if not os.path.isdir(os.path.join(path, 'RADS')):
        print('Not a valid LoL installation, path should contain RADS folder.')
        exit(1)

    if not args['--json'] and not args['--yaml']:
        ask_about_warning('No output format specified, continue?', args)

    provider = ResourceProvider(
        lol_path=path,
        language=args['--lang']
    )
    champions = get_champions(provider)

    if not args['--skip-corrections']:
        correct_champions(champions)

    if not args['--skip-validation']:
        validation_errors = list(validate_champions(champions))
        print('\n'.join(validation_errors))
        print('%d validation errors.' % len(validation_errors))
        if validation_errors:
            ask_about_warning('Validation errors encountered, continue?', args)

    champions = [format_champion(champion) for champion in champions]

    items = get_items(provider)
    items = dict((key, format_item(item)) for key, item in items.items())

    json_path = args['--json']
    if json_path:
        prepare_write_path(json_path)
        with open(json_path, 'w') as f:
            f.write(to_json(champions, items))

    yaml_path = args['--yaml']
    if yaml_path:
        prepare_write_path(yaml_path)
        with open(yaml_path, 'w') as f:
            f.write(to_yaml(champions, items))


def ask_about_warning(warning, args):
    """
    Ask the user if warning is acceptable. If not, exit.

    Will respect options that force a response.
    """
    print(warning)
    if args['--no']:
        result = False
    elif args['--force']:
        result = True
    else:
        result = ask_yes_no()

    if not result:
        print('Aborting')
        exit(1)


def ask_yes_no():
    """Get a yes or no response from the user."""
    while True:
        result = raw_input('Y/N > ').lower()
        if result in ('y', 'yes'):
            return True
        if result in ('n', 'no'):
            return False
        print('Answer Y/N')


def prepare_write_path(path):
    """
    Create missing directories such that path may be opened.

    May raise an exception as it ignores potential race conditions.
    """
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)


if __name__ == '__main__':
    main(docopt.docopt(__doc__, version='LoLDB v%s' % __version__))
