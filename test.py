import unittest
import os
from transcript_process import TranscriptProcess


def get_iter_for_docx(path):
    for entry in os.scandir(path):
        if entry.is_file() and entry.name.split(".")[-1] == 'docx':
            yield entry.name


class TheOfficeTranscriptDataTestCase(unittest.TestCase):
    def setUp(self):
        self.tests_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tests', 'the_office')
        self.transcript_processor = TranscriptProcess(list(get_iter_for_docx(self.tests_dir)), 'the_office')

    def test_michael_style(self):
        blocks = self.transcript_processor._get_raw_blocks_list(os.path.join(self.tests_dir, 'michael.docx'))
        michael_style = self.transcript_processor._get_raw_block_data(blocks[0])[1:5]
        self.assertEqual(tuple(michael_style), (None, True, False, False))

    def test_pam_style(self):
        blocks = self.transcript_processor._get_raw_blocks_list(os.path.join(self.tests_dir, 'pam.docx'))
        pam_style = self.transcript_processor._get_raw_block_data(blocks[0])[1:5]
        self.assertEqual(tuple(pam_style), ('Comic Sans MS', False, False, False))


if __name__ == '__main__':
    unittest.main()