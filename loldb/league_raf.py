# Must run with IronPython
import re

from raf import RAFMaster
from inibin import Inibin
from .util import get_highest_version


def load_fontconfig(fontconfig_path):
    with open(fontconfig_path) as f:
        data = f.read()
    font_config = {}
    for match in re.finditer(r'^tr "([^"]+)" = "(.+)"$', data, re.MULTILINE):
        font_config[match.group(1)] = match.group(2)
    return font_config


def find_inibins(raf_path, pattern):
    """Generator of raf files that match a pattern."""

    rafmaster = RAFMaster(raf_path)
    all_rafs = rafmaster.FileDictFull
    keys = dict(all_rafs).iterkeys()

    for key in keys:
        match = pattern.search(key)
        if not match:
            continue
        raf_entries = all_rafs[key]

        # Get most recent entry
        assert len(raf_entries) > 0
        if len(raf_entries) == 1:
            raf = raf_entries[0]
        else:
            versions = [x.RAFArchive.GetID() for x in raf_entries]
            version = get_highest_version(versions)
            raf = raf_entries[versions.index(version)]

        # Parse data
        raf = bytearray(raf.GetContent())

        if pattern.groups:
            yield tuple(list(match.groups()) + [raf])
        else:
            yield raf


def map_champion_data(inibins, font_config):
    for internal_name, data in inibins:
        mapping = Inibin(data).as_champion(font_config)
        yield internal_name, mapping


def map_by_ids(champions, league):
    champions_to_ids = dict(
        (champion['internal_name'].lower(), champion['id'])
        for champion_id, champion in league['champions'].iteritems()
    )

    for k, v in champions:
        if k in champions_to_ids:
            yield champions_to_ids[k], v


def generate(league, raf_path, fontconfig_path, corrections):
    font_config = load_fontconfig(fontconfig_path)

    champ_inibins = find_inibins(raf_path,
                                 re.compile(r"^data/characters/([^/]+)/\1.inibin$"))
    mappings = map_champion_data(champ_inibins, font_config)
    mappings = map_by_ids(mappings, league)
    mappings = dict(mappings)

    ability_inibins = find_inibins(raf_path,
                                   re.compile(r"^data/(?:characters/[^/]+/)?spells/(.+).inibin$"))
    ability_inibins = dict(ability_inibins)

    # Add ability info to champions
    for champion in mappings.values():
        abilities = champion['abilities']
        for k, name in abilities.items():
            name = name.lower()
            # TODO: Lookup in league
            # if name not in ability_inibins:
            #     name = champion['internal_name'] + name
            if name in ability_inibins:
                # Parse ability
                try:
                    ability = Inibin(ability_inibins[name]).as_ability(font_config)
                except RuntimeError:
                    # TODO: Handle this (probably by updating pyinibin_parser)
                    pass
                else:
                    abilities[k] = {'name': name, 'raw': ability}

    mappings = {
        'champions': mappings
    }

    return mappings
