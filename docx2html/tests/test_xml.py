import mock
from itertools import chain
from lxml import etree
from copy import copy

from docx2html.core import (
    _is_top_level_upper_roman,
    create_html,
    get_image_id,
    get_li_nodes,
    get_namespace,
    is_last_li,
)
from docx2html.tests.document_builder import DocxBuilder as DXB
from docx2html.tests import (
    _TranslationTestCase,
    assert_html_equal,
)


class SimpleListTestCase(_TranslationTestCase):
    expected_output = '''
        <html>
            <ol data-list-type="decimal">
                <li>AAA</li>
                <li>BBB</li>
                <li>CCC</li>
            </ol>
        </html>
    '''

    def get_xml(self):
        li_text = [
            ('AAA', 0, 1),
            ('BBB', 0, 1),
            ('CCC', 0, 1),
        ]
        lis = ''
        for text, ilvl, numId in li_text:
            lis += DXB.li(text=text, ilvl=ilvl, numId=numId)

        xml = DXB.xml(lis)
        return etree.fromstring(xml)

    def test_get_li_nodes(self):
        tree = self.get_xml()
        meta_data = self.get_meta_data()
        w_namespace = get_namespace(tree, 'w')
        first_p_tag = tree.find('%sp' % w_namespace)

        li_data = get_li_nodes(first_p_tag, meta_data)
        assert len(list(li_data)) == 3

    def test_is_last_li(self):
        tree = self.get_xml()
        meta_data = self.get_meta_data()
        p_tags = tree.xpath('.//w:p', namespaces=tree.nsmap)
        result = [is_last_li(p, meta_data, current_numId='1') for p in p_tags]
        self.assertEqual(
            result,
            [False, False, True],
        )


class TableInListTestCase(_TranslationTestCase):
    expected_output = '''
        <html>
            <ol data-list-type="decimal">
                <li>AAA<br />
                    <table>
                        <tr>
                            <td>BBB</td>
                            <td>CCC</td>
                        </tr>
                        <tr>
                            <td>DDD</td>
                            <td>EEE</td>
                        </tr>
                    </table>
                </li>
                <li>FFF</li>
            </ol>
            <p>GGG</p>
        </html>
    '''

    def get_xml(self):
        table = DXB.table(num_rows=2, num_columns=2, text=chain(
            [DXB.p_tag('BBB')],
            [DXB.p_tag('CCC')],
            [DXB.p_tag('DDD')],
            [DXB.p_tag('EEE')],
        ))

        # Nest that table in a list.
        first_li = DXB.li(text='AAA', ilvl=0, numId=1)
        second = DXB.li(text='FFF', ilvl=0, numId=1)
        p_tag = DXB.p_tag('GGG')

        body = ''
        for el in [first_li, table, second, p_tag]:
            body += el
        xml = DXB.xml(body)
        return etree.fromstring(xml)

    def test_get_li_nodes_with_nested_table(self):
        # Create a table
        tree = self.get_xml()
        meta_data = self.get_meta_data()
        w_namespace = get_namespace(tree, 'w')
        first_p_tag = tree.find('%sp' % w_namespace)

        # Show that list nesting deals with the table nesting
        li_data = get_li_nodes(first_p_tag, meta_data)
        assert len(list(li_data)) == 3

    def test_is_last_li(self):
        tree = self.get_xml()
        meta_data = self.get_meta_data()
        result = [is_last_li(el, meta_data, current_numId='1') for el in tree]
        self.assertEqual(
            result,
            # None list items are ignored
            [False, False, True, False],
        )


