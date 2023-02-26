import os

from collections import defaultdict
from itertools import groupby
from bs4 import BeautifulSoup
from bs4.element import Tag
from jinja2 import FileSystemLoader, Environment


def ident(x):
    return x


def strc(tag):
    return ' '.join(tag.contents)


def intc(tag):
    num = int(tag.contents[0])
    return num

def formattedtextc(tag):
    return ''.join(str(x) for x in tag.children)

def formatclasslevels(classes):
    level_items = [
        (
            xmlc(child_by_tag(ccls, 'name')),
            xmlc(ccls.level),
        ) for ccls in classes
    ]
    if not level_items:
        return ''
    else:
        return ' / '.join(f'{cname} {num}' for (cname, num) in level_items)


def only_prefix_children(tag, prefix):
     for child in only_tag_children(tag):
        if child.name.startswith(prefix):
            yield child


def only_tag_children(tag):
    for child in tag.children:
        if isinstance(child, Tag):
            yield child

def child_by_tag(tag, childname, recursive=False):
    return tag.find(childname, recursive=recursive)


def xmlc(tag, format_with=None):
    formatter_func = format_with.format if format_with else ident

    if tag.attrs['type'] == 'number':
        result = intc(tag)
    elif tag.attrs['type'] == 'string':
        result = strc(tag)
    elif tag.attrs['type'] == 'formattedtext':
        result = formattedtextc(tag)
    else:
        raise RuntimeError(f"called xmlc for unhandled type {tag.attrs['type']}")

    return formatter_func(result)


def grouptagsby(iterable_of_tags, attrname):
    def keyfunc(el):
        return xmlc(child_by_tag(el, attrname))

    return groupby(sorted(iterable_of_tags, key=keyfunc), key=keyfunc)


def pluraltext(n, singular, plural):
    if n == 1:
        return singular
    else:
        return plural


def makepowergroupindex(powergroups, spellsonly=False):
    powergroupindex = {}
    for group in only_tag_children(powergroups):
        if spellsonly and group.castertype is None:
            continue

        powergroupindex[xmlc(child_by_tag(group, 'name'))] = group

    return powergroupindex

def grouppowersbyname(powers, powergroups, spellsonly=False):
    grouped = defaultdict(list)

    powergroupindex = makepowergroupindex(powergroups, spellsonly=spellsonly)
    for power in only_tag_children(powers):
        gname = xmlc(power.group)
        if gname in powergroupindex:
            grouped[gname].append(power)

    return grouped


def nw(elem):
    return f"<nowiki>{elem}</nowiki>"


def parse_to_wiki(sheet):
    loader = FileSystemLoader(os.path.dirname(os.path.realpath(__file__)))
    env = Environment(autoescape=False, loader=loader, extensions=['jinja2.ext.i18n'])
    env.filters['xmlc'] = xmlc
    env.filters['only_prefix_children'] = only_prefix_children
    env.filters['only_tag_children'] = only_tag_children
    env.filters['formatclasslevels'] = formatclasslevels
    env.filters['child_by_tag'] = child_by_tag
    env.filters['pluraltext'] = pluraltext
    env.filters['makepowergroupindex'] = makepowergroupindex
    env.filters['grouptagsby'] = grouptagsby
    env.filters['nw'] = nw

    tpl = env.get_template('wiki.tpl')
    return tpl.render(sheet=sheet, powergroupindex=makepowergroupindex(sheet.character.powergroup))


def parse_to_wiki_from_io(sheet_io, from_encoding=None):
    return parse_to_wiki(BeautifulSoup(sheet_io, "xml", from_encoding=from_encoding))



