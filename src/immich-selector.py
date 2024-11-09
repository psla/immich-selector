import argparse
import json
import os
from collections import Counter
from itertools import groupby

# Example invocation:
# python immich-selector.py  -i ~/b395bdc8-7e03-4e3b-8e33-681e3bb5e859.json -d /mnt/nas/public/wspolne/Projekty/2023-2024/2024-02_Las_Vegas/media/
def main():
    parser = argparse.ArgumentParser(description='This program accepts json input from API output from immich, makes symlinks to the files in the desired directories, with filenames corresponding to timestamps')
    parser.add_argument('-i', '--input', type=str, help='File name with immich json file', required=True)
    parser.add_argument('-d', '--destination', type=str, help='Where to place all the symlinks', required=True)
    parser.add_argument('-r', '--old_prefix', type=str, default='/mnt/media', help="A prefix that should be replaced in the path")
    parser.add_argument('-a', '--new_prefix', type=str, default='/mnt/nas/public/wspolne', help="A new prefix that should be placed in the path")
    parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')

    args = parser.parse_args()

    if args.verbose:
        print('Verbose mode enabled')

    print(f'Parsing, {args.input}!')
    
    data = parse_input(args.input)
    file_paths = list(map(lambda asset: asset['originalPath'], data['assets']))
    print(f'Verifying all files come from {args.old_prefix}.')
    corrected_file_paths = list(map(lambda path: replace_prefix(path, args.old_prefix, args.new_prefix), file_paths))
    print(f'Verifying access to files.')
    verify_all_paths_present(corrected_file_paths)
    files_with_timestamps = list(map(lambda x: { 'path': x[1], 'local_timestamp': create_filename(data['assets'][x[0]]) }, enumerate(corrected_file_paths)))
    repeated_timestamps = list(get_repeated_timestamps(files_with_timestamps))
    if len(repeated_timestamps) > 0:
        raise Exception(f"Found files with identical timestamps={repeated_timestamps}")
    create_symlinks(files_with_timestamps, args.destination)

def create_filename(immich_asset):
    sanitized_timestamp = immich_asset['localDateTime'].replace(":", "").replace(".", "")
    return f"{sanitized_timestamp}{os.path.splitext(immich_asset['originalPath'])[1]}"

def get_repeated_timestamps(files_with_timestamps):
    files_with_timestamps = sorted(files_with_timestamps, key=lambda file_with_timestamp: file_with_timestamp['local_timestamp'])
    for key, group in groupby(files_with_timestamps, key=lambda file_with_timestamp: file_with_timestamp['local_timestamp']):
        group = list(group)
        if len(group) > 1:
            yield group

def parse_input(input):
    with open(input, 'r') as f:
        return json.load(f)

def replace_prefix(string, old_prefix, new_prefix):
    if string.startswith(old_prefix):
        return new_prefix + string[len(old_prefix):]
    else:
        raise Exception(f'Old prefix was not present in the file path: {string}')

def verify_all_paths_present(paths):
    for path in paths:
        if not check_file_existence_and_readability(path):
            raise Exception(f'File not accessible: {path}')

def check_file_existence_and_readability(filename):
    if not os.path.exists(filename):
        return False
    if not os.access(filename, os.R_OK):
        return False
    return True

def create_symlinks(files_with_timestamps, destination):
    for file_with_timestamp in files_with_timestamps:
        create_symlink(file_with_timestamp['path'], os.path.join(destination, file_with_timestamp['local_timestamp']))

# Source => File on disk
# Target => Name of the symlink that points to source
def create_symlink(source, target):
    if os.path.exists(target):
        if os.path.islink(target):
            if os.readlink(target) == os.path.abspath(source):
                print(f"Symlink {target} already exists and points to {source}, ignoring")
                return
            else:
                raise Exception(f"Symlink {target} exists but points to a different file: {os.readlink(target)}. Wanted to point to {source}.")
    return os.symlink(source, target)


if __name__ == '__main__':
    main()
