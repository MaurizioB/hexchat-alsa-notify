# hexchat-alsa-notify
A HexChat addon for Linux to play notifications directly from
[Alsa](http://alsa-project.org)


HexChat uses its internal engine to play sound notifications (or libcanberra),
while this is usually ok for most users, some of us have more than one sound
card, or a specific hardware/software setup that could create some issues, such
as a complex .asound configuration or using multiple sound servers like jack
with pulseaudio.
With this script you can use a specific alsa hardware card or, eventually, a
plug:device if set in the .asoundrc file.

## Requirements
- A Linux system with working ALSA sound
- Python scripting interface plugin for HexChat
- [pyalsaaudio](http://larsimmisch.github.io/pyalsaaudio/).

## Install
Download `alsa_notify.py` and put it in the HexChat addon directory (usually it
is `~/.config/hexchat/addons/`) or load it from HexChat through Window/Plugins
and Scripts window.
Once the plugin is loaded it selects the first available hardware device and
tries to use a default file (`sine_alert.wav`).

## Usage
There is a custom menu added in the `Settings` menu of HexChat, you can control
basic behavior of the plugins from here. Apart from that, there's a full command
interface available:

    /alsanotify <command> [option]
`command`                 | action
--------------------------|-------
`config`                  |Show configuration
`list_cards`              |List available sound cards
`set_card id`             |Set card id
`test`                    |Test sound
`test_file *file*`        |Test "file" wave (must be a stereo wave file)*
`set_file *file*`         |Set "file" wave*
`load_file [test]`        |Show a file open dialog to select a file;<br/>add "test" argument to just listen to the file,<br/>otherwise it will be set if successfully opened
`download_sound`          |Download default sound file
`list_events`             |List available events
`set_event event`         |Enable "event" notifications**
`unset_event event`       |Disable "event" notifications**
`about`                   |Show informations about this script
`help`                    |Show this help

(*) `file` name can be an absolute or relative path ('`~`' is accepted).

(**) `event` is case insensitive.


The script automatically enables the 2 default events (more events might be
added in the future) once installed, which are "Channel highlights" when an
user types your nick.

If you just download the script without the default file, you can make the
script to download it for you using the `get_default` command


## Issues
Right now I don't know how to really open _any_ audio file yet, so it's better
to use a standard stereo Wave file at 44.1/48khz.

Using **sox**:

    $ sox input.wav -r 48000 -c 2 output.wav

Using **ffmpeg**:

    $ ffmpeg -i input.wav -ar 48000 -ac 2 output.wav
