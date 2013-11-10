import re


# TODO: Validate items


def validate_champions(champions):
    """
    Generate error messages for every champion that does not validate.

    :type champions: [champion.Champion]
    """
    if not champions:
        yield 'No champions!'

    def validate_attribute(champion, attribute_name):
        if not getattr(champion, attribute_name):
            yield 'Missing %s for champion %s.' % (
                attribute_name, champion.internal_name or champion.id
            )

    for champion in champions:
        identifier = None

        # Validate attributes
        if champion.id < 0:
            yield 'Invalid champion id %d' % id
        else:
            identifier = champion.id

        validate_attribute(champion, 'internal_name')
        validate_attribute(champion, 'name')
        validate_attribute(champion, 'alias')
        validate_attribute(champion, 'title')
        validate_attribute(champion, 'tips_as')
        validate_attribute(champion, 'tips_against')
        validate_attribute(champion, 'tags')
        validate_attribute(champion, 'skins')

        # Validate abilities
        len_abilities = len(champion.abilities)
        if len_abilities != 4:
            yield 'Champion %s has %d abilities, expected 4!' % (
                champion.internal_name or champion.id,
                len_abilities,
            )

        for ability in champion.abilities:
            for message in validate_ability(ability):
                yield message

        # TODO: Validate ratings
        # TODO: Validate stats
        # TODO: Validate skins


def validate_ability(ability):
    """

    :type ability: ability.Ability
    """
    def validate_attribute(ability, attribute_name):
        if not getattr(ability, attribute_name):
            yield 'Missing %s for ability %s.' % (attribute_name, ability)

    validate_attribute(ability, 'name')
    validate_attribute(ability, 'description')
    validate_attribute(ability, 'key')
    validate_attribute(ability, 'tooltip')

    len_levels = len(ability.levels)
    if len_levels != (3 if ability.key == 'R' else 5):
        yield 'Unusual level count %s for ability %s.' % (len_levels,ability)

    keys = set(re.findall(r'@\w+@', ability.tooltip))

    for i, level in enumerate(ability.levels):
        missing_keys = keys - set(level.tooltip_values)
        if missing_keys:
            yield 'Missing tooltip keys %s for level %i of ability %s.' % (
                missing_keys, i, ability
            )
