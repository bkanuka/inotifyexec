# inotifyexec 
Uses `inotify` to watch a directory and execute a command on file changes.
Based off of a [gist](https://gist.github.com/wernight/11401031) by Werner Beroux <werner@beroux.com>.

## Usage
See `inotifyexec --help`

## Why?
Just using inotify-tools `while inotifywait -r -e close_write .; do something; done`
has many issues which are fixed by this tools:
 * If your editor creates a backup before writing the file, it'll trigger multiple times.
 * If your directory structure is deep, it'll have to reinitialize inotify after each change.
 * If your command takes time to execute and isn't in background, you may miss all file changes
   done during that command's execution; and if you run your command in background you may should
   make sure you can run it simultaneously multiple times.
 * File filtering becomes a small script (see also https://superuser.com/questions/181517/).