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


def get_answer(question, args):
    if args['--force']:
        return True
    if args['--no']:
        return False

    print(question)

    while True:
        result = raw_input('Y/N > ').lower()
        if result in ('y', 'yes'):
            return True
        if result in ('n', 'no'):
            return False
        print('Answer Y/N')


def main(args):
    if not args['stats']:
        return

    # Validate input path
    path = args['--path']
    if not os.path.isdir(path):
        print('Invalid directory "%s"' % path)
    if not os.path.isdir(os.path.join(path, 'RADS')):
        print('Not a valid LoL installation, there should be a RADS folder present.')

    if not args['--json'] and not args['--yaml']:
        if not get_answer('No output format specified, continue?', args):
            print('Aborting.')
            return

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
            if not get_answer('Validation errors encountered, continue?', args):
                print('Aborting.')
                return

    champions = [format_champion(champion) for champion in champions]

    items = get_items(provider)
    items = dict((key, format_item(item)) for key, item in items.items())

    if args['--json']:
        with open(args['--json'], 'w') as f:
            f.write(to_json(champions, items))

    if args['--yaml']:
        with open(args['--yaml'], 'w') as f:
            f.write(to_yaml(champions, items))

if __name__ == '__main__':
    main(docopt.docopt(__doc__, version='LoLDB v%s' % __version__))