class RomanNumeralToHeadingTestCase(_TranslationTestCase):
    numbering_dict = {
        '1': {
            0: 'upperRoman',
            1: 'decimal',
            2: 'upperRoman',
        }
    }
    expected_output = '''
        <html>
            <h2>AAA</h2>
            <ol data-list-type="decimal">
                <li>BBB</li>
            </ol>
            <h2>CCC</h2>
            <ol data-list-type="decimal">
                <li>DDD</li>
            </ol>
            <h2>EEE</h2>
            <ol data-list-type="decimal">
                <li>FFF
                    <ol data-list-type="upper-roman">
                        <li>GGG</li>
                    </ol>
                </li>
            </ol>
        </html>
    '''

    def get_xml(self):
        li_text = [
            ('AAA', 0, 1),
            ('BBB', 1, 1),
            ('CCC', 0, 1),
            ('DDD', 1, 1),
            ('EEE', 0, 1),
            ('FFF', 1, 1),
            ('GGG', 2, 1),
        ]
        body = ''
        for text, ilvl, numId in li_text:
            body += DXB.li(text=text, ilvl=ilvl, numId=numId)

        xml = DXB.xml(body)
        return etree.fromstring(xml)

    def test_is_top_level_upper_roman(self):
        tree = self.get_xml()
        w_namespace = get_namespace(tree, 'w')
        meta_data = self.get_meta_data()

        result = []
        for p in tree.findall('%sp' % w_namespace):
            result.append(
                _is_top_level_upper_roman(p, meta_data)
            )
        self.assertEqual(
            result,
            [
                True,  # AAA
                False,  # BBB
                True,  # CCC
                False,  # DDD
                True,  # EEE
                False,  # FFF
                False,  # GGG - notice this is upper roman but not in the root
            ]
        )


class RomanNumeralToHeadingAllBoldTestCase(_TranslationTestCase):
    numbering_dict = {
        '1': {
            0: 'upperRoman',
        }
    }
    expected_output = '''
        <html>
            <h2>AAA</h2>
            <h2>BBB</h2>
            <h2>CCC</h2>
        </html>
    '''

    def get_xml(self):
        li_text = [
            ('AAA', 0, 1),
            ('BBB', 0, 1),
            ('CCC', 0, 1),
        ]
        body = ''
        for text, ilvl, numId in li_text:
            body += DXB.li(text=text, ilvl=ilvl, numId=numId, bold=True)

        xml = DXB.xml(body)
        return etree.fromstring(xml)


class ImageTestCase(_TranslationTestCase):
    relationship_dict = {
        'rId0': 'media/image1.jpeg',
        'rId1': 'media/image2.jpeg',
    }
    image_sizes = {
        'rId0': (4, 4),
        'rId1': (4, 4),
    }
    expected_output = '''
        <html>
            <p>
                <img src="media/image1.jpeg" height="4" width="4" />
            </p>
            <p>
                <img src="media/image2.jpeg" height="4" width="4" />
            </p>
        </html>
    '''

    @staticmethod
    def image_handler(image_id, relationship_dict):
        return relationship_dict.get(image_id)

    def get_xml(self):
        drawing = DXB.drawing('rId0')
        pict = DXB.pict('rId1')
        tags = [
            drawing,
            pict,
        ]
        body = ''
        for el in tags:
            body += el

        xml = DXB.xml(body)
        return etree.fromstring(xml)

    def test_get_image_id(self):
        tree = self.get_xml()
        els = []
        w_namespace = get_namespace(tree, 'w')
        for el in tree.iter():
            if el.tag == '%sdrawing' % w_namespace:
                els.append(el)
            if el.tag == '%spict' % w_namespace:
                els.append(el)
        image_ids = []
        for el in els:
            image_ids.append(get_image_id(el))
        self.assertEqual(
            image_ids,
            [
                'rId0',
                'rId1',
            ]
        )

    @mock.patch('docx2html.core._get_image_size_from_image')
    def test_missing_size(self, patched_item):
        def side_effect(*args, **kwargs):
            return (6, 6)
        patched_item.side_effect = side_effect
        tree = self.get_xml()
        meta_data = copy(self.get_meta_data())
        del meta_data.image_sizes['rId1']

        html = create_html(tree, meta_data)

        # Show that the height and width were grabbed from the actual image.
        assert_html_equal(html, '''
            <html>
                <p>
                    <img src="media/image1.jpeg" height="4" width="4" />
                </p>
                <p>
                    <img src="media/image2.jpeg" height="6" width="6" />
                </p>
            </html>
        ''')


