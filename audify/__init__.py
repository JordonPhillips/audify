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
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-filename', required=True)
    parser.add_argument('-o', '--output_filename', required=True)
    parser.add_argument('-v', '--voice', default='Amy')
    args = parser.parse_args()
    audify(
        input_filename=args.input_filename,
        output_filename=args.output_filename,
        voice=args.voice,
    )


def audify(input_filename, output_filename, voice):
    if input_filename == '-':
        audify_fileobj(sys.stdin, output_filename, voice)
    else:
        with open(input_filename) as f:
            audify_fileobj(f, output_filename, voice)


def audify_fileobj(fileobj, output_filename, voice):
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
