#!/usr/bin/env python
# ACL 2017 - alounsbu@alumni.uwo.ca

import os
import codecs
import platform
import sys

import mutagen


def directory_check(direc):
    """Determine if the system is running Linux or Windows, then pass file names to name_format for formatting."""

    if 'linux' in platform.system() or 'Linux' in platform.system():
        # If the user forgets to start a directory name with /, add it for them.
        if not direc.startswith('/'):
            direc = '/' + direc

        if not direc.endswith('/'):
            direc += '/'
    elif 'windows' in platform.system() or 'Windows' in platform.system():
        if '\\' in direc:
            direc = direc.replace('\\', '/')

        if not direc.endswith('/'):
            direc += '/'

    subdirs = None

    # Detect if other folders exist within the user-provided directory.
    for i in os.listdir(direc):
        if os.path.isdir(os.path.join(direc, i)):
            subdirs = True
            break
        else:
            subdirs = False

    #  Recurse through all folders in the main directory?
    if subdirs:
        print 'Recurse through all folders in the directory? (y/n)\n'
        choice = raw_input('> ')

        if choice.startswith('y'):
            # Get directory names
            for root, dirs, files in os.walk(direc, topdown=True):

                # root name obtained from os.walk is missing an ending forward slash.
                root += '/'

                name_format(files, root)
        else:
            files = os.listdir(direc)
            # Remove all folders and non-mp3 files from the 'files' list.
            for x in files[:]:
                # Linux files
                if x.startswith('.'):
                    files.remove(x)
                elif '.' not in x:
                    files.remove(x)
                elif 'mp3' not in x:
                    files.remove(x)

            name_format(files, direc)
    else:
        #  Get all of the file names in the specified directory.
        try:
            files_init = os.listdir(direc)
            name_format(files_init, direc)
        except OSError:
            print 'No such directory found'
            sys.exit()


def name_format(files, direc):
    """For each file in a directory, extract the <artist name> and <song title> contained in the ID3v2 tag, then
    format each for valid file renaming on the Linux/Windows file-system.
    """

    for mp3 in files:
        if '.mp3' not in mp3:
            continue
        else:
            mp3_file = direc + mp3
            # Begin trying to open an mp3 file.
            try:
                m = mutagen.File(mp3_file, easy=True)

                # Begin trying to obtain the artist and title information contained in the ID3v2 tag.
                try:
                    formatted_title = m['title']

                    # Formatting song title; remove square brackets and unicode indicator.
                    formatted_title = str(formatted_title).strip('[]')
                    formatted_title = formatted_title.strip('u\'')

                    # Remove any quotation marks found in the song title.
                    if '''"''' in formatted_title:
                        formatted_title = formatted_title.strip('''"''')

                    # Escape any unicode symbols found, leaving double/escaped slashes still to be removed.
                    formatted_title.decode('unicode_escape')
                    formatted_title = codecs.escape_decode(formatted_title)[0]

                    # Sequentially replace any non-alphanumeric characters with blanks.
                    for char in '\/:*?"<>|':
                        formatted_title = formatted_title.replace(char, '')

                    formatted_artist = m['artist']

                    # Formatting artist name.
                    formatted_artist = str(formatted_artist).strip('[]')
                    formatted_artist = formatted_artist.strip('u\'')

                    if '''"''' in formatted_artist:
                        formatted_artist = formatted_artist.strip('''"''')

                    formatted_artist.decode('unicode_escape')
                    formatted_artist = codecs.escape_decode(formatted_artist)[0]

                    for char in '\/:*?"<>|':
                        formatted_artist = formatted_artist.replace(char, '')

                    rename_file(direc, formatted_artist, formatted_title, mp3_file)

                # If no artist or song title information exists in the ID3v2 tag, continue onto the next file.
                except KeyError:
                    continue

            # In rare cases, some files use ID3v2 formatting that mutagen is incapable of handling properly.
            # If a KeyError does occur, just continue on to the next file.
            except KeyError:
                continue


def rename_file(direc, artist, title, file_name):
    """Cleanly rename each mp3 file according to <artist name> and <song title> only."""

    renaming = direc + artist + ' - ' + title + '.mp3'
    print file_name
    print renaming
    
    try:
        os.rename(file_name, renaming)
    except OSError:
        print 'Error with', file_name


if __name__ == '__main__':
    text = ''

    if len(sys.argv) == 1:
        print 'Please provide a valid directory.'
    else:
        for k in range(1, len(sys.argv)):
            if k < len(sys.argv):
                text += sys.argv[k] + ' '
            else:
                text += sys.argv[k]

        directory_check(text[:-1])
