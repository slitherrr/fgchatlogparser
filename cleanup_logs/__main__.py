import re
from chunk_parser import chunks_by_date


def main(chatlog, output_directory):
    if os.path.exists(args.output_directory):
        sys.stderr.write("We can't put the output into a directory that already exists, delete it first", )
        sys.exit(1)

    os.mkdir(args.output_directory)

    for to_write, timestamp in chunks_by_date(args.chatlog):
        if to_write:
            logging.info("Writing file with timestamp %s" % timestamp)
            with open(os.path.join(args.output_directory, "%s.html" % timestamp), 'wb') as f:
                f.write(b"<!doctype html>\n<html><body><content>\n")
                for w in to_write:
                    f.write(w.encode("utf8"))
                    f.write(b"<br />\n")
                f.write(b"</content></body></html>\n")
        else:
            logging.info("Skipping %s because it would be empty" % timestamp)


if __name__ == "__main__":
    import argparse
    import logging
    import os
    import sys

    parser = argparse.ArgumentParser(description='Parse out a chatlog')
    parser.add_argument('chatlog', type=argparse.FileType('r'), help="An html file (with no root node) containing the log export from FGII")
    parser.add_argument('output_directory', type=str, nargs='?', default="chatlog_cleanup_output", help="A directory that doesn't exist yet to put the parsed logs into")
    parser.add_argument('--log', default='info', help="Logging level to display. Default is info. Valid values are all the ones allowed by the python logging library")
    parser.add_argument('--log-file', type=argparse.FileType('w'), default=sys.stdout, help="A filename to log to")
    args = parser.parse_args()
    logging.basicConfig(stream=args.log_file, level=getattr(logging, args.log.upper()))
    main(args.chatlog, args.output_directory)
