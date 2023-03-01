import io
import zipfile

from pathlib import Path
from flask import abort, Blueprint, make_response, request, send_file
from fg2wiki import parse_to_wiki_from_io


bp = Blueprint('fg2wiki', __name__, url_prefix='/fg2wiki')


@bp.route('/convert', methods=['POST'])
def towiki():
    if 'file' not in request.files:
        abort(404)

    file = request.files['file']
    if file.filename:
        req_filename = Path(file.filename)
    else:
        req_filename = Path('character.xml')

    return_as_file = request.values.get('download') == 'on'
    encoding = file.mimetype_params.get('charset', None)
    result = parse_to_wiki_from_io(file.stream, from_encoding=encoding)

    if not result:
        resp = make_response("No character detected", 200)
        resp.headers['content-type'] = 'text/plain'
        return resp

    if return_as_file:
        if len(result) == 1:
            name, sheet = result[0]
            return_stream = io.BytesIO(sheet.encode("utf-8"))
            attachment_filename = f'{name}.wiki'
            mimetype = "text/plain"
        else:
            return_stream = io.BytesIO()

            with zipfile.ZipFile(return_stream, 'w') as zf:
                for name, sheet in result:
                    zf.writestr(f'{name}.wiki', sheet.encode('utf-8'))

            return_stream.seek(0)

            attachment_filename = req_filename.with_suffix('.zip')
            mimetype = "application/zip"

        return send_file(
            return_stream,
            mimetype=mimetype,
            download_name=str(attachment_filename),
            as_attachment=return_as_file,
        )
    else:
        resptext = '\n---\n'.join(sheet for (_, sheet) in result)
        resp = make_response(resptext, 200)
        resp.headers['content-type'] = 'text/plain'
        return resp
