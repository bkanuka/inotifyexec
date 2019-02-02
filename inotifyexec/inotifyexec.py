#!/usr/bin/env python3

"""Uses inotify to watch a directory and execute a command on file changes.

Usage:
    inotofyexec [-d DELAY | --delay DELAY] [-e EVENTS | --events EVENTS]
                [-f FILTER | --filter FILTER] [-r | --recursive] [-v | -vv]
                DIRECTORY [--] COMMAND [COMMAND_ARGS]...

Arguments:
    DIRECTORY       Directory to watch for changes
    COMMAND         Command to run on file changes
    COMMAND_ARGS    Arguments to pass through to command. Use "--" to separate DIR and COMMAND.

Options:
    -h --help                   show this help message and exit
    -v --verbose                print status messages. can be specified multiple times
    -d DELAY --delay=DELAY      time in seconds to wait for more changes before
                                executing command [default: 1.0]
    -e EVENTS --events=EVENTS   comma separated list of events to listen for.
                                [default: delete,create,close_write,modify,move]
    -f FILTER --filter=FILTER   only trigger for files matching this regex pattern [default: None]
    -r --recursive              watch directory recursively [default: False]

Events:
    access          file or directory contents were read
    modify          file or directory contents were written
    attrib          file or directory attributes changed
    close_write     file or directory closed, after being opened in
                    writable mode
    close_nowrite   file or directory closed, after being opened in
                    read-only mode
    close           file or directory closed, regardless of read/write mode
    open            file or directory opened
    moved_to        file or directory moved to watched directory
    moved_from      file or directory moved from watched directory
    move            file or directory moved to or from watched directory
    create          file or directory created within watched directory
    delete          file or directory deleted within watched directory
    delete_self     file or directory was deleted
"""

import multiprocessing
import os.path
import re
import subprocess
import sys
import threading
import time

from docopt import docopt

try:
    import pyinotify
except ImportError:
    print('Python pyinotify package is missing (often named python-pyinotify).')
    sys.exit(1)

FLAG_EVENTS = {
    'access': 0x00000001,  # File was accessed
    'modify': 0x00000002,  # File was modified
    'attrib': 0x00000004,  # Metadata changed
    'close_write': 0x00000008,  # Writable file was closed
    'close_nowrite': 0x00000010,  # Unwritable file closed
    'close': 0x00000008 | 0x00000010,
    'open': 0x00000020,  # File was opened
    'moved_from': 0x00000040,  # File was moved from X
    'moved_to': 0x00000080,  # File was moved to Y
    'move': 0x00000040 | 0x00000080,
    'create': 0x00000100,  # Subfile was created
    'delete': 0x00000200,  # Subfile was deleted
    'delete_self': 0x00000400,  # Self (watched item itself) was deleted
}


class Process(pyinotify.ProcessEvent):

    def __init__(self, immediate_callback, **kargs):
        super().__init__(**kargs)
        self.immediate_callback = immediate_callback

    def process_default(self, event):
        target = os.path.join(event.path, event.name)
        self.immediate_callback(target)


def watch_delay_call(
        base_directory,
        callback,
        delay=1.0,
        recursive=False,
        mask=pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE |
             pyinotify.IN_MODIFY | pyinotify.IN_MOVED_TO):
    """Watch all files below a directory and execute a command on changes.

  Add some delay so that multiple save operations trigger a single execution.

  Args:
    base_directory: Directory to monitor, recursively.
    callback: Function to call on file change, with a list of paths.
    delay: Time in seconds to delay.
    recursive: Monitor directory recursively.
    mask: File system changes to listen for.
  """

    def delay_call(pipe, delayed_callback, delay):
        path_list = []
        while True:
            # Wait until there is a change.
            path_list.append(pipe.recv())
            while pipe.poll():
                path_list.append(pipe.recv())

            # Delay
            time.sleep(delay)

            # If there are more changes, restart the timer.
            if pipe.poll():
                continue

            # Make unique
            path_list = set(path_list)

            # Execute the callback.
            delayed_callback(path_list)

            # Reset
            path_list = []

    receiver, sender = multiprocessing.Pipe(False)

    delay_callback_thread = threading.Thread(
        target=delay_call,
        args=(receiver, callback, delay))
    delay_callback_thread.daemon = True  # dies with this program.
    delay_callback_thread.start()

    while True:
        wm = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(wm, Process(sender.send))
        wm.add_watch(base_directory, mask, rec=recursive, auto_add=True)
        try:
            while True:
                notifier.process_events()
                if notifier.check_events():
                    notifier.read_events()
        except KeyboardInterrupt:
            notifier.stop()
            break


if __name__ == '__main__':
    from pprint import pprint

    arguments = docopt(__doc__)
    pprint(arguments)

    mask = 0
    if arguments["--events"]:
        events_list = arguments["--events"].split(',')
        for ev in events_list:
            evcode = FLAG_EVENTS.get(ev, 0)
            if evcode:
                mask |= evcode
            else:
                sys.exit("The event '%s' is not valid" % ev)
    else:
        sys.exit("No events specified")

    command = [arguments['COMMAND']] + arguments['COMMAND_ARGS']

    def callback(paths):
        if paths:
            if arguments["--filter"] and arguments["--filter"] != 'None':
                paths = [path for path in paths if re.search(arguments["--filter"], path)]
                if not paths:
                    return

            print('')
            for path in paths:
                print('Files changes:')
                print('    {0}'.format(path))
        print('Running command:')
        print('    {0}'.format(' '.join(command)))
        subprocess.call(command)

    print('Monitoring file changes in directory: {0}'.format(arguments['DIRECTORY']))

    watch_delay_call(base_directory=arguments['DIRECTORY'],
                     callback=callback,
                     delay=float(arguments['--delay']),
                     recursive=arguments['--recursive'],
                     mask=mask)
