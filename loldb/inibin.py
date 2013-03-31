"""
A reader for the inibin file format.

One function, read_inibin, is exported for use. It will read the file buffer,
parse the inibin, and map the inibin keys to have human-readable names.

Champion and ability inibins are supported.
"""

import StringIO
import struct

__ALL__ = ['read_inibin']


MULT_5 = lambda x: x * 5

KEY_MAPPING = {
    # Inibins use numeric keys - this maps the keys to human-readable names

    'character': {
        # Unused:
        # 'tags': -148652351,  # Comma-delimited
        # 'lore': -51751813,
        # 'name': 82690155,
        # 'desc': -547924932,
        # 'tips_as': 70667385,
        # 'tips_against': 70667386,
        # 'title': -547924932,

        'stats': {
            # Bases do not include level one per-level bonus
            #   (with the exception of aspd)
            'hp': {
                'base': 742042233,
                'per_level': -988146097
            },
            'hp5': {
                'base': (-166675978, MULT_5),  # hp1
                'per_level': (-1232864324, MULT_5)  # hp1/lvl
            },
            'mana': {
                'base': 742370228,
                'per_level': 1003217290
            },
            'mp5': {
                'base': (619143803, MULT_5),  # mp1
                'per_level': (1248483905, MULT_5)  # mp1/lvl
            },
            'range': 1387461685,
            'dmg': {
                'base': 1880118880,
                'per_level': 1139868982
            },
            'aspd': {
                # TODO: See what champion inibin has -1.0 aspd
                'base': (-2103674057,
                         lambda x: (0.625 / (1.0 + x)) if x != -1.0 else None),
                # Per-level aspd value is an integer percentage (ex. 2 => 2%)
                'per_level': (770205030, lambda x: x * 0.01)
            },
            'armor': {
                'base': -1695914273,
                'per_level': 1608827366
            },
            'mr': {
                'base': 1395891205,
                # TODO: -194100563 was once used for per-level mr
                #   Verify if the old key is still in use
                'per_level': -262788340,
            },
            'speed': 1081768566,
        },

        # Skill names
        'abilities': {
            # TODO: Passive
            # 'passive_desc': 743602011,
            'skill1': 404599689,
            'skill2': 404599690,
            'skill3': 404599691,
            'skill4': 404599692,
        },
    },
    'ability': {
        # Unused
        # # The tags seem inaccurate most of the time
        # 'tags': (1829373218, lambda s: s.split(' | ')),
        # '?buff_tooltip?': -2007242095,
        # '?levelup?': -963665088,

        'cost': {
            # @Cost@
            'level1': -523242843,
            'level2': -523242842,
            'level3': -523242841,
            'level4': -523242840,
            'level5': -523242839,
        },
        'effect1': {
            # @Effect1Amount@
            # Usually physical / magic damage
            'level1': 466816973,
            'level2': -235012530,
            'level3': -936842033,
            'level4': -1638671536,
            'level5': 1954466257
        },
        'effect2': {
            # @Effect2Amount@
            'level1': -396677938,
            'level2': -1098507441,
            'level3': -1800336944,
            'level4': 1792800849,
            'level5': 1090971346
        },
        'effect3': {
            # @Effect3Amount@
            'level1': -1260172849,
            'level2': -1962002352,
            'level3': 1631135441,
            'level4': 929305938,
            'level5': 227476435
        },
        'effect4': {
            # @Effect4Amount@
            'level1': -2123667760,
            'level2': 1469470033,
            'level3': 767640530,
            'level4': 65811027,
            'level5': -636018476
        },
        'effect5': {
            # @Effect5Amount@
            # TODO: Finish
            'WARNING': 'NOT IMPLEMENTED',
            # 'level1': None, # 1229951523 or 1307804625?
            'level2': 605975122,
            'level3': -95854381,
            'level4': -797683884,
            # 'level5': # -1499513387 or 466816973?
        },
        'effect6': {
            # TODO: Finish
            'WARNING': 'NOT IMPLEMENTED'
        },
        'scale1': 844968125,  # @CharAbilityPower@
        'scale2': -1783890251,  # @CharAbilityPower2@
        # There is no scale3 / 4
        # TODO: Damage scaling?
        'cooldown': {
            # @Cooldown@
            'level1': -1665665330,
            'level2': -1665665329,
            'level3': -1665665328,
            'level4': -1665665327,
            'level5': -1665665326,
        },
        'name': 1805538005,
        'internalName': -1203593619,
        'desc': -863113692,
        'tooltip': -1660048132,
        'img': 2059614685,
        'range': -1764096472,
        # For at least one ult this is the right range. Check it if 'range' is 0
        # '?range_ult?': -1549183761,
    },
}


def _take_bits(buf, count):
    """Return the booleans that were packed into bytes."""

    # TODO: Verify output
    bytes_count = (count + 7) // 8
    bytes_mod = count % 8
    data = _unpack_from(buf, 'B', bytes_count)
    values = []
    for i, byte in enumerate(data):
        for _ in range(8 if i != bytes_count - 1 else bytes_mod):
            # TODO: Convert to True / False
            values.append(byte & 0b10000000)
            byte <<= 1
    return values


inibin_format = [
    ('version', 'B'),
    ('end_len', 'H'),
    ('subversion', 'H'),
]
VERSION = 2
FLAGS = [
    (0b0000000000000001, 'i'),  # Signed?
    (0b0000000000000010, 'f'),
    (0b0000000000000100, 'b', lambda x: float(x) / 10),  # Integer divided by 10
    (0b0000000000001000, 'h'),  # Short. Signed?
    (0b0000000000010000, 'b'),  # 1-byte integer. Signed?
    (0b0000000000100000, _take_bits),  # 1-bit booleans, 8 per byte
    (0b0000000001000000, 3, 'b'),  # RGB Color?
    (0b0000000010000000, 3, 'i'),  # ?
    (0b0000010000000000, 4, 'b'),  # RGBA Color?
    (0b0001000000000000, None),  # String offsets
    # String offsets will be handled manually
]


