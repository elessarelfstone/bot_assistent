import os
from dotenv import load_dotenv
import click
from transcript_process import TranscriptProcess
import utils

load_dotenv()


@click.command()
@click.argument('directory')
def main(directory):
    # docx_files = list(utils.get_iter_for_docx(path))
    transcriptor = TranscriptProcess(directory)
    transcriptor.process()

if __name__ == "__main__":
    main()