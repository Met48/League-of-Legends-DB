import collections


def correct_champions(champions):
    for champion in champions:
        for ability in champion.abilities:
            correct_ability(ability)


ABILITY_CORRECTIONS = {
    # Ahri
    'Fox-Fire': {
        # @f1 shows maximum damage to a single target
        # Each fox-fire after the first does 30% damage
        # So if three hit a single target total is 160% damage
        '@f1@': lambda x: float(int(x.tooltip_values['@Effect1Amount@'] * 1.6)),
        'levels': {

        }
    },
}


def correct_ability(ability):
    def apply_correction(key, correction, level):
        if isinstance(correction, collections.Callable):
            correction = correction(level)
        level.tooltip_values[key] = correction

    correction = ABILITY_CORRECTIONS.get(ability.name, None)
    if correction is not None:
        for key, value in correction.items():
            if key == 'levels':
                # Corrections to individual levels
                # TODO: Refactor
                for level in value:
                    for i, (key, value) in enumerate(level.items()):
                        apply_correction(key, value, ability.levels[i])
            else:
                # Apply to all levels
                for level in ability.levels:
                    apply_correction(key, value, level)
