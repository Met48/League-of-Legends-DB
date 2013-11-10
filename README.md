# LoL DB

League of Legends database generator that uses the local game install for all its information.

## WIP!

This is incomplete, check the todo before using.

## Introduction

This utility makes it easy to generate an up-to-date League of Legends database. It relies only on the local game install, so it can be run as soon as the game updates and will catch all changes.

As the utility is still early in development, there is some manual involvement via a correction file. This file contains some ability values which could not be automatically extracted.

## What the Output Looks Like

```yaml
champions:
- abilities:
  - description: Ahri sends out and pulls back her orb, dealing magic damage on the
      way out and true damage on the way back.
    key: Q
    levels:
    - cooldown: 7.0
      cost: 70.0
      tooltip_values: {'@CharAbilityPower@': 32.499998807907104, '@Effect1Amount@': 40.0}
    # ...
    name: Orb of Deception
    tooltip: Deals @Effect1Amount@ (+@CharAbilityPower@) magic damage on the way out,
      and @Effect1Amount@ (+@CharAbilityPower@) true damage on the way back.
  # ...
  alias: ahri
  icon_path: Ahri_Square_0.png
  id: 103
  internal_name: Ahri
  lore: {body: 'Unlike other foxes that roamed the woods of southern Ionia, Ahri had
      always felt a strange connection to the magical world around her; a connection
      that was somehow incomplete. Deep inside, she felt the skin she had been born
      into was an ill fit for her and dreamt of one day becoming human. Her goal seemed
      forever out of reach, until she happened upon the wake of a human battle. It
      was a grisly scene, the land obscured by the forms of wounded and dying soldiers.
      She felt drawn to one: a robed man encircled by a waning field of magic, his
      life quickly slipping away. She approached him and something deep inside of
      her triggered, reaching out to the man in a way she couldn''t understand. His
      life essence poured into her, carried on invisible strands of magic. The sensation
      was intoxicating and overwhelming. As her reverie faded, she was delighted to
      discover that she had changed. Her sleek white fur had receded and her body
      was long and lithe - the shape of the humans who lay scattered about her.


      However, though she appeared human, she knew that in truth the transformation
      was incomplete. A cunning creature, she adapted herself to the customs of human
      society and used her profound gift of beauty to attract unsuspecting men. She
      could consume their life essences when they were under the spell of her seductive
      charms. Feeding on their desires brought her closer to her dream, but as she
      took more lives, a strange sense of regret began to well within her. She had
      reservations about actions which never troubled her as a fox. She realized that
      she could not overcome the pangs of her evolving morality. In search of a solution,
      Ahri found the Institute of War, home of the most gifted mages on Runeterra.
      They offered her a chance to attain her humanity without further harm through
      service in the League of Legends.', quote: Mercy is a human luxury... and responsibility.,
    quote_author: Ahri}
  name: Ahri
  ratings: {attack: 3, defense: 4, difficulty: 8, magic: 8}
  select_sound_path: ''
  skins:
  - {champion_id: 103, id: 103000, internal_name: BaseAhri, is_base: 1, name: '',
    portrait_path: Ahri_0.jpg, rank: 0, splash_path: Ahri_Splash_0.jpg}
  - {champion_id: 103, id: 103001, internal_name: AhriHanbok, is_base: 0, name: Dynasty
      Ahri, portrait_path: Ahri_1.jpg, rank: 1, splash_path: Ahri_Splash_1.jpg}
  - {champion_id: 103, id: 103002, internal_name: AhriShadowfox, is_base: 0, name: Midnight
      Ahri, portrait_path: Ahri_2.jpg, rank: 2, splash_path: Ahri_Splash_2.jpg}
  - {champion_id: 103, id: 103003, internal_name: AhriFireFox, is_base: 0, name: Foxfire
      Ahri, portrait_path: Ahri_3.jpg, rank: 3, splash_path: Ahri_Splash_3.jpg}
  stats:
    armor: {base: 11, per_level: 3.5}
    attack_speed: {base: 0.668449196156463, per_level: 0.02}
    damage: {base: 50, per_level: 3}
    hp: {base: 380, per_level: 80}
    hp5: {base: 5.5, per_level: 0.5999999865889549}
    magic_resist: {base: 30, per_level: 0}
    mana: {base: 230, per_level: 50}
    mp5: {base: 6.25, per_level: 0.5999999865889549}
    range: 550
    speed: 330
  tags: !!set {mage: null}
  tips_against: ['Ahri''s survivability is dramatically reduced when her Ultimate,
      Spirit Rush, is down.', 'Stay behind minions to make Charm difficult to land,
      this will reduce Ahri''s damage potential significantly.']
  tips_as: ['Use Charm to set up your combos, it will make landing Orb of Deception
      and Fox-Fire dramatically easier.', 'Initiate team fights using Charm, and chase
      down stragglers with Spirit Rush.', 'Spirit Rush enables Ahri''s abilities,
      it opens up paths for Charm, helps double hitting with Orb of Deception, and
      closes to make use of Fox-Fire.']
  title: the Nine-Tailed Fox
# ...
items:
  3128:
    alias: deathfire_grasp
    categories: !!set {active: null, cooldown_reduction: null, spell_damage: null}
    cost: 680
    icon_path: 3128_Deathfire_Grasp.png
    id: 3128
    name: Deathfire Grasp
    recipe: !!set {1058: null, 3108: null}
    stats:
      ap: {flat: 120.0, percentage: 0.0}
      armor: {flat: 0.0, percentage: 0.0}
      # ...
    tier: 2
    tooltip: <stats>+120 Ability Power<br>+10% Cooldown Reduction</stats><br><br><active>UNIQUE
      Active:</active> Deals 15% of target champion's maximum Health in magic damage
      and increases all subsequent magic damage taken by the target by 20% for 4 seconds
      (60 second cooldown).
  # ...
```

## Installation

After you have cloned the repo, you will need to install the dependencies. The easiest way to do this is via `pip install -r requirements.txt`. If you don't have pip, install the following dependencies:

- [raf](https://pypi.python.org/pypi/raf)
- [inibin](https://pypi.python.org/pypi/inibin)
- [PyYAML](https://pypi.python.org/pypi/PyYAML)
- [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/)
- [docopt](http://docopt.org/)

## Usage

Use from the command line.

Typical usage is `python -m loldb stats --json output.json --yaml output.yaml`.

```
Usage:
  loldb stats [options]
  loldb --help
  loldb --version

Options:
  -p, --path=<path>     Location of LoL installation.
  -o, --os=<system>     Operating system. Either 'mac' or 'win', if absent
                        attempts to auto-detect.

  -j, --json=<path>     Location to write json representation to.
  -y, --yaml=<path>     Location to write yaml representation to.

  -f, --force           Continue automatically on warnings.
  -n, --no              Abort automatically on warnings.

  --skip-corrections    Debug option, does not correct champions.
  --skip-validation     Debug option, does not validate output.


  -h, --help            Display this message.
  --version             Display version number.
```

## Todo

- Fix sets in YAML output
- Extract champion passives
- Finish implementing corrections. There's ~100 abilities missing one or more values, as well as an entire ability missing for Rumble.
- Get information for runes
- Fix rounding of stats and tooltip values
- Verify output for languages that translate character names
- Fix ability costs that aren't mana
- Extract meaning of tooltip values

## Sources

Data is gathered from the local game installation.

- Champions
  - Basic data, skins: `gameStats_en_US.sqlite`
  - Stats, abilities: RAF archives
- Items: `gameStats_en_US.sqlite`
