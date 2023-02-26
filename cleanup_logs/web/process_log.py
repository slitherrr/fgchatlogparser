import io
import zipfile

from flask import abort, Blueprint, make_response, request, send_file
from cleanup_logs.chunk_parser import chunks_by_date
from cleanup_logs.calendar_export import each_event_from_string


bp = Blueprint('process_log', __name__, url_prefix='/process_log')


@bp.route('/chatlog', methods=['POST'])
def chatlog():
    if 'file' not in request.files:
        abort(404)

    file = request.files['file']
    display_crunch = request.values.get('display-crunch') == 'on'
    encoding = file.mimetype_params.get("charset", "utf8")
    zipfile_stream = io.BytesIO()

    with zipfile.ZipFile(zipfile_stream, 'w') as zf:
        for chunk, datestamp in chunks_by_date(file, encoding, display_crunch=display_crunch):
            chunk_as_html = ['<!doctype html>', '<html><body><content>'] + [l + '<br>' for l in chunk] + ['</content></body></html>']
            zf.writestr('{}.html'.format(datestamp), '\n'.join(chunk_as_html).encode('utf8'))

    zipfile_stream.seek(0)

    return send_file(zipfile_stream, mimetype="application/zip", download_name="parsed_logs.zip", as_attachment=True)


@bp.route('/calendar', methods=['POST'])
def calendar():
    if 'file' not in request.files:
        abort(404)

    file = request.files['file']
    zipfile_stream = io.BytesIO()
    encoding = file.mimetype_params.get("charset", "utf8")


    with zipfile.ZipFile(zipfile_stream, 'w') as zf:
        all_gm = []
        all_public = []

        for name, (year, month, day), gm, public in each_event_from_string(file.read()):
            if gm:
                all_gm.append('\n'.join([f'<div id={name} name={name}>', '<h3>', f'{year} - {month} - {day}', '</h3>', gm, '</div>']))

            if public:
                all_public.append('\n'.join([f'<div id={name} name={name}>', '<h3>', f'{year} - {month} - {day}', '</h3>', public, '</div>']))

        if not any([all_gm, all_public]):
            abort(make_response(f'No entries found in {file.name}', 404))

        if all_gm:
            print(repr(all_gm))
            gm_as_html = ['<!doctype html>', '<html><body><content>', *all_gm ,'</content></body></html>']
            zf.writestr('gm.html', '\n'.join(gm_as_html).encode(encoding))

        if all_public:
            print(repr(all_public))
            public_as_html = ['<!doctype html>', '<html><body><content>', *all_public ,'</content></body></html>']
            zf.writestr('public.html', '\n'.join(public_as_html).encode(encoding))

    zipfile_stream.seek(0)

    return send_file(zipfile_stream, mimetype="application/zip", download_name="calendar_entries.zip", as_attachment=True)
