from . import parse_to_wiki_from_io


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("gimme a filename plz")
        sys.exit(1)

    with open(sys.argv[1]) as fr:
        sys.stdout.write(parse_to_wiki_from_io(fr))
