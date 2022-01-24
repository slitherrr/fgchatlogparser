import re

LINE_CONTENTS_PARSER = re.compile(r'^(<font color="#[0-9a-f]{6,8}">)(.*)(</font>)(?: \[(.*)\])?')
LINK_PARSER = re.compile(r'^<a href="([^"]+)">\(LINK\)</a>$')
LOG_TIMESTAMP = re.compile(r"<b>Chat log started at (\d{1,2})\.(\d{1,2})\.(\d{4}) / (\d\d):(\d\d):(\d\d)</b>")
HIDDEN_ROLL_GM = re.compile(r"^(absalom|GM):")

IGNORE_THESE = [
    'SLASH COMMANDS:',
    ' /die [NdN+N] [message]',
    ' /vote [message]',
    ' /ooc [message]',
    ' /emote [message]',
    ' /mood [mood] [message]',
    ' /mood ([multiword mood]) [message]',
    'Gamemaster only:',
    ' /story [message]',
    ' /identity [name]',
    ' /whisper [character] [message]',
    ' /export [module_filename] [description]',
    ' /save',
    ' /clear',
    ' /night',
    ' /day',
    'Campaign saved.',
]

OOC_AND_WHISPERS = [re.compile(r) for r in [
    r'\A-> [^:]+:',  # whispers
    r'\A\w+ \([\s\w]+\):',  # OOC
]]


def chunks_by_date(lines, encoding="utf8"):
    line_group = None
    current_timestamp = None
    for l in lines:
        l = l.decode(encoding)
        l = l.strip().replace('<br />', '').replace('<br/>', '')
        if not l:
            continue

        timestamp_match = LOG_TIMESTAMP.match(l)
        if timestamp_match:
            if current_timestamp:
                yield (line_group, current_timestamp)
            line_group = []
            month, day, year, hour, minute, second = timestamp_match.groups()
            current_timestamp = "%s%s%s_%s%s%s" % (year, month, day, hour, minute, second)
            continue

        contents_match = LINE_CONTENTS_PARSER.match(l)
        font_start, contents, font_end, crunch = [""] * 4
        if contents_match:
            font_start, contents, font_end, crunch = contents_match.groups()
        else:
            link_match = LINK_PARSER.match(l)
            if link_match:
                (contents,) = link_match.groups()
                contents = '<a href="{url}">{url}</a>'.format(url=contents)
            else:
                raise RuntimeError("Got unexpected line: %s" % l)

        if crunch and HIDDEN_ROLL_GM.match(contents):
            line_group.append("[hiding roll result for %s]" % contents)
        elif contents and contents in IGNORE_THESE:
            continue
        elif contents:
            if any([r.match(contents) for r in OOC_AND_WHISPERS]):
                continue
            if line_group is None:
                current_timestamp = "unknown_time"
                line_group = []
            line_group.append("%s%s%s" % (font_start, contents, font_end))

    if line_group:
        yield (line_group, current_timestamp)
