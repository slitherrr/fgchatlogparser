import io

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
        attachment_filename = Path(file.filename).with_suffix('.wiki')
    else:
        attachment_filename = 'character.wiki'

    return_as_file = request.values.get('download') == 'on'
    encoding = file.mimetype_params.get('charset', None)
    result = parse_to_wiki_from_io(file, from_encoding=encoding)

    if return_as_file:
        return_stream = io.BytesIO(result.encode("utf-8"))
        return send_file(
            return_stream,
            mimetype="application/zip",
            download_name=str(attachment_filename),
            as_attachment=return_as_file,
        )
    else:
        resp = make_response(result, 200)
        resp.headers['content-type'] = 'text/plain'
        return resp
