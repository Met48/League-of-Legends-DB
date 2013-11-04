"""
Usage:
  loldb --path=<path> [options]
  loldb -h | --help
  loldb --version

Options:
  -p, --path=<path>  Location of LoL installation.
  --lang=<language>  Language to output [default: en_US].

  -h, --help         Display this message.
  --version          Display version number.

"""
import os

import docopt

from . import __version__
from .provider import ResourceProvider
from .champion import get_champions
from .item import get_items


def main(args):
    path = args['--path']
    if not os.path.isdir(path):
        print('Invalid directory "%s"' % path)
    provider = ResourceProvider(
        lol_path=path,
        language=args['--lang']
    )
    champions = get_champions(provider)
    items = get_items(provider)
    # TODO: Save output

if __name__ == '__main__':
    main(docopt.docopt(__doc__, version='LoLDB v%s' % __version__))
