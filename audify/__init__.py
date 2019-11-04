#!/usr/bin/env python3
import argparse
import os
import shutil
import string
import sys
import tempfile
from pathlib import Path
from typing import List, Iterable, Any

import boto3
from pydub import AudioSegment

CHUNK_SIZE = 3000


def main():
    parser = argparse.ArgumentParser(
        description=(
            "A simple command line tool that uses Amazon Polly to convert text "
            "files into mp3 files."
        )
    )
    parser.add_argument(
        "-i",
        "--input-filename",
        required=True,
        help=(
            "The file containing the text to convert to speech. If - is "
            "provided, text will be read from stdin."
        ),
    )
    parser.add_argument(
        "-o",
        "--output-filename",
        required=True,
        help=("The output file name. This file will be in mp3 format."),
    )
    parser.add_argument(
        "-v",
        "--voice",
        default="Amy",
        help=(
            "The voice to read the text in. Any voice supported by Amazon "
            "Polly is valid. The default voice is Amy. Other voices can be "
            "found on the docs for Polly: "
            "https://docs.aws.amazon.com/polly/latest/dg/voicelist.html"
        ),
    )
    args = parser.parse_args()
    audify(
        input_filename=args.input_filename,
        output_filename=args.output_filename,
        voice=args.voice,
    )


def audify(input_filename: str, output_filename: str, voice: str):
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
    if input_filename == "-":
        audify_fileobj(sys.stdin, output_filename, voice)
    else:
        path = Path(input_filename)
        _audify(Path(input_filename), Path(output_filename), voice)


def audify_fileobj(fileobj: Any, output_filename: str, voice: str):
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
    with tempfile.TemporaryFile() as f:
        while data := fileobj.read(CHUNK_SIZE):
            f.write(data)
        _audify(Path(f.name), Path(output_filename), voice)


def _audify(
    input_file: Path, output_file: Path, voice: str, display_progress: bool = False,
):
    with tempfile.TemporaryDirectory() as tempdir:
        temp_path_dir = Path(tempdir)
        chunk_files = _audify_chunks(input_file, voice, temp_path_dir, display_progress)
        _stich_chunks(chunk_files, output_file, display_progress)


def _stich_chunks(chunk_files: List[Path], output_file: Path, display_progress: bool):
    audio = None
    for chunk_file in chunk_files:
        segment = AudioSegment.from_mp3(chunk_file)
        if audio is None:
            audio = segment
        else:
            audio = audio + segment

    if audio:
        audio.export(str(output_file), format="mp3")


def _audify_chunks(
    input_file: Path, voice: str, tempdir: Path, display_progress: bool
) -> List[Path]:
    polly = boto3.client("polly")
    chunk_files = []
    for i, chunk in enumerate(_read_input(input_file)):
        response = polly.synthesize_speech(
            OutputFormat="mp3", Text=chunk, VoiceId=voice
        )
        chunk_file = tempdir / ("%s.mp3" % i)
        chunk_file.write_bytes(response["AudioStream"].read())
        chunk_files.append(chunk_file)
    return chunk_files


def _read_input(input_file: Path, chunk_size: int = CHUNK_SIZE) -> Iterable[str]:
    with input_file.open() as fileobj:
        data = fileobj.read(chunk_size)

        while data:
            text, remainder = _rsplit_whitespace(data)
            size = chunk_size - len(remainder)
            yield text
            data = remainder + fileobj.read(size)


def _rsplit_whitespace(input_string: str):
    for i in range(len(input_string) - 1, 0, -1):
        if input_string[i] in string.whitespace:
            return input_string.rsplit(input_string[i], 1)


if __name__ == "__main__":
    main()
