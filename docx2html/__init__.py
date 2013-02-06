import argparse
from docx2html.core import convert

__all__ = [
    convert.func_name,
]


def parse_args():
    parser = argparse.ArgumentParser(
        description='Convert OOXML docx files to html',
    )
    parser.add_argument(
        '--pretty-print',
        dest='pretty_print',
        action='store_true',
        default=False,
        help='Resulting html is printed pretty (easy to read)',
    )
    parser.add_argument(
        '--file',
        dest='filepath',
        type=str,
        required=True,
        help='Path to file for conversion',
    )
    parser.add_argument(
        '--to-file',
        dest='to_file',
        action='store_true',
        default=False,
        help='Save the output as a file',
    )

    return parser.parse_args()


def main():
    args = parse_args()
    filepath = args.filepath
    pretty_print = args.pretty_print
    to_file = args.to_file

    html = convert(filepath, pretty_print=pretty_print)
    if to_file:
        new_filepath = filepath[:-4] + 'html'
        with open(new_filepath, 'w') as f:
            f.write(html)
    else:
        print html


if __name__ == '__main__':
    main()
