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
)
from docx2html.tests import (
    assert_html_equal,
    _TranslationTestCase,
    DOCUMENT_DRAWING_TEMPLATE,
    DOCUMENT_LI_TEMPLATE,
    DOCUMENT_PICT_TEMPLATE,
    DOCUMENT_PICT_NO_IMAGEID_TEMPLATE,
    DOCUMENT_P_TEMPLATE,
    DOCUMENT_TBL_TEMPLATE,
    DOCUMENT_TC_TEMPLATE,
    DOCUMENT_TR_TEMPLATE,
    DOCUMENT_XML_TEMPLATE,
)


def _create_li(text, ilvl, numId):
    return DOCUMENT_LI_TEMPLATE % {
        'text': text,
        'ilvl': ilvl,
        'numId': numId,
    }


def _create_table(num_rows, num_columns, text):
    def _create_tc(cell_value):
        return DOCUMENT_TC_TEMPLATE % {
            'text': cell_value,
        }

    def _create_tr(rows, text):
        tcs = ''
        for _ in range(rows):
            tcs += _create_tc(text.next())
        return DOCUMENT_TR_TEMPLATE % {
            'tcs': tcs,
        }

    trs = ''
    for _ in range(num_columns):
        trs += _create_tr(num_rows, text)
    return DOCUMENT_TBL_TEMPLATE % {
        'trs': trs,
    }


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
            lis += _create_li(text=text, ilvl=ilvl, numId=numId)

        xml = DOCUMENT_XML_TEMPLATE % {
            'body': lis,
        }
        return etree.fromstring(xml)

    def test_get_li_nodes(self):
        tree = self.get_xml()
        meta_data = self.get_meta_data()
        w_namespace = get_namespace(tree, 'w')
        first_p_tag = tree.find('%sp' % w_namespace)

        li_data = get_li_nodes(first_p_tag, meta_data)
        assert len(list(li_data)) == 3


class TableInListTestCase(_TranslationTestCase):
    expected_output = '''
        <html>
            <ol data-list-type="decimal">
                <li>AAA</li>
            </ol>
            <table>
                <tr>
                    <td>AAA</td>
                    <td>BBB</td>
                </tr>
                <tr>
                    <td>CCC</td>
                    <td>DDD</td>
                </tr>
            </table>
            <ol data-list-type="decimal">
                <li>BBB</li>
            </ol>
        </html>
    '''

    def get_xml(self):
        table = _create_table(num_rows=2, num_columns=2, text=chain(
            ['AAA'],
            ['BBB'],
            ['CCC'],
            ['DDD'],
        ))

        # Nest that table in a list.
        first_li = _create_li(text='AAA', ilvl=0, numId=1)
        second = _create_li(text='BBB', ilvl=0, numId=1)
        body = ''
        for el in [first_li, table, second]:
            body += el
        xml = DOCUMENT_XML_TEMPLATE % {
            'body': body,
        }
        return etree.fromstring(xml)

    def test_get_li_nodes_with_nested_table(self):
        # Create a table
        tree = self.get_xml()
        meta_data = self.get_meta_data()
        w_namespace = get_namespace(tree, 'w')
        first_p_tag = tree.find('%sp' % w_namespace)

        # Currently, the nest should be split (two lists instead of one with a
        # nested table in it)
        li_data = get_li_nodes(first_p_tag, meta_data)
        assert len(list(li_data)) == 1


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
        lis = ''
        for text, ilvl, numId in li_text:
            lis += _create_li(text=text, ilvl=ilvl, numId=numId)

        xml = DOCUMENT_XML_TEMPLATE % {
            'body': lis,
        }
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
                <img src="media/image1.jpeg" height="4" width="4"/>
            </p>
            <p>
                <img src="media/image2.jpeg" height="4" width="4"/>
            </p>
        </html>
    '''

    @staticmethod
    def image_handler(image_id, relationship_dict):
        return relationship_dict.get(image_id)

    def get_xml(self):
        drawing = DOCUMENT_DRAWING_TEMPLATE % {
            'r_id': 'rId0',
        }
        pict = DOCUMENT_PICT_TEMPLATE % {
            'r_id': 'rId1',
        }
        tags = [
            drawing,
            pict,
        ]
        body = ''
        for el in tags:
            body += el

        xml = DOCUMENT_XML_TEMPLATE % {
            'body': body,
        }
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
                    <img src="media/image1.jpeg" height="4" width="4"/>
                </p>
                <p>
                    <img src="media/image2.jpeg" height="6" width="6"/>
                </p>
            </html>
        ''')


class ListWithContinuationTestCase(_TranslationTestCase):
    expected_output = '''
        <html>
            <ol data-list-type="decimal">
                <li>AAA</li>
            </ol>
            <p>BBB</p>
            <ol data-list-type="decimal">
                <li>CCC</li>
            </ol>
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
            <ol data-list-type="decimal">
                <li>HHH</li>
            </ol>
        </html>
    '''

    def get_xml(self):
        table = _create_table(num_rows=2, num_columns=2, text=chain(
            ['DDD'],
            ['EEE'],
            ['FFF'],
            ['GGG'],
        ))
        tags = [
            _create_li(text='AAA', ilvl=0, numId=1),
            DOCUMENT_P_TEMPLATE % {
                'text': 'BBB',
            },
            _create_li(text='CCC', ilvl=0, numId=1),
            table,
            _create_li(text='HHH', ilvl=0, numId=1),
        ]
        body = ''
        for el in tags:
            body += el

        xml = DOCUMENT_XML_TEMPLATE % {
            'body': body,
        }
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
                <img src="media/image1.jpeg" height="4" width="4"/>
            </p>
        </html>
    '''

    @staticmethod
    def image_handler(image_id, relationship_dict):
        return relationship_dict.get(image_id)

    def get_xml(self):
        pict = DOCUMENT_PICT_TEMPLATE % {
            'r_id': 'rId0',
        }
        tags = [
            pict,
        ]
        body = ''
        for el in tags:
            body += el

        xml = DOCUMENT_XML_TEMPLATE % {
            'body': body,
        }
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


class PictImageTestCase(_TranslationTestCase):
    expected_output = '''
        <html/>
    '''

    def get_xml(self):
        pict = DOCUMENT_PICT_NO_IMAGEID_TEMPLATE
        tags = [
            pict,
        ]
        body = ''
        for el in tags:
            body += el

        xml = DOCUMENT_XML_TEMPLATE % {
            'body': body,
        }
        return etree.fromstring(xml)
