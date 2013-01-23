from jinja2 import Environment, PackageLoader
from unittest import TestCase
import re

from docx2html.core import (
    MetaData,
    create_html,
)

env = Environment(
    loader=PackageLoader(
        'docx2html.tests',
        'templates',
    ),
)


def create_xml(body):
    template = env.get_template('base.xml')
    return template.render(body=body)


def create_p_tag(text, bold=False):
    if isinstance(text, str):
        # Use create a single r tag based on the text and the bold
        run_tag = create_r_tag(text, bold)
        run_tags = [run_tag]
    elif isinstance(text, list):
        run_tags = text
    else:
        raise AssertionError('text must be a string or a list')
    template = env.get_template('p.xml')

    kwargs = {
        'run_tags': run_tags,
    }
    return template.render(**kwargs)


def create_r_tag(text, is_bold=False):
    template = env.get_template('r.xml')
    kwargs = {
        'text': text,
        'is_bold': is_bold,
    }
    return template.render(**kwargs)


def create_hyperlink_tag(r_id, run_tags):
    template = env.get_template('hyperlink.xml')
    kwargs = {
        'r_id': r_id,
        'run_tags': run_tags,
    }
    return template.render(**kwargs)


def create_li(text, ilvl, numId, bold=False):
    if isinstance(text, str):
        # Use create a single r tag based on the text and the bold
        run_tag = create_r_tag(text, bold)
        run_tags = [run_tag]
    elif isinstance(text, list):
        run_tags = []
        for run_text, run_bold in text:
            run_tags.append(create_r_tag(run_tags, run_bold))
    else:
        raise AssertionError('text must be a string or a list')
    template = env.get_template('p.xml')

    kwargs = {
        'run_tags': run_tags,
        'is_list': True,
        'ilvl': ilvl,
        'numId': numId,
    }
    return template.render(**kwargs)


def create_table(num_rows, num_columns, text):

    def _create_tc(cell_value):
        template = env.get_template('tc.xml')
        return template.render(p_tag=cell_value)

    def _create_tr(rows, text):
        tcs = [_create_tc(text.next()) for _ in range(rows)]
        template = env.get_template('tr.xml')
        return template.render(tcs=tcs)

    trs = [_create_tr(num_rows, text) for _ in range(num_rows)]
    template = env.get_template('table.xml')
    return template.render(trs=trs)


def create_drawing(r_id):
    template = env.get_template('drawing.xml')
    return template.render(r_id=r_id)


def create_pict(r_id=None):
    template = env.get_template('pict.xml')
    return template.render(r_id=r_id)


def assert_html_equal(actual_html, expected_html):
    assert collapse_html(
        actual_html,
    ) == collapse_html(
        expected_html
    ), actual_html


def collapse_html(html):
    """
    Remove insignificant whitespace from the html.

    >>> print collapse_html('''\\
    ...     <h1>
    ...         Heading
    ...     </h1>
    ... ''')
    <h1>Heading</h1>
    >>> print collapse_html('''\\
    ...     <p>
    ...         Paragraph with
    ...         multiple lines.
    ...     </p>
    ... ''')
    <p>Paragraph with multiple lines.</p>
    """
    def smart_space(match):
        # Put a space in between lines, unless exactly one side of the line
        # break butts up against a tag.
        before = match.group(1)
        after = match.group(2)
        space = ' '
        if before == '>' or after == '<':
            space = ''
        return before + space + after
    # Replace newlines and their surrounding whitespace with a single space (or
    # empty string)
    html = re.sub(
        r'(>?)\s*\n\s*(<?)',
        smart_space,
        html,
    )
    return html.strip()


DEFAULT_NUMBERING_DICT = {
    '1': {
        0: 'decimal',
        1: 'decimal',
    },
    '2': {
        0: 'none',
        1: 'none',
    },
}
DEFAULT_RELATIONSHIP_DICT = {
    'rId3': 'fontTable.xml',
    'rId2': 'numbering.xml',
    'rId1': 'styles.xml',
}
DEFAULT_STYLES_DICT = {
    'style0': {
        'header': False,
        'font_size': '24',
        'based_on': None,
    },
}
DEFAULT_FONT_SIZES_DICT = {
    '24': None,
}


def image_handler(*args, **kwargs):
    return 'test'
DEFAULT_IMAGE_HANDLER = image_handler
DEFAULT_IMAGE_SIZES = {}


# This is a base test case defining methods to generate the xml and the meta
# data for each test case.
class _TranslationTestCase(TestCase):
    expected_output = None
    numbering_dict = DEFAULT_NUMBERING_DICT
    relationship_dict = DEFAULT_RELATIONSHIP_DICT
    styles_dict = DEFAULT_STYLES_DICT
    font_sizes_dict = DEFAULT_FONT_SIZES_DICT
    image_handler = DEFAULT_FONT_SIZES_DICT
    image_sizes = DEFAULT_IMAGE_SIZES

    def get_xml(self):
        raise NotImplementedError()

    def get_meta_data(self):
        return MetaData(
            numbering_dict=self.numbering_dict,
            relationship_dict=self.relationship_dict,
            styles_dict=self.styles_dict,
            font_sizes_dict=self.font_sizes_dict,
            image_handler=self.image_handler,
            image_sizes=self.image_sizes,
        )

    def test_expected_output(self):
        if self.expected_output is None:
            raise AssertionError('expected_output is not defined')

        # Create the xml
        tree = self.get_xml()
        meta_data = self.get_meta_data()

        # Verify the final output.
        html = create_html(tree, meta_data)

        assert_html_equal(html, self.expected_output)
