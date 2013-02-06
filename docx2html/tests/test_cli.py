import unittest
import subprocess


class CLITestCase(unittest.TestCase):
    def _call_cli(self, args):
        arguments = ' '.join(args)
        subprocess.call('docx2html %s' % arguments, shell=True)

    def test_no_args(self):
        self._call_cli([])