class ListWithContinuationTestCase(_TranslationTestCase):
    expected_output = '''
        <html>
            <ol data-list-type="decimal">
                <li>AAA<br />BBB</li>
                <li>CCC<br />
                    <table>
                        <tr>
                            <td>DDD</td>
                            <td>EEE</td>
                        </tr>
                        <tr>
                            <td>FFF</td>
                            <td>GGG</td>
                        </tr>
                    </table>
                </li>
                <li>HHH</li>
            </ol>
        </html>
    '''

    def get_xml(self):
        table = DXB.table(num_rows=2, num_columns=2, text=chain(
            [DXB.p_tag('DDD')],
            [DXB.p_tag('EEE')],
            [DXB.p_tag('FFF')],
            [DXB.p_tag('GGG')],
        ))
        tags = [
            DXB.li(text='AAA', ilvl=0, numId=1),
            DXB.p_tag('BBB'),
            DXB.li(text='CCC', ilvl=0, numId=1),
            table,
            DXB.li(text='HHH', ilvl=0, numId=1),
        ]
        body = ''
        for el in tags:
            body += el

        xml = DXB.xml(body)
        return etree.fromstring(xml)


class PictImageTestCase(_TranslationTestCase):
    relationship_dict = {
        'rId0': 'media/image1.jpeg',
    }
    image_sizes = {
        'rId0': (4, 4),
    }
    expected_output = '''
        <html>
            <p>
                <img src="media/image1.jpeg" height="4" width="4" />
            </p>
        </html>
    '''

    @staticmethod
    def image_handler(image_id, relationship_dict):
        return relationship_dict.get(image_id)

    def get_xml(self):
        pict = DXB.pict('rId0')
        tags = [
            pict,
        ]
        body = ''
        for el in tags:
            body += el

        xml = DXB.xml(body)
        return etree.fromstring(xml)

    def test_image_id_for_pict(self):
        tree = self.get_xml()

        # Get all the pict tags
        pict_tags = tree.xpath('.//w:pict', namespaces=tree.nsmap)
        self.assertEqual(len(pict_tags), 1)

        # Get the image id for the pict tag.
        pict_tag = pict_tags[0]
        image_id = get_image_id(pict_tag)
        self.assertEqual(image_id, 'rId0')


class PictImageMissingIdTestCase(_TranslationTestCase):
    expected_output = '''
        <html></html>
    '''

    def get_xml(self):
        pict = DXB.pict(None)
        tags = [
            pict,
        ]
        body = ''
        for el in tags:
            body += el

        xml = DXB.xml(body)
        return etree.fromstring(xml)


class TableWithInvalidTag(_TranslationTestCase):
    expected_output = '''
        <html>
            <table>
                <tr>
                    <td>AAA</td>
                    <td>BBB</td>
                </tr>
                <tr>
                    <td></td>
                    <td>DDD</td>
                </tr>
            </table>
        </html>
    '''

    def get_xml(self):
        table = DXB.table(num_rows=2, num_columns=2, text=chain(
            [DXB.p_tag('AAA')],
            [DXB.p_tag('BBB')],
            # This tag may have CCC in it, however this tag has no meaning
            # pertaining to content.
            ['<w:invalidTag>CCC</w:invalidTag>'],
            [DXB.p_tag('DDD')],
        ))
        body = table
        xml = DXB.xml(body)
        return etree.fromstring(xml)


class HyperlinkStyledTestCase(_TranslationTestCase):
    relationship_dict = {
        'rId0': 'www.google.com',
    }

    expected_output = '''
    <html>
        <p><a href="www.google.com">link</a>.</p>
    </html>
    '''

    def get_xml(self):
        run_tags = []
        run_tags.append(DXB.r_tag('link', is_bold=True))
        run_tags = [DXB.hyperlink_tag(r_id='rId0', run_tags=run_tags)]
        run_tags.append(DXB.r_tag('.', is_bold=False))
        body = DXB.p_tag(run_tags)
        xml = DXB.xml(body)
        return etree.fromstring(xml)


class HyperlinkVanillaTestCase(_TranslationTestCase):
    relationship_dict = {
        'rId0': 'www.google.com',
    }

    expected_output = '''
    <html>
        <p><a href="www.google.com">link</a>.</p>
    </html>
    '''

    def get_xml(self):
        run_tags = []
        run_tags.append(DXB.r_tag('link', is_bold=False))
        run_tags = [DXB.hyperlink_tag(r_id='rId0', run_tags=run_tags)]
        run_tags.append(DXB.r_tag('.', is_bold=False))
        body = DXB.p_tag(run_tags)
        xml = DXB.xml(body)
        return etree.fromstring(xml)
