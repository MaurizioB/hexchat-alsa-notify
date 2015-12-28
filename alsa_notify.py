#!/usr/bin/env python
# -*- coding: utf-8 -*

__module_name__ = "Alsa Notifications"
__module_version__ = "0.5"
__module_description__ = "Advanced Alsa notifications"
__author__ = "MaurizioB"
__website__ = "https://github.com/MaurizioB/hexchat-alsa-notify"
__authorwebsite__ = "http://jidesk.net"

import hexchat
import alsaaudio, wave
import os.path
from os import makedirs
#from collections import OrderedDict

sound_filename = default_sound = 'sine_alerts.wav'

addons_path = os.path.join(hexchat.get_info('configdir'), 'addons')
card = 0
prefs_raw = 'alsa_notify'

events = {'Channel Msg Hilight': True,
          'Channel Action Hilight': True,
          'Private Action': True,
          'Private Action to Dialog': True,
          'Private Message': True,
          'Private Message to Dialog': True
}

commands = [('config', 'Show configuration'),
            ('audio', None),
            ('list_cards', 'List available sound cards'),
            ('set_card id', 'Set card id'),
            ('test', 'Test sound'),
            ('test_file <file>', 'Test "file" wave (must be a stereo wave file)'),
            ('set_file <file>', 'Set "file" wave'),
            ('load_file [test]', ('Show a file open dialog to choose a file; add '
                                 '"test" argument to just listen to the file '
                                 'otherwise it will be set if successfully opened')),
            ('download_sound', 'Download default sound file'),
            ('events', None),
            ('list_events', 'List available events'),
            ('set_event event', 'Enable "event" notifications'),
            ('unset_event event', 'Disable "event" notifications'),
            ('docs', None),
            ('about', 'Show informations about this script'),
            ('help', 'Show this help'),
            ]


def help_message():
    message = ['\002\00304AlsaNotify\017\tUsage:',
            '/alsanotify <command> [option]:\n',]
    maxlen = len(max([i[0] for i in commands], key=len))+4
    for i in commands:
        if not i[1]:
            message.append('\00310{}>\t\017'.format(i[0]))
        else:
            message.append('\002{}\017{}{}'.format(i[0], ' '*(maxlen-len(i[0])), i[1]))

    message.append('\n\nOnly "standard" wave files are accepted, no floating point; other formats (FLAC, ogg, mp3...) are not supported yet.')
    return '\n'.join(message)

### preference wrapper
def get_pluginpref(name):
    prefs = eval(hexchat.get_pluginpref(prefs_raw))
    return prefs.get(name, None)

def set_pluginpref(name, value):
    prefs = eval(hexchat.get_pluginpref(prefs_raw))
    prefs[name] = value
    hexchat.set_pluginpref(prefs_raw, str(prefs))

def del_pluginpref(name):
    prefs = eval(hexchat.get_pluginpref(prefs_raw))
    try:
        prefs.pop(name)
    except:
        pass
    hexchat.set_pluginpref(prefs_raw, str(prefs))

def list_pluginpref():
    print hexchat.get_pluginpref(prefs_raw)
### done

def aprint(*message):
    message = ' '.join(message)
    #print '\002\00304[AlsaNotify]\017 {}'.format(message)
    #hexchat.emit_print('Notice', 'AlsaNotify', message)
    print '\002\00304AlsaNotify\017\t', message

### config loading/setting
if not hexchat.get_pluginpref(prefs_raw):
    firstrun = True
    hexchat.set_pluginpref(prefs_raw, str('{}'))
else:
    firstrun = False
    version = get_pluginpref('version')
    if not version or version < __module_version__:
        set_pluginpref('version', __module_version__)

        aprint('updating preferences')
        if not get_pluginpref('events'):
            set_pluginpref('events', events)
        else:
            imported = get_pluginpref('events')
            print imported
            for event, active in events.items():
                events[event] = imported.get(event, active)
            set_pluginpref('events', events)
            print events

        print '...done!'
    elif version < __module_version__:
        pass

if not get_pluginpref('card'):
    set_pluginpref('card', card)

