from collections import namedtuple
import re


def get_skins_map(connection):
    """Get formatted champion skin details from sql database."""

    skins_map = {}

    cursor = connection.cursor()
    rows = cursor.execute("SELECT * FROM `championSkins`")

    # Get column names from cursor
    columns = [c[0] for c in cursor.description]
    ChampionSkinRow = namedtuple('ChampionSkinRow', columns)

    for row in rows:
        row = ChampionSkinRow(*row)

        skin = {
            'id': row.id,
            'name': row.displayName,
            'internal_name': row.name,
            'portrait': row.portraitPath,
            'splash': row.splashPath,
            'base': bool(row.isBase),
        }

        # Add to temporary skins table
        champion_id = row.championId
        if champion_id not in skins_map:
            skins_map[champion_id] = {}
        skins_map[champion_id][row.rank] = skin

    return skins_map


def to_underscore_notation(s):
    """Split a string with underscores at case changes."""

    s = re.sub('(?<=[a-z])[A-Z]', lambda m: '_' + m.group(0), s)
    s = re.sub(' ', '_', s)
    s = re.sub('^_+', '', s)
    s = re.sub('_+$', '', s)
    s = re.sub('__+', '_', s)
    s = s.lower()
    return s


def guess_name(skin, internal_champ_name, corrections):
    """
    Tries to derive "friendly" skin name.

    Returns tuple of:
        guess - string
        confident - bool

    The process for finding a "friendly" name uses two guesses:
        1. The internal skin name with the internal champion name removed
        2. The public skin name with the last word removed
    Both methods have deficiencies.

    Method one can produce bad names because the internal names do not always
    reflect the ppublic name of the skin.
    Method two will fail whenever a champion has a multi-word name.

    The confidence of the answer depends on both methods agreeing.
    """

    internal_skin_name = skin['internal_name']
    underscore_skin_name = to_underscore_notation(skin['name'])

    # First guess - internal skin name with internal champ name removed
    guess1 = re.sub('(?i)' + re.escape(internal_champ_name),
                    '', internal_skin_name)
    guess1 = to_underscore_notation(guess1)

    # Second guess - public skin name with last word removed (name)
    guess2 = skin['name'].split()
    guess2 = guess2[:-1]
    guess2 = '_'.join(guess2)
    guess2 = to_underscore_notation(guess2)

    # Check if the automatic replacement is good enough
    if (guess1 == guess2 or
            guess1 in underscore_skin_name or
            guess1 == 'base'):
        return guess1, True

    # Check if a correction exists
    if internal_skin_name in corrections:
        # If the correction is "None", it indicates guess1 is fine
        if corrections[internal_skin_name] is None:
            return None, True
        else:
            return corrections[internal_skin_name], True

    return guess2, False


def request_replacement(skin, guess):
    internal_skin_name = skin['internal_name']
    print ''
    print "Skin Name:            ", skin['name']
    print "Skin Internal Name:   ", internal_skin_name
    print "Current replacement:  ", guess

    print "Enter Y to accept the current replacement."
    print "Enter N to assign no replacement."
    print "Or enter a manual replacement."

    while True:
        response = raw_input('> ').strip()

        if response.lower() == 'y':
            print "Setting", internal_skin_name, "to", guess
            return guess
        elif response.lower() == 'n':
            print "Setting no replacement."
            return None
        elif len(response.strip()) < 2:
            print 'Please enter a valid option.'
        else:
            print "Setting", internal_skin_name, "to", response
            return response


def correct_skins_map(skins, champions, corrections):
    """
    Correct skins, in-place.

    Requires champions dictionary for more accurate naming.
    """

    corrections = corrections.setdefault('skins', {})

    for champion_id, champion_skins in skins.items():
        assert champion_id in champions
        internal_champ_name = champions[champion_id]['internal_name']

        for _, skin in champion_skins.items():
            internal_skin_name = skin['internal_name']
            guess, probable = guess_name(skin, internal_champ_name, corrections)

            if probable:
                if guess is not None:
                    skin['aliases'] = [guess]
                continue

            replacement = request_replacement(skin, guess)
            corrections[internal_skin_name] = replacement
            if replacement is not None:
                skin['aliases'] = [replacement]
