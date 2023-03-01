from . import parse_to_wiki_from_io


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("gimme a filename plz")
        sys.exit(1)

    with open(sys.argv[1], 'rb') as fr:
        sys.stdout.write('\n---\n'.join(sheet for (_, sheet) in parse_to_wiki_from_io(fr)))
