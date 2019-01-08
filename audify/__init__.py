#!/usr/bin/env python
import argparse
import os
import shutil
import string
import sys
import tempfile

import boto3
from pydub import AudioSegment


def main():
    parser = argparse.ArgumentParser(description=(
        'A simple command line tool that uses Amazon Polly to convert text '
        'files into mp3 files.'
    ))
    parser.add_argument(
        '-i', '--input-filename', required=True,
        help=(
            'The file containing the text to convert to speech. If - is '
            'provided, text will be read from stdin.'
        )
    )
    parser.add_argument(
        '-o', '--output-filename', required=True,
        help=(
            'The output file name. This file will be in mp3 format.'
        )
    )
    parser.add_argument(
        '-v', '--voice', default='Amy',
        help=(
            'The voice to read the text in. Any voice supported by Amazon '
            'Polly is valid. The default voice is Amy. Other voices can be '
            'found on the docs for Polly: '
            'https://docs.aws.amazon.com/polly/latest/dg/voicelist.html'
        )
    )
    args = parser.parse_args()
    audify(
        input_filename=args.input_filename,
        output_filename=args.output_filename,
        voice=args.voice,
    )


def audify(input_filename, output_filename, voice):
    """Convert a text file into spoken mp3 file.

    :param input_filename: A text file to convert.
    :type input_filename: str

    :param output_filename: The name of the resulting mp3 file.
    :type output_filename: str

    :param voice: The voice to read the text in. Any voice supported by Amazon
        Polly is valid. The default voice is Amy. Other voices can be found on
        the docs for Polly:
        https://docs.aws.amazon.com/polly/latest/dg/voicelist.html
    :type voice: str
    """
    if input_filename == '-':
        audify_fileobj(sys.stdin, output_filename, voice)
    else:
        with open(input_filename) as f:
            audify_fileobj(f, output_filename, voice)


def audify_fileobj(fileobj, output_filename, voice):
    """Convert a file-like object containing text into spoken mp3 file.

    :param fileobj: A file-like object containg text to convert.
    :type fileobj: file-like object

    :param output_filename: The name of the resulting mp3 file.
    :type output_filename: str

    :param voice: The voice to read the text in. Any voice supported by Amazon
        Polly is valid. The default voice is Amy. Other voices can be found on
        the docs for Polly:
        https://docs.aws.amazon.com/polly/latest/dg/voicelist.html
    :type voice: str
    """
    tempdir = tempfile.mkdtemp()
    try:
        chunk_files = _audify_chunks(fileobj, voice, tempdir)
        _stich_chunks(chunk_files, output_filename)
    finally:
        shutil.rmtree(tempdir)


def _stich_chunks(chunk_files, output_filename):
    audio = None
    for chunk_file in chunk_files:
        segment = AudioSegment.from_mp3(chunk_file)
        if audio is None:
            audio = segment
        else:
            audio = audio + segment

    if audio:
        audio.export(output_filename, format='mp3')

def _audify_chunks(fileobj, voice, tempdir):
    polly = boto3.client('polly')
    chunk_files = []
    for i, chunk in enumerate(_read_input(fileobj)):
        filename = os.path.join(tempdir, '%s.mp3' % i)
        response = polly.synthesize_speech(
            OutputFormat='mp3',
            Text=chunk,
            VoiceId=voice,
        )
        with open(filename, 'wb') as f:
            f.write(response['AudioStream'].read())
        chunk_files.append(filename)
    return chunk_files


def _read_input(fileobj, chunk_size=3000):
    data = fileobj.read(chunk_size)

    while data:
        text, remainder = _rsplit_whitespace(data)
        size = chunk_size - len(remainder)
        yield text
        data = remainder + fileobj.read(size)


def _rsplit_whitespace(input_string):
    for i in range(len(input_string) - 1, 0, -1):
        if input_string[i] in string.whitespace:
            return input_string.rsplit(input_string[i], 1)


if __name__ == "__main__":
    main()
