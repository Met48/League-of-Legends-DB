import collections
import os.path


def get_answer():
    """Get a yes or no answer from the user."""
    while True:
        answer = raw_input('y/n > ').lower()
        if answer not in ('y', 'n'):
            print "Enter a valid option."
        else:
            return answer == 'y'


# Processing dictionaries

def merge(*mappings):
    out = dict()

    def walk(obj, base):
        for key, value in obj.items():
            if isinstance(value, collections.Mapping):
                walk(value, base.setdefault(key, {}))
            else:
                if key in base:
                    print "WARNING: Merging duplicate key '%s'" % key
                base[key] = value

    for mapping in mappings:
        walk(mapping, out)

    return out


def fix_aliases(league, remove=False):
    def copy_aliases(node, parent, aliases):
        """Copy node to alias keys of parent."""
        for alias in aliases:
            if len(alias) < 3:
                print "WARNING: Short alias '%s'" % alias
            if alias in parent:
                print "WARNING: Alias '%s' already exists, skipping" % alias
            else:
                parent[alias] = node

    def count_seq(node):
        """Add a count if node has keys similar to a 0-indexed list."""
        numeric_keys = set()
        for key in node.keys():
            try:
                key = int(key)
            except ValueError:
                continue
            else:
                numeric_keys.add(key)

        if numeric_keys and 0 in numeric_keys:
            count = 0
            while count in numeric_keys:
                count += 1
            node['count'] = count

    def update_walk(node, parent):
        """Recursive walk that updates aliases."""

        if 'aliases' in node:
            aliases = node['aliases']
            del node['aliases']

            if not parent:
                print ("WARNING: Aliases '%r' for root-level node" %
                       aliases)
            else:
                if not remove:
                    copy_aliases(node, parent, aliases)

        count_seq(node)

        # Continue walk
        node_items = list(node.items())
        for key, item in node_items:
            if isinstance(item, collections.Mapping):
                update_walk(item, node)

    update_walk(league, None)

    return league


# Working with LoL paths

def get_highest_version(versions):
    versions = [(v, v.split('.')) for v in versions]

    def version_converter(version):
        try:
            parts = map(int, version[1])
        except ValueError:
            return None
        else:
            return [parts, version[0]]

    versions = map(version_converter, versions)
    versions = filter(lambda x: x is not None, versions)
    versions = sorted(versions)

    if not versions:
        raise RuntimeError("No valid version.")

    return versions[-1][1]


def build_path(
        base_path,
        project="lol_air_client",
        subdir='releases',
        version=None):
    """Generate path for most recent release of a project."""

    subdir = subdir.lower()
    path = [base_path, "RADS/projects", project, subdir]

    if subdir != 'filearchives':
        if version is None:
            current_base = os.path.join(*path)
            versions = os.listdir(current_base)
            versions = [v for v in versions if
                        os.path.isdir(os.path.join(current_base, v))]
            version = get_highest_version(versions)

        path.append(version)

    return os.path.join(*path)