if not get_pluginpref('events'):
    set_pluginpref('events', events)

if get_pluginpref('enabled') == None:
    set_pluginpref('enabled', True)

if get_pluginpref('sounds_path') == None:
    if os.path.isdir(os.path.join(addons_path, 'alsa_notify')):
        sounds_path = os.path.join(addons_path, 'alsa_notify')
    else:
        sounds_path = os.path.join(hexchat.get_info('configdir'), 'sounds')
        if not os.path.isdir(sounds_path):
            try:
                makedirs(sounds_path)
            except OSError:
                aprint('Error creating sounds directory "{}", check write permissions'.format(sounds_path))

else:
    sounds_path = get_pluginpref('sounds_path')

if not get_pluginpref('file'):
    set_pluginpref('file', sound_file)
else:
    sound_file = get_pluginpref('file')

### done


def playme(sound_file=None, *args):
    card = get_pluginpref('card')
    if not sound_file:
        sound_file = get_pluginpref('file')
    try:
        out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, card='hw:{},0'.format(card))
    except:
        aprint('Error opening soundcard')
        return hexchat.EAT_NONE
    try:
        f = wave.open(sound_file, 'rb')
    except wave.Error:
        aprint('Error, maybe the file "{}" is not a wave file?'.format(sound_file))
        return
    except EOFError:
        aprint('Error, file "{}" is empty'.format(sound_file))
        return
    except IOError:
        aprint('Error accessing file "{}", check file permissions'.format(sound_file))
        return
    out.setchannels(f.getnchannels())
    out.setrate(f.getframerate())
    out.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    out.setperiodsize(160)
    data = f.readframes(320)
    while len(data) > 0:
        out.write(data)
        data = f.readframes(320)
    out.close()
    return hexchat.EAT_NONE

def printcards():
    for i, card in enumerate(alsaaudio.cards()):
        if i == get_pluginpref('card'):
            print '\002\00304{}\017: {}'.format(i, card)
        else:
            print '{}: {}'.format(i, card)


