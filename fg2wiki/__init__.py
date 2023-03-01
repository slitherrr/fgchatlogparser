import os

from itertools import groupby
from typing import IO, Any, Dict, Iterable, List, Tuple, TypeVar, Union, cast
from bs4 import BeautifulSoup, NavigableString
from bs4.element import Tag
from jinja2 import FileSystemLoader, Environment


T = TypeVar('T')


def ident(x: T) -> T:
    return x


def strc(tag: Tag) -> str:
    return ' '.join(str(x) for x in tag.contents)


def intc(tag: Tag) -> int:
    cast_contents = cast(List[str], tag.contents)
    num = int(cast_contents[0])
    return num


def formattedtextc(tag: Tag) -> str:
    return ''.join(str(x) for x in tag.children)


def formatclasslevels(classes: List[Tag]) -> str:
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


def only_prefix_children(tag: Tag, prefix) -> Iterable[Tag]:
     for child in only_tag_children(tag):
        if child.name.startswith(prefix):
            yield child


def only_tag_children(tag: Tag) -> Iterable[Tag]:
    for child in tag.children:
        if isinstance(child, Tag):
            yield child


def child_by_tag(tag: Tag, childname: str, recursive: bool=False) -> Union[Tag, NavigableString, None]:
    return tag.find(childname, recursive=recursive)


def xmlc(tag: Union[Tag, NavigableString, None], format_with: Union[str, None] = None) -> Union[str, int]:
    if tag is None or isinstance(tag, NavigableString):
        return ''

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


def grouptagsby(iterable_of_tags: Iterable[Tag], attrname: str) -> Iterable[Tuple[Union[str, int], Iterable[Tag]]]:
    def keyfunc(el: Tag) -> Union[str, int]:
        return xmlc(child_by_tag(el, attrname))

    return groupby(sorted(iterable_of_tags, key=keyfunc), key=keyfunc)


def pluraltext(n: int, singular: str, plural: str) -> str:
    if n == 1:
        return singular
    else:
        return plural


def makepowergroupindex(powergroups: Tag, spellsonly: bool=False) -> Dict[str, Tag]:
    powergroupindex = {}

    for group in only_tag_children(powergroups):
        if spellsonly and group.castertype is None:
            continue

        powergroupindex[xmlc(child_by_tag(group, 'name'))] = group

    return powergroupindex


def nw(elem: Any) -> str:
    return f"<nowiki>{elem}</nowiki>"


def parse_to_wiki(sheet: BeautifulSoup) -> List[Tuple[str, str]]:
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
    pgi = {}
    rv = []

    if not sheet.root or not sheet.root.character:
        return rv

    for i, character in enumerate(sheet.root.find_all('character', recursive=False)):
        name_tag = child_by_tag(character, 'name')
        name = (
            strc(name_tag) if name_tag and not isinstance(name_tag, NavigableString)
            else f'character{i}'
        )

        if character.powergroup:
            pgi = makepowergroupindex(character.powergroup)

        rv.append((name.replace(' ', ''), tpl.render(charname=name, character=character, powergroupindex=pgi)))

    return rv


def parse_to_wiki_from_io(sheet_io: IO[bytes], from_encoding: Union[str, None]=None) -> List[Tuple[str, str]]:
    return parse_to_wiki(BeautifulSoup(sheet_io, "xml", from_encoding=from_encoding))



