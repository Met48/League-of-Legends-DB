class Skin(object):
    id = -1
    name = ''
    portrait_path = ''
    splash_path = ''
    is_base = False
    champion_id = -1
    rank = -1

    def __init__(self, internal_name):
        self.internal_name = internal_name

    def __repr__(self):
        return "<Skin %s '%s'>" % (self.id, self.name)


def _make_skin_from_sql_row(row):
    skin = Skin(row.name)
    skin.id = row.id
    skin.name = row.displayName
    skin.portrait_path = row.portraitPath
    skin.splash_path = row.splashPath
    skin.is_base = row.isBase
    skin.champion_id = row.championId
    skin.rank = row.rank  # TODO: ?
    return skin


def get_skins(provider):
    for row in provider.get_db_rows('championSkins'):
        yield _make_skin_from_sql_row(row)


def get_skins_for_champion(provider, champion_id):
    query = "SELECT * FROM `championSkins` WHERE championId = %s" % champion_id
    for row in provider.get_db_query(query):
        yield _make_skin_from_sql_row(row)
