"""
Usage:
  loldb --path=<path> [options]
  loldb -h | --help
  loldb --version

Options:
  -p, --path=<path>  Location of LoL installation.
  -o, --out=<path>   File path to save json representation.
  --lang=<language>  Language to output [default: en_US].

  -h, --help         Display this message.
  --version          Display version number.

"""
import json
import os

import docopt

from . import __version__
from .champion import get_champions
from .converter import (
    format_champion,
    format_item,
)
from .correct import correct_champions
from .item import get_items
from .provider import ResourceProvider
from .validate import validate_champions


class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return list(o)
        return super(Encoder, self).default(o)


def main(args):
    path = args['--path']
    if not os.path.isdir(path):
        print('Invalid directory "%s"' % path)
    output_path = args['--out']
    provider = ResourceProvider(
        lol_path=path,
        language=args['--lang']
    )
    champions = get_champions(provider)
    correct_champions(champions)
    print('\n'.join(validate_champions(champions)))
    champions = map(format_champion, champions)

    items = get_items(provider)
    items = dict(zip(items.keys(), map(format_item, items.values())))

    output = {
        'champions': champions,
        'items': items,
    }
    output = json.dumps(output, cls=Encoder)
    if output_path is not None:
        with open(args['--out'], 'w') as f:
            f.write(output)
    else:
        print(output)

if __name__ == '__main__':
    main(docopt.docopt(__doc__, version='LoLDB v%s' % __version__))