def manager(word, word_eol, user_data):
    card = get_pluginpref('card')
    sound_file = get_pluginpref('file')
    if len(word) < 2:
        aprint('use a command!')
    else:
        if word[1] == 'config':
            aprint('Configuration:')
            print 'Sound card:', alsaaudio.cards()[get_pluginpref('card')]
            if os.path.isfile(sound_file):
                print 'Audio file:', sound_file
            else:
                print 'Audio file "{}" not found, check configuration!'.format(sound_file)
        elif word[1] == 'list_cards':
            aprint('Available sound cards:')
            printcards()
        elif word[1] == 'set_card':
            if not len(word) >= 3 or not word[2].isdigit() or int(word[2])>=len(alsaaudio.cards()):
                aprint('Please use a valid card number from this list:')
                printcards()
            else:
                card = int(word[2])
                aprint('Setting soundcard "{}"'.format(alsaaudio.cards()[card]))
                set_pluginpref('card', card)
        elif word[1] == 'test_file' or word[1] == 'set_file':
            if not len(word) >= 3:
                aprint('Please enter a file path')
            else:
                newfile = os.path.join(addons_path, os.path.expanduser(word_eol[2].strip('\'"')))
                if os.path.isfile(os.path.join(addons_path, newfile)):
                    statinfo = os.stat('/home/mauriziob/session05.wav')
                    if int(statinfo.st_size)/1024/1024.0 > 4:
                        aprint('File size too big, try with something smaller')
                        return hexchat.EAT_ALL
                    if int(statinfo.st_size) == 0:
                        aprint('File looks empty, try another file')
                        return hexchat.EAT_ALL
                    aprint('Testing file: "{}"'.format(newfile))
                    try:
                        playme(newfile)
                        if word[1] == 'set_file':
                            set_pluginpref('file', newfile)
                            print 'File {} set for notifications'.format(newfile)
                    except:
                        print 'error playing "{}"'.format(newfile)
                else:
                    aprint('Please enter a valid file path')
        elif word[1] == 'test':
            aprint('Playing test file: "{}"'.format(sound_file))
            playme()
        elif word[1] == 'download_sound':
            if os.path.isfile(os.path.join(sounds_path, sound_filename)):
                aprint('Default "{}" already exists'.format(sound_filename))
            aprint('Trying to download the default file')
            import urllib2, socket
            try:
                dl = urllib2.urlopen('https://raw.github.com/MaurizioB/hexchat-alsa-notify/master/'+sound_filename, timeout=10)
            except urllib2.URLError, e:
                aprint('Error downloading the default file:', e.reason)
                return hexchat.EAT_ALL
            except socket.timeout:
                aprint('Timeout downloading the default file!')
                return hexchat.EAT_ALL
            data = dl.read()
            try:
                with open(os.path.join(sounds_path, sound_filename), 'wb') as wavefile:
                    wavefile.write(data)
            except:
                aprint('Error saving the default file! Check permissions or drive space!')
                return hexchat.EAT_ALL
            aprint('Default file "{}" successfully downloaded!'.format(sound_filename))
            hexchat.command('MENU DEL "Settings/Notifications/Settings/Download sounds"')

        elif word[1] == 'enable':
            set_pluginpref('enabled', True)
            aprint('Notifications enabled')
            menu_events(True)
        elif word[1] == 'disable':
            set_pluginpref('enabled', False)
            aprint('Notifications disabled')
            menu_events(False)
        elif word[1] == 'list_events':
            aprint('Available events ("*" marks an enabled event):')
            for event, active in get_pluginpref('events').iteritems():
                print '[{}] {}'.format('*' if active else ' ', event)
        elif word[1] == 'set_event':
            events = get_pluginpref('events')
            event = word_eol[2].strip('\'"').lower()
            if not event in [e.lower() for e in events.keys()]:
                aprint('Please input a valid event between these:\n{}'.format('\n'.join(events.keys())))
                return hexchat.EAT_ALL
            events[event] = True
            hexchat.hook_print(event, notify)
            set_pluginpref('events', events)
            aprint('Notifications set for "{}"'.format(event))
        elif word[1] == 'unset_event':
            events = get_pluginpref('events')
            event = word_eol[2].strip('\'"').lower()
            if not event in [e.lower() for e in events.keys()]:
                aprint('Please input a valid event between these:\n{}'.format('\n'.join(events.keys())))
                return hexchat.EAT_ALL
            events[event] = False
            hexchat.unhook(event)
            set_pluginpref('events', events)
            aprint('Notifications unset for "{}"'.format(event))
        elif word[1] == 'load_file':
            hexchat.hook_command('alsanotifyloadfile', loadfile)
            hexchat.command('getfile "alsanotifyloadfile{}" "Load .wav file" {}'.format(' testaudiofile' if (len(word) == 3 and word[2] == 'test') else '', sounds_path))
            return hexchat.EAT_ALL

        elif word[1] == 'help':
            print help_message()
        elif word[1] == 'about':
            aprint('{}, version {}'.format(__module_name__, __module_version__))
            print 'Python addon written by <\002\00304{}\017> (\00310{}\017)'.format(__author__, __authorwebsite__)
            print 'Official addon website:', __website__
        #only for testing
        elif word[1] == 'del_conf':
            aprint('Deleting configuration')
            hexchat.del_pluginpref(prefs_raw)
            aprint('Done: {}'.format(hexchat.list_pluginpref()))
            #del_pluginpref('card')
            #del_pluginpref('file')
        else:
            aprint('Command not valid')
    return hexchat.EAT_ALL

def loadfile(word, word_eol, user_data):
    #print word_eol
    if len(word_eol) == 1 or word[-1] == 'testaudiofile':
        hexchat.unhook('alsanotifyloadfile')
        return hexchat.EAT_ALL
    sound_file = word[-1]
    if word[1] == 'testaudiofile':
        hexchat.command('alsanotify test_file '+sound_file)
    else:
        hexchat.command('alsanotify set_file '+sound_file)
    return hexchat.EAT_ALL

