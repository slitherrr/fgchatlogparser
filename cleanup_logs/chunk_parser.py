import re

LINE_CONTENTS_PARSER = re.compile(r'^(<font color="##?[0-9a-f]{6,8}">)(.*)(</font>)(?: \[(.*)\])?', re.IGNORECASE)
LINK_PARSER = re.compile(r'^<a href="([^"]+)">\(LINK\)</a>$')
LOG_TIMESTAMP = re.compile(r'(?:<a name="\d{4}-\d{1,2}-\d{1,2}" /><b>Session started at (\d{4})-(\d{1,2})-(\d{1,2}) / (\d\d):(\d\d)|<b>Chat log started at (\d{1,2})\.(\d{1,2})\.(\d{4}) / (\d\d):(\d\d):(\d\d))</b>')
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
    'SLASH COMMANDS [required] &#60;optional&#62;',
    '----------------',
    '/afk ',
    '/clear ',
    '/console ',
    '/dicevolume [0-100|on|off]',
    '/die [NdN+N] &#60;message&#62;',
    '/emote [message]',
    '/export ',
    '/exportchar ',
    '/exportnpc ',
    '/flushdb ',
    '/gmid [name]',
    '/id [name]',
    '/importchar ',
    '/importnpc ',
    '/info ',
    '/kick [user]',
    '/mod [N] &#60;message&#62;',
    '/mood [mood] &#60;message&#62;',
    '/mood ([multiword mood]) &#60;message&#62;',
    '/ooc [message]',
    '/option [option_name] &#60;option_value&#62;',
    '/r [message]',
    '/reload ',
    '/rollon [table name] &#60;-c [column name]&#62; &#60;-d dice&#62; &#60;-hide&#62;',
    '/save ',
    '/scaleui [50-200]',
    '/story [message]',
    '/version ',
    '/vote [message]',
    '/w [character] [message]',
]

OOC_AND_WHISPERS = [re.compile(r) for r in [
    r'\A\s*-(>|&#62;) [^:]+:',  # whispers
    r'\A\w+ \([\s\w]+\):',  # OOC
]]


def chunks_by_date(lines, encoding="utf8", display_crunch=False):
    line_group = []
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
            if timestamp_match.groups()[1]:
                year, month, day, hour, minute, *_ = timestamp_match.groups()
                second = 0
            else:
                _, _, _, _, _, month, day, year, hour, minute, second = timestamp_match.groups()

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

            if display_crunch and crunch:
                line_group.append("%s%s: %s%s" % (font_start, contents, crunch, font_end))
            else:
                line_group.append("%s%s%s" % (font_start, contents, font_end))

    if line_group:
        yield (line_group, current_timestamp)
