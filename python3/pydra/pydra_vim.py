import vim
import subprocess as sp

from .models.imprt import (
    ImportSentence,
    ImportAsPart,
)


def test_function() -> str:
    #  lines = vim.current.buffer[:]
    file_path = vim.current.buffer.name

    # Execute flake8
    flake8_job = sp.run(
        'flake8 {}'.format(file_path),
        shell=True,
        stdout=sp.PIPE,
        stderr=sp.DEVNULL,
    )

    # Extract result
    _ = flake8_job.stdout.decode('utf-8')

    # construct sentence
    import_sentence_to_be_added = ImportSentence(
        'pprint',
        [
            ImportAsPart('pprint', 'pp'),
        ],
    )
    vim.current.buffer[:0] = [str(import_sentence_to_be_added)]
    return ''
