import io
import zipfile

from flask import abort, Blueprint, request, send_file
from cleanup_logs.chunk_parser import chunks_by_date

bp = Blueprint('process_log', __name__, url_prefix='/process_log')

@bp.route('/', methods=['POST'])
def index():
    file = request.files["file"]
    if not file:
        abort(404)

    encoding = file.mimetype_params.get("charset", "utf8")
    zipfile_stream = io.BytesIO()

    with zipfile.ZipFile(zipfile_stream, 'w') as zf:
        for chunk, datestamp in chunks_by_date(file, encoding):
            chunk_as_html = ['<!doctype html>', '<html><body><content>'] + [l + '<br>' for l in chunk] + ['</content></body></html>']
            zf.writestr('{}.html'.format(datestamp), '\n'.join(chunk_as_html).encode('utf8'))

    zipfile_stream.seek(0)

    return send_file(zipfile_stream, mimetype="application/zip", attachment_filename="parsed_logs.zip", as_attachment=True)
