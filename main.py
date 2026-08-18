import argparse

from card import Card


def main():
    parser = argparse.ArgumentParser(
        description='Pack the file with metadata to the card and '
                    'unpack the card to the file and metadata'
    )

    subparsers = parser.add_subparsers(dest='method')

    pack_parser = subparsers.add_parser('pack')
    pack_parser.add_argument('file_path')
    pack_parser.add_argument('metadata')
    pack_parser.add_argument('-o', '--output')

    unpack_parser = subparsers.add_parser('unpack')
    unpack_parser.add_argument('card_path')
    unpack_parser.add_argument('-m', '--manifest', action='store_true')
    unpack_parser.add_argument('-o', '--output')

    args = parser.parse_args()

    try:
        if args.method == 'pack':
            Card.pack(args.file_path, args.metadata, args.output)
        elif args.method == 'unpack':
            manifest = Card.unpack(args.card_path, args.output)
            if args.manifest:
                print(f"Version:".ljust(10), manifest.version)
                print(f"Hash:".ljust(10), manifest.hash)
                print(f"Extension:".ljust(10), manifest.extension)
                print(f"Metadata:".ljust(10), manifest.metadata)
        else:
            raise ValueError('unknown method')
    except Exception as e:
        print(f'Failed to {args.method}: {e}')


if __name__ == "__main__":
    main()