def _fix_keys(key_mapping, inibin_mapping, font_config):
    """
    Create a human-readable dictionary of the values in inibin_mapping.

    Arguments:
    key_mapping -- Dictionary used for conversion. Supports nesting. Every other
        value should be a numeric inibin key, or a tuple of the key and a
        function to apply to the result
    inibin_mapping -- The dictionary returned from reading an inibin
    font_config -- The dictionary loaded from fontconfig_en_US.txt. Strings in
        the inibin are often keys of this dictionary
    """

    def walk(node, out_node):
        # Walk the nodes of the key mapping
        for key, value in node.items():
            if isinstance(value, dict):
                if key not in out_node:
                    out_node[key] = {}
                walk(value, out_node[key])
            else:
                # Can either be just the index, or the index plus a function to apply
                func = None
                if isinstance(value, tuple):
                    func = value[-1]
                    index = value[0]
                else:
                    index = value

                if index is None or index not in inibin_mapping:
                    out_node[key] = None
                    continue

                val = inibin_mapping[index]

                # Try numeric conversion
                # Inibins often store numbers in strings
                if isinstance(val, str):
                    try:
                        val = int(val)
                    except ValueError:
                        try:
                            val = float(val)
                        except ValueError:
                            pass

                # Check if value is a reference to a fontconfig key
                if val in font_config:
                    val = font_config[val]

                # Apply the function
                if func is not None:
                    val = func(val)

                out_node[key] = val

    out = {}
    walk(key_mapping, out)

    return out


def _unpack_from(buf, format, count=None, little_endian=True):
    """Read a binary format from the buffer."""

    if count is not None:
        assert count > 0
        format = '%i%s' % (count, format)

    if little_endian is True:
        format = '<' + format
    else:
        format = '>' + format

    size = struct.calcsize(format)
    res = struct.unpack_from(format, buf.read(size))

    if count is not None:
        return res
    else:
        return res[0]


def read_inibin(buf, font_config, kind='character'):
    """
    Read an inibin file.

    Arguments:
    buf -- file-like object with the inibin's contents. Make sure the file
        was opened in binary mode.
    font_config -- a dictionary representation of fontconfig_en_US.txt
    kind -- either 'character' or 'ability' (default 'character')
    """

    try:
        buf.read
    except AttributeError:
        buf = StringIO.StringIO(buf)

    mapping = {}

    # Header

    version = _unpack_from(buf, 'B')
    assert version == 2

    str_len = _unpack_from(buf, 'H')

    flags = _unpack_from(buf, 'H')

    # Verify that we can process all the flags this inibin uses
    #   (support is not comprehensive yet, but handles all the typical flags)
    recognized_flags = reduce(lambda a, b: a | b, (f[0] for f in FLAGS), 0)
    masked_flags = flags & (~recognized_flags)

    if masked_flags != 0:
        raise RuntimeError(
            "Unrecognized flags. Observed: %s, whitelisted: %s, difference: %s" %
            (bin(flags), bin(recognized_flags), bin(masked_flags)))

    # Inibin v2 blocks
    # Flags are in the order they would appear in the file in
    for row in FLAGS:
        if row[0] & flags:
            # This skip is here for the last flag, the string table
            if row[1] is None:
                continue

            # Read number of keys
            count = _unpack_from(buf, 'H')
            keys = _unpack_from(buf, 'i', count)

            # Does the flag specify multiple values per key?
            per_count = 1
            try:
                per_count = int(row[1])
            except (ValueError, TypeError):
                pass
            else:
                # Remove multiplier from the row
                row = [row[0]] + list(row[2:])

            # Read values
            if isinstance(row[1], basestring):
                values = _unpack_from(buf, row[1], per_count * count)

                # Apply row functions (if any)
                for transform in row[2:]:
                    values = [transform(v) for v in values]
            elif callable(row[1]):
                # Custom function (ex. bits)
                values = row[1](buf, count)
            else:
                raise RuntimeError("Unknown operation.")

            # If there were multiple values per key, group them
            # TODO: This creates a list of lists even if count == 1
            if per_count > 1:
                values_out = []
                for i, val in enumerate(values):
                    if i % per_count == 0:
                        values_out.append([])
                    values_out[-1].append(val)
                values = values_out
                del values_out

            # Update mapping
            for key, value in zip(keys, values):
                assert key not in mapping
                mapping[key] = value

    # String table
    # TODO: Move this into its own function
    if flags & 0b0001000000000000:
        count = _unpack_from(buf, 'H')
        keys = _unpack_from(buf, 'i', count)
        values = _unpack_from(buf, 'H', count)
        strings = buf.read(str_len)
        mapping['raw_strings'] = strings  # For debug
        values = [strings[v:].partition('\x00')[0] for v in values]

        for key, value in zip(keys, values):
            assert key not in mapping
            mapping[key] = value

    # There should be no non-padding bytes remaining
    remaining = buf.read()
    if len(remaining) > 0 and not all(c == '\x00' for c in remaining):
        raise RuntimeError("%i bytes remaining!" % len(remaining))

    # Convert the mapping to be more human-readable
    assert kind in KEY_MAPPING
    mapping = _fix_keys(KEY_MAPPING[kind], mapping, font_config)

    return mapping


if __name__ == '__main__':
    from pprint import pprint
    import sys
    assert len(sys.argv) == 2
    with open(sys.argv[1], 'rb') as f:
        data = f.read()
    mapping = read_inibin(data)
    pprint(mapping)
