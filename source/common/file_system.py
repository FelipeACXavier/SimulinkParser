import os
import sys
import shutil
import subprocess

from common.logging import *
from zipfile import ZipFile
from urllib.request import urlretrieve
from common.result import VoidResult


def download_file(url: str, file: str) -> VoidResult:
    LOG_TRACE(f'Downloading: {url} to {file}')
    try:
        urlretrieve(url, file)
    except Exception as e:
        return VoidResult.failed(e.message)

    return VoidResult()


def extract_archive(in_file: str, out_dir: str) -> VoidResult:
    LOG_TRACE(f'Extracting: {in_file} to {out_dir}')
    try:
        with ZipFile(in_file, 'r') as zObject:
            zObject.extractall(path=out_dir)
    except Exception as e:
        return VoidResult.failed(e.message)

    return VoidResult()


def copy_archive(src: str, dst: str) -> VoidResult:
    try:
        if os.path.isdir(src):
            LOG_TRACE(f'Source: {src} is a directory')

            os.makedirs(os.path.dirname(dst), exist_ok=True)

            for filename in os.listdir(src):
                source_file = os.path.join(src, filename)
                destination_file = os.path.join(dst, filename)

                LOG_TRACE(f'Copying {source_file} to {destination_file}')
                if os.path.isfile(source_file):
                    shutil.copy(source_file, destination_file)
                else:
                    shutil.copytree(source_file, destination_file)

        elif os.path.isdir(dst):
            LOG_TRACE(f'Destination {dst} is a directory')
            source_file = os.path.basename(src)
            destination_file = os.path.join(dst, source_file)
            shutil.copy(src, destination_file)
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
    except Exception as e:
        return VoidResult.failed(e.message)

    return VoidResult()


def run_command(command, tail=True):
    LOG_TRACE(command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    if tail:
        with process.stdout as pipe:
            for line in iter(pipe.readline, b''):
                print(line.decode("utf-8"), end='')

    process.wait()
    if process.returncode != 0:
        return VoidResult.failed(f'Failed to run command {command}')

    return VoidResult()


def create_dir(dir_name):
    try:
        os.makedirs(dir_name)
    except FileExistsError as e:
        pass


def exists(file_name):
    return os.path.exists(file_name)


def is_directory_empty(dir_name):
    return not os.path.isdir(dir_name) or not os.listdir(dir_name)


def to_absolute_path(path):
    if os.path.isabs(path):
        return path

    return os.path.abspath(path)


def current_dir():
    return os.getcwd()


def remove_file(file):
    if exists(file):
        os.remove(file)
