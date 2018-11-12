from docx import Document
import json
import os
import classes
import pymysql
from assistant_db import AssistantDB
import utils


class TranscriptProcess():
    def __init__(self, directory):
        # getting real path for movie's directory
        self.path = os.path.join(os.getenv('DATA_DIR'), directory)
        # getting real path for movie's settings file
        settings_file = os.path.join(self.path, 'movie.json')
        # stat_path = os.path.join(os.getenv('DATA_DIR'), directory, 'processed.stat')
        # getting real path for stat file

        self.docx_files = list(self._get_iter_for_docx(self.path))
        with open(settings_file, "r") as file:
            self.movie_json = json.load(file)
        self.name = self.movie_json["name"]
        self._styles = self._get_characters_styles()
        self._db = AssistantDB(
            os.getenv('DB_HOST'),
            os.getenv('DB_USER'),
            os.getenv('DB_PASS'),
            os.getenv('DB_NAME')
            )

    def _get_iter_for_docx(path):
        for entry in os.scandir(path):
            if entry.is_file() and entry.name.split(".")[-1] == 'docx':
                yield os.path.join(path, entry.name)

    def _get_font(self, raw_block):
        """ gets text's font
        """
        fonts = [raw_block.style.font.name] + [run.font.name for run in raw_block.runs]
        fonts = list(filter(bool, fonts))
        return fonts[0] if len(fonts) else None

    def _is_bold(self, raw_block):
        """ checks if block's text is bold
        """
        font_bolds = [raw_block.style.font.bold] + [run.font.bold for run in raw_block.runs]
        font_bolds = list(filter(bool, font_bolds))
        return True if len(font_bolds) else False

    def _is_italic(self, raw_block):
        """ checks if block's text is italic
        """
        font_italic = [raw_block.style.font.italic] + [run.font.italic for run in raw_block.runs]
        font_italic = list(filter(bool, font_italic))
        return True if len(font_italic) else False

    def _is_underline(self, raw_block):
        """ checks if block's text is underline
        """
        font_underline = [raw_block.style.font.underline] + [run.font.underline for run in raw_block.runs]
        font_underline = list(filter(bool, font_underline))
        return True if len(font_underline) else False

    def _get_raw_blocks_list(self, docx_file):
        """ gets blocks of transcript, it could be dialog or monolog
        """
        document = Document(docx_file)
        parsed_blocks = []
        buf = []
        parsed_blocks.append(buf)
        for paragraph in document.paragraphs:
            if paragraph.text:
                buf.append(paragraph)
            else:
                buf = []
                parsed_blocks.append(buf)
        parsed_blocks = list(filter(lambda x: len(x), parsed_blocks))
        return parsed_blocks

    def _get_raw_block_data(self, raw_block):
        """ gets concatenated text of block and its style info

        """
        text = '\n'.join(item.text for item in raw_block)
        font = self._get_font(raw_block[0])
        is_bold = self._is_bold(raw_block[0])
        is_italic = self._is_italic(raw_block[0])
        is_underline = self._is_underline(raw_block[0])
        return text, font, is_bold, is_italic, is_underline

    def _get_characters_styles(self):
        """ gets personal characters style from movie settings(json)
        """
        template = classes.Speech()
        styles = []
        for character, props in self.movie_json["styles"].items():
            buf = {**{"font": None, "is_bold": False, "is_italic": False, "is_underline": False}, **props}
            buf["character"] = character
            styles.append({key: buf[key] for key in sorted(buf.keys())})
        # print(styles)
        return styles

    def _get_character_of_speech(self, block_data):
        """ gets character for monolog, if it's dialog returns None
        """
        excl_keys = {"character", "text"}
        character = None
        for item in self._styles:
            ch_style = {key: item[key] for key in item if key not in excl_keys}
            if block_data == tuple([ch_style['font'], ch_style['is_bold'], ch_style['is_italic'], ch_style['is_underline']]):
                character = item['character']
        return character

    def get_blocks_data(self):
        """ gets generator for retrieveing prepared pieces of transcript as Speech's class instant
        """
        for file in self.docx_files:
            if not  os.path.basename(file) in self.processed_files:
                blocks = self._get_raw_blocks_list(file)
                for block in blocks:
                    tmp_data = self._get_raw_block_data(block)
                    character = self._get_character_of_speech(tmp_data[1:5])
                    yield tmp_data[0], character

    def process(self):
        try:
            flag = False
            for body, character in self.get_blocks_data():
                # print(body, character)
                if character:
                    self._db.add_transcript((body, "{0} - {1}".format(self.name, character)))
                else:
                    self._db.add_transcript((body, "{0}".format(self.name)))
            self._db.commit()
            flag = True
        finally:
            if flag:
                with open(os.path.join(self.path, 'processed.stat'), "a") as file:
                    for docx in self.docx_files:
                        file.write(os.path.basename(docx+"\n"))