#!/usr/bin/env python
# -*- coding: utf-8 -*

__module_name__ = "Hexchat Alsa Notify"
__module_version__ = "0.3"
__module_description__ = "Custom alsa notifications"
__author__ = "MaurizioB"
__website__ = "https://github.com/MaurizioB/hexchat-alsa-notify"
__authorwebsite__ = "http://jidesk.net"

import hexchat
import alsaaudio, wave
import os.path

sound_filename = 'sine_alerts.wav'
addons_path = os.path.join(hexchat.get_info('configdir'), 'addons')
sound_file = os.path.join(addons_path, sound_filename)
card = 0

events = {'Channel Msg Hilight': True,
          'Channel Action Hilight': True,
          }

def help_message():
    message = ['\002\00304AlsaNotify\017\tUsage:',
            '/alsanotify <command> [option]:\n',
            '\002config\017               Show configuration',
            '\00310audio>\t\017',
            '\002list_cards\017           List available sound cards',
            '\002set_card id\017          Set card id',
            '\002test\017                 Test sound',
            '\002test_file <file>\017     Test "file" wave (must be a stereo wave file)',
            '\002set_file <file>\017      Set "file" wave',
            '\002load_file [test]\017     Show a file open dialog to choose a file; add "test" argument to just listen to the file, otherwise it will be set if successfully opened',
            '\002get_default\017          Download default sound file',
            '\00310events>\t\017',
            '\002list_events\017          List available events',
            '\002set_event event\017      Enable "event" notifications',
            '\002unset_event event\017    Disable "event" notifications',
            '\00310docs>\t\017',
            '\002about\017                Show informations about this script',
            '\002help\017                 Show this help',
            '\n\nOnly "standard" wave files are accepted, no floating point; other formats (FLAC, ogg, mp3...) are not supported yet.'
            ]
    return '\n'.join(message)

### preference wrapper
prefs_raw = 'alsa_notify'
if not hexchat.get_pluginpref(prefs_raw):
    hexchat.set_pluginpref(prefs_raw, str('{}'))

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

### config loading/setting
if not get_pluginpref('card'):
    set_pluginpref('card', card)

if not get_pluginpref('file'):
    set_pluginpref('file', sound_file)

if not get_pluginpref('events'):
    set_pluginpref('events', events)
### done


def aprint(*message):
    message = ' '.join(message)
    #print '\002\00304[AlsaNotify]\017 {}'.format(message)
    #hexchat.emit_print('Notice', 'AlsaNotify', message)
    print '\002\00304AlsaNotify\017\t', message

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


def settings(word, word_eol, user_data):
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
        elif word[1] == 'get_default':
            if os.path.isfile(os.path.join(addons_path, sound_filename)):
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
                with open(os.path.join(addons_path, sound_filename), 'wb') as wavefile:
                    wavefile.write(data)
            except:
                aprint('Error saving the default file! Check permissions or drive space!')
                return hexchat.EAT_ALL
            aprint('Default file "{}" successfully downloaded!'.format(sound_filename))

        elif word[1] == 'list_events':
            aprint('Available events ("*" marks an enabled event):')
            for event, active in get_pluginpref('events').iteritems():
                print '[{}] {}'.format('*' if active else ' ', event)
        elif word[1] == 'set_event':
            events = get_pluginpref('events')
            event = word_eol[2].strip('\'"').title()
            if not event in events.keys():
                aprint('Please input a valid event between these:\n{}'.format('\n'.join(events.keys())))
                return hexchat.EAT_ALL
            events[event] = True
            hexchat.hook_print(event, notify)
            set_pluginpref('events', events)
            aprint('Notifications set for "{}"'.format(event))
        elif word[1] == 'unset_event':
            events = get_pluginpref('events')
            event = word_eol[2].strip('\'"').title()
            if not event in events.keys():
                aprint('Please input a valid event between these:\n{}'.format('\n'.join(events.keys())))
                return hexchat.EAT_ALL
            events[event] = False
            hexchat.unhook(event)
            set_pluginpref('events', events)
            aprint('Notifications unset for "{}"'.format(event))
        elif word[1] == 'load_file':
            hexchat.hook_command('alsanotifyloadfile', loadfile)
            hexchat.command('getfile "alsanotifyloadfile{}" "Load .wav file" ./'.format(' testaudiofile' if (len(word) == 3 and word[2] == 'test') else ''))
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
    current = hexchat.find_context()
    origin = hexchat.get_context()
    if current == origin and hexchat.get_info('win_status') == 'active':
        return hexchat.EAT_NONE
    if not os.path.isfile(sound_file):
        aprint('Audio file not found, check configuration!')
        return hexchat.EAT_NONE
    playme()

#hexchat.hook_print("Channel Msg Hilight", notify)
#hexchat.hook_print('Channel Action Hilight', notify)

for event, active in get_pluginpref('events').iteritems():
    if active:
        hexchat.hook_print(event, notify)


hexchat.hook_command('alsanotify', settings, help=help_message())

aprint('{} (v. {}) successfully loaded with these settings:'.format(__module_name__, __module_version__))
print 'Sound card:', alsaaudio.cards()[get_pluginpref('card')]
if os.path.isfile(sound_file):
    print 'Audio file:', sound_file
else:
    print '\002\00304*\017\tAudio file "{}" not found, check configuration!'.format(get_pluginpref('file'))
    print 'Use "/alsanotify get_default" to download the default file or "/alsanotify set_file" to set a custom file'

