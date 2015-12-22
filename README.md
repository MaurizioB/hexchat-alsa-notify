# hexchat-alsa-notify
A hexchat addon to play notifications directly from alsa


Hexchat uses its internal engine to play sound notifications (or libcanberra),
while this is usually ok for most users, some of us have more than one sound
card, or a specific hardware/software setup that could create some issues, such
as a complex .asound configuration or using multiple sound servers like jack
with pulseaudio.
With this script you can use a specific alsa hardware card or, eventually, a
plug:device if set in the .asoundrc file.

## Usage
Download alsa_notify.py and put it in the `$(XDG_CONFIG_HOME)/hexchat/addons/`
(usually it is `~/.config/hexchat/addons/`) or load it from Hexchat through
Window/Plugins and Scripts window.
Once the plugin is loaded it selects the first hardware device and tries to
use a default file (`sine_alert.wav`), you can download it using:

    /alsanotify get_default

Then type `/alsanotify help` in any window to learn how to configure it.

## Issues
Right now I don't know how to really open _any_ audio file yet, so it's better
to use a standard stereo Wave file at 44.1/48khz.

Using **sox**

    $ sox input.wav -r 48000 -c 2 output.wav

Using **ffmpeg**

    $ ffmpeg -i input.wav -ar 48000 -ac 2 output.wav
