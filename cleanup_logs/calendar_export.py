from defusedxml.ElementTree import fromstring, tostring

def each_event_from_string(source):
    root = fromstring(source)
    logs = root.find('.//calendar/log')
    if not logs:
        return 'OK'

    for maybe_logentry in logs:
        if maybe_logentry.tag.startswith('id-'):
            day = maybe_logentry.find('./day').text
            month = maybe_logentry.find('./month').text
            year = maybe_logentry.find('./year').text
            name = maybe_logentry.find('./name').text
            gm = maybe_logentry.find('./gmlogentry')
            public = maybe_logentry.find('./logentry')

            if gm:
                gm.tag = "div"
                gm.attrib.clear()

            if public:
                public.tag = "div"
                public.attrib.clear()

            yield name, (year, month, day), tostring(gm, encoding='unicode'), tostring(public, encoding='unicode')
