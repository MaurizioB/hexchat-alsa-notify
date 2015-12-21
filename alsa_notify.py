#!/usr/bin/env python
# -*- coding: utf-8 -*

__module_name__ = "Hexchat Alsa Notify"
__module_version__ = "0.1"
__module_description__ = "Alsa notifications"
__author__ = "MaurizioB"

import hexchat
import alsaaudio, wave
import os.path

sound_file = '/home/mauriziob/sounds/sine_alerts.wav'
card = 0

def help_message():
    message = ['\002\00304AlsaNotify\017\tUsage:',
            '/alsanotify <command> [option]:',
            'config           Show configuration',
            'listcards        List available sound cards',
            'setcard id       Set card id',
            'test             Test sound',
            'testfile file    Test "file" wave (must be a stereo wave file)',
            'setfile file     Set "file" wave',
            'help             Shows this help'
            ]
    return '\n'.join(message)

if not hexchat.get_pluginpref('card'):
    hexchat.set_pluginpref('card', card)

if not hexchat.get_pluginpref('file'):
    hexchat.set_pluginpref('file', sound_file)

def aprint(*message):
    message = ' '.join(message)
    #print '\002\00304[AlsaNotify]\017 {}'.format(message)
    #hexchat.emit_print('Notice', 'AlsaNotify', message)
    print '\002\00304AlsaNotify\017\t', message

def playme(sound_file=None, *args):
    card = hexchat.get_pluginpref('card')
    if not sound_file:
        sound_file = hexchat.get_pluginpref('file')
    try:
        out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, card='hw:{},0'.format(card))
    except:
        aprint('Error opening soundcard')
        return hexchat.EAT_NONE
    f = wave.open(sound_file, 'rb')
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
        if i == hexchat.get_pluginpref('card'):
            print '\002\00304{}\017: {}'.format(i, card)
        else:
            print '{}: {}'.format(i, card)


def settings(word, word_eol, userdata):
    card = hexchat.get_pluginpref('card')
    sound_file = hexchat.get_pluginpref('file')
    if len(word) < 2:
        aprint('use a command!')
    else:
        if word[1] == 'config':
            aprint('Configuration:')
            print 'Sound card:', alsaaudio.cards()[hexchat.get_pluginpref('card')]
            print 'Audio file:', hexchat.get_pluginpref('file')
        elif word[1] == 'listcards':
            aprint('Available sound cards:')
            printcards()
        elif word[1] == 'setcard':
            if not len(word) >= 3 or not word[2].isdigit() or int(word[2])>=len(alsaaudio.cards()):
                aprint('Please use a valid card number from this list:')
                printcards()
            else:
                card = int(word[2])
                aprint('Setting soundcard "{}"'.format(alsaaudio.cards()[card]))
                hexchat.set_pluginpref('card', card)
        elif word[1] == 'testfile' or word[1] == 'setfile':
            if not len(word) >= 3:
                aprint('Please enter a file path')
            else:
                newfile = word_eol[2].strip('\'"')
                if os.path.isfile(newfile):
                    aprint('Testing file: "{}"'.format(newfile))
                    try:
                        playme(newfile)
                        if word[1] == 'setfile':
                            hexchat.set_pluginpref('file', newfile)
                            print 'File {} set for notifications'.format(newfile)
                    except:
                        print 'error playing "{}"'.format(newfile)
                else:
                    aprint('Please enter a valid file path')
        elif word[1] == 'test':
            aprint('Playing test file: "{}"'.format(sound_file))
            playme()
        elif word[1] == 'help':
            print help_message()
        else:
            aprint('Command not valid')
    return hexchat.EAT_ALL

def notify(*args):
    playme()

hexchat.hook_print("Channel Msg Hilight", notify)
hexchat.hook_print('Channel Action Hilight', notify)
hexchat.hook_command('alsanotify', settings, help=help_message())

aprint(__module_name__, 'successfully loaded with:')
print 'Sound card:', alsaaudio.cards()[hexchat.get_pluginpref('card')]
print 'Audio file:', hexchat.get_pluginpref('file')

