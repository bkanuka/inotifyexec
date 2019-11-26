# inotifyexec 
Uses `inotify` to watch a directory and execute a command on file changes.
Based off of a [gist](https://gist.github.com/wernight/11401031) by Werner Beroux <werner@beroux.com>.

## Usage
```
Uses inotify to watch a directory and execute a command on file changes.

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
```

## Why?
Just using inotify-tools `while inotifywait -r -e close_write .; do something; done`
has many issues which are fixed by this tools:
 * If your editor creates a backup before writing the file, it'll trigger multiple times.
 * If your directory structure is deep, it'll have to reinitialize inotify after each change.
 * If your command takes time to execute and isn't in background, you may miss all file changes
   done during that command's execution; and if you run your command in background you may should
   make sure you can run it simultaneously multiple times.
 * File filtering becomes a small script (see also https://superuser.com/questions/181517/).