def notify(word, word_eol, user_data):
    if not get_pluginpref('enabled'):
        return hexchat.EAT_NONE
    current = hexchat.find_context()
    origin = hexchat.get_context()
    if current == origin and hexchat.get_info('win_status') == 'active':
        return hexchat.EAT_NONE
    if not os.path.isfile(sound_file):
        aprint('Audio file not found, check configuration!')
        return hexchat.EAT_NONE
    playme()

def make_menu():
    path = 'Settings/Notifications'
    hexchat.command('MENU -i ADD '+path)
    hexchat.command('MENU -t{} ADD "{}/Enable notifications" "alsanotify enable" "alsanotify disable"'.format('1' if get_pluginpref('enabled') else '0', path ))
    hexchat.command('MENU ADD '+path+'/-')

    hexchat.command('MENU ADD "'+path+'/Settings"')
    confpath = path+'/Settings'

    #add audio cards
    hexchat.command('MENU ADD "'+confpath+'/Sound card"')
    active = alsaaudio.cards()[int(get_pluginpref('card'))]
    for i, card in enumerate(alsaaudio.cards()):
        hexchat.command('MENU -r{a},{g} ADD "{p}/Sound card/{c}" "alsanotify set_card {i}"'.format(a='1' if active==card else '0', g=alsaaudio.cards()[0], p=confpath, c=card, i=i))
    hexchat.command('MENU ADD '+confpath+'/-')

    #load custom file
    hexchat.command('MENU ADD "'+confpath+'/Load file..." "alsanotify load_file"')
    
    #download default file
    if not os.path.isfile(os.path.join(sounds_path, default_sound)):
        hexchat.command('MENU ADD "'+confpath+'/Download sounds" "alsanotify download_sound"')

    hexchat.command('MENU ADD '+path+'/-')
    #add event list
    if get_pluginpref('enabled'):
        s = '1'
    else: s = '0'
    for event, active in get_pluginpref('events').items():
        hexchat.command('MENU -e{s} -t{a} ADD "{p}/{e}" "alsanotify set_event {e}" "alsanotify unset_event {e}"'.format(s=s, a='1' if active else '0', p=path, e=event))

def menu_events(active):
    path = 'Settings/Notifications'
    if active:
        s = '1'
    else: s = '0'
    for event, active in get_pluginpref('events').items():
        hexchat.command('MENU -e{s} -t{a} ADD "{p}/{e}" "alsanotify set_event {e}" "alsanotify unset_event {e}"'.format(s=s, a='1' if active else '0', p=path, e=event))

def unload(userdata):
    aprint('unloading {} addon'.format(__module_name__))
    hexchat.command('MENU DEL Settings/Notifications')


#functions defined, let's go!
for event, active in get_pluginpref('events').items():
    if active:
        hexchat.hook_print(event, notify)

make_menu()
hexchat.hook_command('alsanotify', manager, help=help_message())
hexchat.hook_unload(unload)

if firstrun:
    aprint('{} (v. {}) successfully loaded!'.format(__module_name__, __module_version__))
    print 'This is the first time it is installed, you may want to configure it. These are the default settings:'
else:
    aprint('{} (v. {}) successfully loaded with these settings:'.format(__module_name__, __module_version__))
print 'Sound card:', alsaaudio.cards()[get_pluginpref('card')]
if os.path.isfile(sound_file):
    print 'Audio file:', sound_file
else:
    print '\002\00304*\017\tAudio file "{}" not found, check configuration!'.format(get_pluginpref('file'))
    print 'Use "/alsanotify download_sound" to download the default file or "/alsanotify set_file" to set a custom file'
if get_pluginpref('enabled'):
    enabled = []
    disabled = []
    for event, active in get_pluginpref('events').items():
        if active:
            enabled.append(event)
        else:
            disabled.append(event)
    if len(enabled) > 0:
        print 'Notifications are enabled for the following events:'
        print '*\t'+', '.join(enabled)
    if len(disabled) > 0:
        print 'Notifications are disabled for the following events:'
        print '*\t'+', '.join(disabled)

else:
    print 'Notifications are disabled'

