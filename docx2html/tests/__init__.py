import re
from unittest import TestCase

from docx2html.core import (
    MetaData,
    create_html,
)

DOCUMENT_XML_TEMPLATE = """
<?xml version="1.0"?>
<w:document xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
        %(body)s
</w:document>
""".strip()

DOCUMENT_T_TEMPLATE = """
<w:t>%(text)s</w:t>
"""

DOCUMENT_P_TEMPLATE = """
    <w:p>
        <w:pPr>
            <w:pStyle w:val="style0"/>
        </w:pPr>
        <w:r>
            <w:rPr>
                %(bold)s
            </w:rPr>
            %(text)s
        </w:r>
    </w:p>
""".strip()

DOCUMENT_LI_TEMPLATE = """
    <w:p>
        <w:pPr>
            <w:pStyle w:val="style0"/>
            <w:numPr>
                <w:ilvl w:val="%(ilvl)d"/>
                <w:numId w:val="%(numId)d"/>
            </w:numPr>
        </w:pPr>
        <w:r>
            <w:rPr>
                %(bold)s
            </w:rPr>
            %(text)s
        </w:r>
    </w:p>
""".strip()

# Simple tc, no rowspan or colspans
DOCUMENT_TC_TEMPLATE = """
    <w:tc>
        <w:tcPr>
            <w:tcW w:type="dxa" w:w="4986"/>
            <w:tcBorders>
                <w:top w:color="000000" w:space="0" w:sz="2" w:val="single"/>
                <w:left w:color="000000" w:space="0" w:sz="2" w:val="single"/>
                <w:bottom w:color="000000" w:space="0" w:sz="2" w:val="single"/>
            </w:tcBorders>
            <w:shd w:fill="auto" w:val="clear"/>
            <w:tcMar>
                <w:top w:type="dxa" w:w="55"/>
                <w:left w:type="dxa" w:w="55"/>
                <w:bottom w:type="dxa" w:w="55"/>
                <w:right w:type="dxa" w:w="55"/>
            </w:tcMar>
        </w:tcPr>
        %(p_tag)s
    </w:tc>
""".strip()

DOCUMENT_TR_TEMPLATE = """
    <w:tr>
        <w:trPr>
            <w:cantSplit w:val="false"/>
        </w:trPr>
        %(tcs)s
    </w:tr>
""".strip()

DOCUMENT_TBL_TEMPLATE = """
    <w:tbl>
        <w:tblPr>
            <w:tblW w:type="dxa" w:w="9972"/>
            <w:jc w:val="left"/>
            <w:tblBorders>
                <w:top w:color="000000" w:space="0" w:sz="2" w:val="single"/>
                <w:left w:color="000000" w:space="0" w:sz="2" w:val="single"/>
                <w:bottom w:color="000000" w:space="0" w:sz="2" w:val="single"/>
            </w:tblBorders>
        </w:tblPr>
        <w:tblGrid>
            <w:gridCol w:w="4986"/>
            <w:gridCol w:w="4986"/>
        </w:tblGrid>
        %(trs)s
    </w:tbl>
""".strip()


DOCUMENT_DRAWING_TEMPLATE = """
    <w:p>
        <w:pPr>
            <w:pStyle w:val="style0"/>
        </w:pPr>
        <w:r>
            <w:rPr/>
            <w:drawing>
                <wp:anchor allowOverlap="1" behindDoc="0" distB="0" distL="0" distR="0" distT="0" layoutInCell="1" locked="0" relativeHeight="0" simplePos="0">
                    <wp:simplePos x="0" y="0"/>
                    <wp:positionH relativeFrom="column">
                        <wp:posOffset>2397125</wp:posOffset>
                    </wp:positionH>
                    <wp:positionV relativeFrom="paragraph">
                        <wp:posOffset>0</wp:posOffset>
                    </wp:positionV>
                    <wp:extent cx="1537970" cy="354965"/>
                    <wp:effectExtent b="0" l="0" r="0" t="0"/>
                    <wp:wrapSquare wrapText="largest"/>
                    <wp:docPr descr="A description..." id="1" name="Picture"/>
                    <wp:cNvGraphicFramePr>
                        <a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>
                    </wp:cNvGraphicFramePr>
                    <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
                        <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
                                <pic:nvPicPr>
                                    <pic:cNvPr descr="A description..." id="0" name="Picture"/>
                                    <pic:cNvPicPr>
                                        <a:picLocks noChangeArrowheads="1" noChangeAspect="1"/>
                                    </pic:cNvPicPr>
                                </pic:nvPicPr>
                                <pic:blipFill>
                                    <a:blip r:embed="%(r_id)s"/>
                                    <a:srcRect/>
                                    <a:stretch>
                                        <a:fillRect/>
                                    </a:stretch>
                                </pic:blipFill>
                                <pic:spPr bwMode="auto">
                                    <a:xfrm>
                                        <a:off x="0" y="0"/>
                                        <a:ext cx="1537970" cy="354965"/>
                                    </a:xfrm>
                                    <a:prstGeom prst="rect">
                                        <a:avLst/>
                                    </a:prstGeom>
                                    <a:noFill/>
                                    <a:ln w="9525">
                                        <a:noFill/>
                                        <a:miter lim="800000"/>
                                        <a:headEnd/>
                                        <a:tailEnd/>
                                    </a:ln>
                                </pic:spPr>
                            </pic:pic>
                        </a:graphicData>
                    </a:graphic>
                </wp:anchor>
            </w:drawing>
        </w:r>
    </w:p>
""".strip()


DOCUMENT_PICT_TEMPLATE = """
    <w:p w:rsidR="00E94BDC" w:rsidRPr="003638EA" w:rsidRDefault="00E94BDC" w:rsidP="00E94BDC">
        <w:pPr>
            <w:rPr>
                <w:color w:val="000000"/>
            </w:rPr>
        </w:pPr>
        <w:r w:rsidR="00360165">
            <w:rPr>
                <w:b/>
                <w:color w:val="000000"/>
            </w:rPr>
            <w:pict>
                <v:shape id="_x0000_i1027" type="#_x0000_t75" style="width:99.75pt;height:116.25pt">
                    <v:imagedata r:id="%(r_id)s" o:title="New Picture"/>
                </v:shape>
            </w:pict>
        </w:r>
    </w:p>
""".strip()


DOCUMENT_PICT_NO_IMAGEID_TEMPLATE = """
    <w:p w:rsidR="00E94BDC" w:rsidRPr="003638EA" w:rsidRDefault="00E94BDC" w:rsidP="00E94BDC">
        <w:pPr>
            <w:rPr>
                <w:color w:val="000000"/>
            </w:rPr>
        </w:pPr>
        <w:r w:rsidR="00360165">
            <w:rPr>
                <w:b/>
                <w:color w:val="000000"/>
            </w:rPr>
            <w:pict>
                <v:shape id="_x0000_i1027" type="#_x0000_t75" style="width:99.75pt;height:116.25pt">
                </v:shape>
            </w:pict>
        </w:r>
    </w:p>
""".strip()


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
