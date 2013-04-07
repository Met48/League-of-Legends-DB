# LoL DB

Easy-to-use League of Legends data.

```javascript
> items.recurve_bow.stats.aspd
{ flat: 0, percentage: 30 }
> champions.caitlyn.stats.dmg
{ base: 47, per_level: 3 }
> champions.wukong.internal_name
'MonkeyKing'
> champions.quinn.skins.phoenix
{ portrait: 'Quinn_1.jpg',
  internal_name: 'PhoenixQuinn',
  name: 'Phoenix Quinn',
  base: false,
  splash: 'Quinn_Splash_1.jpg',
  id: 133001 }
```

## WIP!

This is still in early development, so make sure to check out the Todo before using.

## Overview

To get started just download a file from [the output branch](https://github.com/Met48/LoLDB/tree/output). Both JSON and YAML are supported; take a look!

```yaml
champions:
  103: &id556
    abilities:
    - cooldown: [7.0, 7.0, 7.0, 7.0, 7.0]
      cost: [70.0, 75.0, 80.0, 85.0, 90.0]
      desc: Ahri sends out and pulls back her orb, dealing magic damage on the way
        out and true damage on the way back.
      name: Orb of Deception
      tooltip: Deals @Effect1Amount@ (+@CharAbilityPower@) magic damage on the way
        out, and @Effect1Amount@ (+@CharAbilityPower@) true damage on the way back.
      tooltip_values:
        '@CharAbilityPower@': 0.32499998807907104
        '@Effect1Amount@': [40.0, 65.0, 90.0, 115.0, 140.0]
        # ...
    # ...
    icon: Ahri_Square_0.png
    id: 103
    internal_name: Ahri
    lore: {desc: 'Unlike other foxes that roamed the woods of southern Ionia, ...',
      quote: Mercy is a human luxury... and responsibility., quote_author: Ahri}
    name: Ahri
    rating: {attack: 3, defense: 4, difficulty: 8, magic: 8}
    select_sound: en_US/Ahri.mp3
    skins:
      0: &id482 {base: true, id: 103000, internal_name: BaseAhri, name: '', portrait: Ahri_0.jpg,
        splash: Ahri_Splash_0.jpg}
      1: &id483 {base: false, id: 103001, internal_name: AhriHanbok, name: Dynasty
          Ahri, portrait: Ahri_1.jpg, splash: Ahri_Splash_1.jpg}
      2: &id485 {base: false, id: 103002, internal_name: AhriShadowfox, name: Midnight
          Ahri, portrait: Ahri_2.jpg, splash: Ahri_Splash_2.jpg}
      3: &id484 {base: false, id: 103003, internal_name: AhriFireFox, name: Foxfire
          Ahri, portrait: Ahri_3.jpg, splash: Ahri_Splash_3.jpg}
      base: *id482
      count: 4
      dynasty: *id483
      foxfire: *id484
      midnight: *id485
    stats:
      armor: {base: 11, per_level: 3.5}
      aspd: {base: 0.66844919615646303, per_level: 0.02}
      dmg: {base: 50, per_level: 3}
      hp: {base: 380, per_level: 80}
      hp5: {base: 5.5, per_level: 0.59999998658895493}
      mana: {base: 230, per_level: 50}
      mp5: {base: 6.25, per_level: 0.59999998658895493}
      mr: {base: 30, per_level: 0}
      range: 550
      speed: 330
    tags: {assassin: true, mage: true, ranged: true}
    tips:
      against: ['Ahri''s survivability is dramatically reduced when her Ultimate,
          Spirit Rush, is down.', 'Stay behind minions to make Charm difficult to
          land, this will reduce Ahri''s damage potential significantly.']
      as: ['Use Charm to set up your combos, it will make landing Orb of Deception
          and Fox-Fire dramatically easier.', ...]
    title: the Nine-Tailed Fox
  ahri: *id556
  # ...
items:
  3128: &id697
    categories: {active: true, cooldown_reduction: true, spell_damage: true}
    cost: 680
    icon: 055_Borses_Staff_of_Apocalypse.png
    id: 3128
    name: Deathfire Grasp
    recipe: [1058, 3108]
    stats:
      ad: {flat: 0.0, percentage: 0.0}
      ap: {flat: 120.0, percentage: 0.0}
      # ...
    tier: 2
    tooltip: <stats>+120 Ability Power<br>+10% Cooldown Reduction</stats><br><br><active>UNIQUE
      Active:</active> Deals 15% of target champion's maximum Health in magic damage
      and increases all subsequent magic damage taken by the target by 20% for 4 seconds
      (60 second cooldown).
  deathfire_grasp: *id697
  # ...
```

It's almost completely automatic; running it on most patches won't need any user input, making it easy to keep up-to-date.

## Requirements

- [IronPython 2.7.3](http://ironpython.net/)
- [RAFlibPlus](https://code.google.com/p/raflib-plus/)
- [PyYAML](https://pypi.python.org/pypi/PyYAML)

Extract RAFlibPlus to `../raflib`.

It will load your regular `site-packages` as well, so you don't need to install PyYAML for IronPython specifically. This hack will probably be removed in the future.

## Usage

For now, you can find generated output on [the output branch](https://github.com/Met48/LoLDB/tree/output).

You can also generate the most up-to-date version from your local install. Make sure raflib is in place and that the `archives` directory exists. Then just run `ipy main.py`.

It will create `league.json`, `league.part.json`, `league.pickle`, and `league.yaml` for you. Every version will also get copied to `archives`.

## Todo

- Fix errors in `tooltip_values`
  - Fix `@f1@`, `@f2@`, etc.
  - Fix `@Effect6Amount@` - this only affects Quinn
- Fix rounding of `aspd`, `tooltip_values`
- Fix output for languages that translate character names
- Fix ability costs that aren't mana
- Fix Rumble's abilities

--

- Generate data for champion passives
- Generate information for runes
- Organize data better for iteration
  - Ex. A list of champion ids is really needed
- Extract what each effect actually does using the tooltips
  - This is WIP, see `parse_tooltip.py`
- Generate an efficient, web-friendly version
  - Current size of `league.part.json` is 900 KB

## Sources

Data is gathered from the local game installation, assumed to be on `C:\`.

- Champions
  - Basic data, skins: `gameStats_en_US.sqlite`
  - Stats, abilities: RAF archives, `fontconfig_en_US.txt`
- Items: `gameStats_en_US.sqlite`

Data for other languages can be generated as well.
