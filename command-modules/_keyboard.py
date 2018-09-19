#
# This file is a command-module for Dragonfly.
# (c) Copyright 2018 by AseLinux
# Modified original dragonfly's _multiedit.py https://github.com/t4ngo/dragonfly-modules/blob/master/command-modules/_multiedit.py
#
# (c) Copyright 2008 by Christo Butcher
# Licensed under the LGPL, see <http://www.gnu.org/licenses/>
#

"""
Command-module for cursor movement and **editing**
============================================================================

This module allows the user to control the cursor and 
efficiently perform multiple text editing actions within a 
single phrase.


Example commands
----------------------------------------------------------------------------

*Note the "/" characters in the examples below are simply 
to help the reader see the different parts of each voice 
command.  They are not present in the actual command and 
should not be spoken.*

Example: **"up 4 / down 1 page / home / space 2"**
   This command will move the cursor up 4 lines, down 1 page,
   move to the beginning of the line, and then insert 2 spaces.

Example: **"left 7 words / backspace 3 / insert hello Cap world"**
   This command will move the cursor left 7 words, then delete
   the 3 characters before the cursor, and finally insert
   the text "hello World".

Example: **"home / space 4 / down / 43 times"**
   This command will insert 4 spaces at the beginning of 
   of this and the next 42 lines.  The final "43 times" 
   repeats everything in front of it that many times.


Discussion of this module
----------------------------------------------------------------------------

This command-module creates a powerful voice command for 
editing and cursor movement.  This command's structure can 
be represented by the following simplified language model:

 - *CommandRule* -- top-level rule which the user can say
    - *repetition* -- sequence of actions (name = "sequence")
       - *KeystrokeRule* -- rule that maps a single 
         spoken-form to an action
    - *optional* -- optional specification of repeat count
       - *integer* -- repeat count (name = "n")
       - *literal* -- "times"

The top-level command rule has a callback method which is 
called when this voice command is recognized.  The logic 
within this callback is very simple:

1. Retrieve the sequence of actions from the element with 
   the name "sequence".
2. Retrieve the repeat count from the element with the name
   "n".
3. Execute the actions the specified number of times.

"""

try:
    import pkg_resources
    pkg_resources.require("dragonfly >= 0.6.5beta1.dev-r99")
except ImportError:
    pass

from dragonfly import *

from natlink import setMicState
import lib.sound as sound
from _dragonfly_tools import show_natlink_messages_window


import win32con
from dragonfly.actions.keyboard import Typeable, keyboard
from dragonfly.actions.typeables import typeables
if not 'Control_R' in typeables:
    keycode = win32con.VK_RCONTROL
    typeables["Control_R"] = Typeable(code=keycode, name="Control_R")
if not 'semicolon' in typeables:
    typeables["semicolon"] = keyboard.get_typeable(char=';')

#---------------------------------------------------------------------------
# Here we globally defined the release action which releases all
#  modifier-keys used within this grammar.  It is defined here
#  because this functionality is used in many different places.
#  Note that it is harmless to release ("...:up") a key multiple
#  times or when that key is not held down at all.

release = Key("shift:up, ctrl:up, alt:up, win:up") #shift ctrl alt win are dragonfly's internally defined names for those keyboard keys

#---------------------------------------------------------------------------
def cancel_and_sleep(text=None, text2=None):
    """Used to cancel an ongoing dictation and puts microphone to sleep.

    This method notifies the user that the dictation was in fact canceled,
    with a sound and a message in the Natlink feedback window.
    Then the the microphone is put to sleep.
    Example:
    "'random mumbling go to sleep'" => Microphone sleep.

    """
    
    setMicState("sleeping")
    sound.play(sound.SND_DING)
    show_natlink_messages_window(duration=2, msg="* Dictation canceled. Going to sleep. *")

    
    

def test_keyboard():
    """
    just print a message to natlink messages window
    """

    show_natlink_messages_window(duration=3, msg="** testing _keyboard.py **")
    

#---------------------------------------------------------------------------
# Set up this module's configuration.

config            = Config("keyboard")
config.cmd        = Section("Language section")
# this is the default config command map that came with _multi-edit.py, which I will be fixing and categorising and adding to.
config.cmd.map    = Item(
    # Here we define the *default* command map.  If you would like to
    #  modify it to your personal taste, please *do not* make changes
    #  here.  Instead change the *config file* called "_multiedit.txt".
{
     # Spoken-form    ->    ->    ->     Action object
     
    # all should be replaced by the controlKeyMap, just need to add <n> to spec/spoken form and it's action mapping in config.cmd.map down below
     # "up [<n>]":                         Key("up:%(n)d"),
     # "down [<n>]":                       Key("down:%(n)d"),
     # "left [<n>]":                       Key("left:%(n)d"),
     # "right [<n>]":                      Key("right:%(n)d"),
     # "page up [<n>]":                    Key("pgup:%(n)d"),
     # "page down [<n>]":                  Key("pgdown:%(n)d"),
     # "up <n> (page | pages)":            Key("pgup:%(n)d"),
     # "down <n> (page | pages)":          Key("pgdown:%(n)d"),
     # "left <n> (word | words)":          Key("c-left:%(n)d"),
     # "right <n> (word | words)":         Key("c-right:%(n)d"),
     # "home":                             Key("home"),
     # "end":                              Key("end"),
     # "space [<n>]":                      release + Key("space:%(n)d"),
     # "enter [<n>]":                      release + Key("enter:%(n)d"),
     # "tab [<n>]":                        Key("tab:%(n)d"),
     # "delete [<n>]":                     release + Key("del:%(n)d"),
     # "backspace [<n>]":                  release + Key("backspace:%(n)d"),
     # "pop up":                           release + Key("apps"),
     
    # all these have moved into controlKeyMap
    # no quite sure of their benefit
     # "[(hold|press)] alt": Key("alt:down/3"),
     # "release alt": Key("alt:up"),
     # "[(hold|press)] shift": Key("shift:down/3"),
     # "release shift": Key("shift:up"),
     # "[(hold|press)] control": Key("ctrl:down/3"),
     # "release control": Key("ctrl:up"),
     "release [all]": release,
    
    # normal dictation while in command mode, and amongst all the other commands so ccr continuous command recognition applies
     "(say|dictate) <text>":               release + Text("%(text)s"),
     "mimic <text>":             release + Mimic(extra="text"),
     
     # some dragon control stuff, i think i like to use at the moment
     # replaces dragon's "go to sleep" and adds "snore" and extra functionality of cancelling the immediate utterances
     "[<text>] (snore|go to sleep|cancel and sleep) [<text2>]": Function(cancel_and_sleep),  # @IgnorePep8
     "test keyboard":                                           Function(test_keyboard),
     
    # text editing
     # the usual suspects
     "paste":                            release + Key("c-v"),
     "duplicate <n>":                    release + Key("c-c, c-v:%(n)d"),
     "copy":                             release + Key("c-c"),
     "cut":                              release + Key("c-x"),
     "select all":                       release + Key("c-a"),
     "delete [<n> | this] (line|lines)": release + Key("home, s-down:%(n)d, del"),
     # nice ones, Short-talk word jumps and deletes
     "fomble [<n>]":    Key("c-right/5:%(n)d"),
     "(sky|shift) fomble [<n>]":    Key("shift:down/3") + Key("c-right/5:%(n)d"),
     "kimble [<n>]":    Key("c-del/5:%(n)d"),
     "bamble [<n>]":    Key("c-left/5:%(n)d"),
     "(sky|shift) bamble [<n>]":    Key("shift:down/3") + Key("c-left/5:%(n)d"),
     "dumbbell [<n>]":  Key("c-backspace/5:%(n)d"),
     # jump top or bottom of page, works in browsers, editors, email, etc, like dragons default commands scroll up and scroll down
     "(doc home|north)": Key("c-home"),
     "(doc end|south)":  Key("c-end"),
     "(shift|sky) north": Key("shift:down/3") + Key("c-home"),
     "(shift|sky) south":  Key("shift:down/3") + Key("c-end"),
     # Closures.
     "angle brackets": Key("langle, rangle, left/3"),
     "brackets": Key("lbracket, rbracket, left/3"),
     "braces": Key("lbrace, rbrace, left/3"),
     "parens": Key("lparen, rparen, left/3"),
     "quotes": Key("dquote/3, dquote/3, left/3"),
     "(single-quotes|singles)": Key("squote, squote, left/3"),
     # undo, redo
     "undo": release + Key("c-z/3"),
     "undo <n> [times]": release + Key("c-z/3:%(n)d"),
     "redo": release + Key("c-y/3"),
     "redo <n> [times]": release + Key("c-y/3:%(n)d"),

     
    # tab control, in browser, notepad, file explorer, gnome-shell, etc
    "(pret|preet) [<n>]": Key("c-pgup/5:%(n)d"),
    "(net|neat) [<n>]":  Key("c-pgdown/5:%(n)d"),
    # moving tabs  
    "(shift|sky) (pret|preet) [<n>]": Key("shift:down/3") + Key("c-pgup/5:%(n)d"),
    "(shift|sky) (net|neat) [<n>]":  Key("shift:down/3") + Key("c-pgdown/5:%(n)d"),
    "clote [<n>]":      Key("c-w/2:%(n)d"),
    "backward [<n>]":   Key("a-left/2:%(n)d"),
    "forward [<n>]":    Key("a-right/2:%(n)d"),
    "upward [<n>]":    Key("a-up/2:%(n)d"),
    # zoom
    "zoom [in] [<n>]":    Key("c-plus:%(n)d"),
    "zoom out [<n>]":    Key("c-minus:%(n)d"),

    # Windows control
    "win flip": Key("alt:down, tab:down/5, alt:up"),	# the 5 is outerpause and is about the minimum for this to work
    "win toggle": Key("win:down, tab/25:3, win:up"),
    "win show": Key("ctrl:down, win:down, tab:down") + Key("control:up, win:up, tab:up"),

    # sound control, these work on Windows 7 but not on windows 10, will find out later how to fix this
    "volume up [<n>]": Key("volumeup:%(n)d"),
    "volume down [<n>]": Key("volumedown:%(n)d"),
    
    # mouse control, default dragon needs "mouse click, mouse right click, there is no middle click",
    # removed the optionality for "do", because PCbyVoice has "show taskbar" followed by "click <number>"
    "do [left] click": Mouse("left"),
    "[do] right click": Mouse("right"),
    "[do] middle click": Mouse("middle"),
    "[do] double click": Mouse("left:2"),
    "[do] triple click": Mouse("left:3"),
    "[do] start drag": Mouse("left:down"),
    "[do] stop drag": Mouse("left:up"),

    # To release keyboard capture by VirtualBox.
    "press right control": Key("Control_R"),   
            
    },
    namespace={
     "Key":   Key,
     "Text":  Text,
    }
)


# F1 to F12.
functionKeyMap = {
    'F one': 'f1',
    'F two': 'f2',
    'F three': 'f3',
    'F four': 'f4',
    'F five': 'f5',
    'F six': 'f6',
    'F seven': 'f7',
    'F eight': 'f8',
    'F nine': 'f9',
    'F ten': 'f10',
    'F eleven': 'f11',
    'F twelve': 'f12',
}

controlKeyMap = {
    "(left|loss)": "left", # leaf was getting confused with lape i.e. left parenthesis
    "(right|ross)": "right",
    "(up|gup|gope|goop)": "up",
    "(down|gun|gown)": "down",
    "(page up|powp|pope)": "pgup",
    "(page down|pown|pound)": "pgdown",
    "(home|west)": "home",
    "(end|east)": "end",
    "(space|spooce)": "space",
    "(enter|return|slap|loon|shock)": "enter",
    "(escape|scape|act|cancel)": "escape",
    "(tab|tub|tabby|tubby|jump)": "tab",
    "(context-menu|pop up|menu key|application key)": "apps",
    "(delete|crack)": "del",
    "(backspace|chook)": "backspace",
}

numberKeyMap = {
    "zero": "0",
    "(one|Ono)": "1", # "one" !!?? this is not getting recognized and I have to say press one, just added "Ono" let's see how that works
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}

letterKeyMap = {
    # NATO letter names/utterances
    "alpha": "a",
    "bravo": "b",
    "charlie": "c",
    "delta": "d",
    "echo": "e",
    "foxtrot": "f",
    "golf": "g",
    "hotel": "h",
    "india": "i",
    "juliet": "j",
    "kilo": "k",
    "lima": "l",
    "mike": "m",
    "november": "n",
    "oscar": "o",
    "papa": "p",
    "quebec": "q",
    "romeo": "r",
    "sierra": "s",
    "tango": "t",
    "uniform": "u",
    "victor": "v",
    "whiskey": "w",
    "x-ray": "x",
    "yankee": "y",
    "zulu": "z",
            
    # short letter names/utterances
    #        "(arch|alpha|alph|elf)": "a",
    "arch": "a",
#        "(bravo|brav|brov)": "b",
    "brov": "b",
#        "(charlie|char)": "c",
    "char": "c",
#        "delta": "d",
    "dell": "d",
#        "echo|eco|etch|eck": "e",
    "(eeks|echo|edge)": "e",
#        "(foxtrot|fox|fomp)": "f",
    "fox|fomp": "f",
#        "(golf|goal)": "g",
    "(golf|goof|Geek)": "g",
#        "(hotel|hot|hark)": "h",
    "hark": "h",
#        "(India|indigo|ice)": "i",
    "ice": "i",
#        "(Juliet|Julie|jewel)": "j",
    "Julie": "j",
#        "(kilo|keel|kill)": "k",
    "(kill|keel)": "k",
#        "(lima|limb)": "l",
    "limb": "l",
#        "(Mike|Mick)": "m",
    "Mick": "m",
#        "(November|nov|nova)": "n",
    "(nova|nov)": "n",
#        "(oscar|osh)": "o",
    "owsh": "o", # pronounce it as a-w-sh o-u-sh o-sh
#        "(papa|pup|puppy)": "p",
    "pup": "p",
#        "(Quebec|queen)": "q",
    "queen": "q",
#        "(Romeo|Rome|rom)": "r",
    "Roche": "r",
#        "(Sierra|souk)": "s",
    "souk": "s",
#        "(Tango|tang|teek)": "t",
    "teek": "t",
#        "(uniform|uni)": "u",
    "uni": "u",
#        "(Victor|vic)": "v",
    "vic": "v",
#        "(whiskey|whis|whisk|womp)": "w",
    "(whis|whisk)": "w",
#        "(x-ray|ex)": "x",
    "x-ray": "x",
#        "(Yankee|yank|yang)": "y",
    "yank": "y",
#        "(Zulu|zoo)": "z",
    "Zulu": "z",      
}

symbolKeyMap = {
    "([vertical] bar|pipe)": "bar", #"|",
    "(dash|minus|hyphen)": "minus", #"-",
    "(dot|dotty|period|point|dit|doot)": "dot", #".",
    "(comma|commy|comy)": "comma", #",",  # comma not working as a command, so I added alternatives
    "(backslash|blash|clash)": "backslash", #"\\", # backslash doesn't seem to work, so I added blash & clash, the symbols that seem not to work are the ones that when I say "say symbol_name" --prints this--> \symbol_name, like this --> \backslash
    "([forward] slash|flash|lash|slashy)": "slash", #"/", # the word slash stopped working (maybe it wasn't working from the beginning), so I added flash & lash
    "(score|underscore)": "underscore", #"_", # underscore seems not working, and saying "say|dictate underscore" --prints this-> _\underscore
    "(star|asterisk)": "asterisk", #"*",
    "(colon|colly)": "colon", #":",
    "(semicolon|semi)": "semicolon", #";",
    "at (sign|symbol)|atte": "at", #"@", # "at sign"  doesn't work, "at" on its own not a good idea
    "[double] quote": "doublequote", #'"',
    "(single [quote]|sing)": "singlequote", #"'",
    "hash": "hash", #"#",
    "dollar|dolly": "dollar", #"$", # i just liked dolly as well
    "percent|centy": "percent", #"%", # just going with the flow
    "and (sign|symbol)|ampersand|sandy": "ampersand", #"&",  # ampersand doesn't seem to work, and symbol or sign seems heavy to recognize, sandy is going with the flow
#    "(equal|equals|eeks)": "=",
    "(equal|equals)": "equals", #"=", # using "eeks" for e instead of the problematic echo|etch|eck
    "plus [sign]": "plus", #"+",
    "space": "space", #" ",
    "(less than|lang|langle)": "langle", #"<",
    "(greater than|rang|rangle)": "rangle", #">",
    "(lape|len)": "lparen", #'(',
    "(rape|ren)": "rparen", #")",
    "lace": "lbrace", #"{",
    "race": "rbrace", #"}",
    "lack": "lbracket", #"[",
    "rack": "rbracket", #"]",
    "(question|question mark|quest)": "question", #"?",
    "(backtick)": "backtick", #"`", # remove tick confused with teek and bing not used
    "(caret|carrot)": "caret", #"^",
    "tilde": "tilde", #"~",
    "(exclamation [mark]|bang|clam|clammy)": "exclamation", #"!",
}

# this is the shorthand for press with another key and release
# example: Key("c-v")
# Modifiers for the press-command.
modifierMap = {
    "(alt|alternative|meta|diamond|command)": "a",
    "control": "c",
    "(shift|sky)": "s",
    "(super|windows key|win key)": "w", # don't want to use the utterance Win or Windows, as i think it is used alot elsewere, so keeping it simple for now, (dragon uses "press Windows key" or "click Start"
}

# this is a mapping from utterance to the name of the key internally in dragonfly
# example: Key("alt", "dot") , which
# Modifiers for the press-command, if only the modifier is pressed.
singleModifierMap = {
    "(alt|alternative|meta|diamond|command)": "alt",
    "control": "ctrl",
    "(shift|sky)": "shift",
    "(super|windows key|win key)": "win",
}

            
# notice .update to the previously/above defined/created config.cmd.map
# mapping from spoken form (dragonfly spec) to dragonfly action (Key, Text, i think there is more)
# the angle brackets surrounded things, are dragonfly's extras list, which contain Choice objects, created in class KeystrokeRule
# the different Choice object were created using Python dictionaries defined above, where the dictionary key is the spoken form in the dictionary value is the name of the keyboard key as dragonfly Python library knows/defines/calls it internally.
config.cmd.map.update({

#--------------------------
# ONE FINGER on keyboard
#--------------------------
    # i believe this holds down the button till a release command is issued
    "hold <modifierSingle>":         Key("%(modifierSingle)s"),
    "release <modifierSingle>":      Key("%(modifierSingle)s"),
    
    # press any key on the keyboard, once, no repetition included yet, you can say of course delta repeat 3 times, but repeat number of times comes from another rule down below in the file
    # "[press] <pressKey>": Key("%(pressKey)s"),  # @IgnorePep8    
    "press <functionKey>": Key("%(functionKey)s"),  # @IgnorePep8
    "[press] <controlKey> [<n>]": Key("%(controlKey)s:%(n)d"),  # @IgnorePep8
    "[press] <numberKey>": Key("%(numberKey)s"),  # @IgnorePep8
    "[press] <letterKey>": Key("%(letterKey)s"),  # @IgnorePep8
    "[press] <symbolKey>": Key("%(symbolKey)s"),  # @IgnorePep8    

#--------------------------
#TWO FINGERS on keyboard
#--------------------------
    # key combinations, i will split it into smaller pieces to avoid unneeded/unsued combinations, to keep the grammer simpler and thereby less error prone
    #-------------------------------------------------------------------
    
    #"[press] <modifier1> <pressKey>": Key("%(modifier1)s-%(pressKey)s"),  # @IgnorePep8
    #"[press] <modifier1> <modifier2> <pressKey>": Key("%(modifier1)s%(modifier2)s-%(pressKey)s"),  # @IgnorePep8
    
    # i don't need this yet
    # "press <modifier1> <functionKey>": Key("%(modifier1)s-%(functionKey)s"),  # @IgnorePep8
    
    # like "press alt space" = clicking right left corner of a window or right clicking anywhere on the title bar of a window, opens menu for minimize maximize restore close and more
    # like press alt left|right|up for backaward and forward and up one level in browser and file browser
    # like super up for maximize
    # like control left or right to jump words
    "[press] <modifier1> <controlKey> [<n>]": Key("%(modifier1)s-%(controlKey)s:%(n)d"),  # @IgnorePep8
    # tried the above with repetition [<n>] but it didn't work before, I tried and now and seems it works
    # also you can say "shift up [repeat] 3 times", as defined in the (class RepeatRule(CompoundRule))
    
    # might simplify this later, and use only Super out of the 4 modifiers, use only for example super + number as other uses are probably not needed
    # like super 1 or super 2 to choose an open applicaiton from the task bar
    # like shift number, for symbols when i get stuck
    "[press] <modifier1> <numberKey>": Key("%(modifier1)s-%(numberKey)s"),  # @IgnorePep8
    
    # shift letter for uppercase
    # super + d to show desktop
    # control v to paste
    # alt d to delete a word forward, control w to delete a word backward, in linux terminal
    "[press] <modifier1> <letterKey>": Key("%(modifier1)s-%(letterKey)s"),  # @IgnorePep8
    
    # like alt dot in linux terminal for last argument from last command in history similar to escape dot, but escape is not and doesn't need to be in modifierMap
    "[press] <modifier1> <symbolKey>": Key("%(modifier1)s-%(symbolKey)s"),  # @IgnorePep8
    
#--------------------------
# THREE FINGERS on keybaord
#--------------------------
    # two modifier keys then a normal keyboard key
    # like control alt tango, to open a terminal in ubuntu linux
    # like control shift tango, to reopen a closed tab in browser or notepad++
    # this seems too much, so categorizing like above to only what i know i need and keeping it simpler    
    #"[press] <modifier1> <modifier2> <pressKey>": Key("%(modifier1)s%(modifier2)s-%(pressKey)s"),  # @IgnorePep8 # this did not seem to be necessary when I tested earlier for combinations like control+alt+t to open a new terminal in X11 on Ubuntu Linux
    "[press] <modifier1> <modifier2> <letterKey>": Key("%(modifier1)s%(modifier2)s-%(letterKey)s"),  # @IgnorePep8
    
    "[press] <modifier1> <modifier2> <controlKey>": Key("%(modifier1)s%(modifier2)s-%(controlKey)s"),  # @IgnorePep8
    #
})

#this generates a config file, in this directory, named _keyboard.txt, but needs manual fixing, just enable this line once then comment it out.
#config.generate_config_file()
# these config files get reloaded automatically when they are edited and saved without the need to sleep and wake up or microphone off and microphone on, because they are monitored for changes by _dragonfly_tools.py (class ConfigManagerGrammar(Grammar))
namespace = config.load()

#---------------------------------------------------------------------------
# Here we prepare the list of formatting functions from the config file.

# Retrieve text-formatting functions from this module's config file.
#  Each of these functions must have a name that starts with "format_".
format_functions = {}
if namespace:
    for name, function in namespace.items():
        if name.startswith("format_") and callable(function):
            spoken_form = function.__doc__.strip()

            # We wrap generation of the Function action in a function so
            #  that its *function* variable will be local.  Otherwise it
            #  would change during the next iteration of the namespace loop.
            def wrap_function(function):
                def _function(dictation):
                    formatted_text = function(dictation)
                    Text(formatted_text).execute()
                return Function(_function)

            action = wrap_function(function)
            format_functions[spoken_form] = action


# Here we define the text formatting rule.
# The contents of this rule were built up from the "format_*"
#  functions in this module's config file.
if format_functions:
    class FormatRule(MappingRule):

        mapping  = format_functions
        extras   = [Dictation("dictation")]

else:
    FormatRule = None


#---------------------------------------------------------------------------
# Here we define the keystroke rule.

# This rule maps spoken-forms to actions.  Some of these 
#  include special elements like the number with name "n" 
#  or the dictation with name "text".  This rule is not 
#  exported, but is referenced by other elements later on.
#  It is derived from MappingRule, so that its "value" when 
#  processing a recognition will be the right side of the 
#  mapping: an action.
# Note that this rule does not execute these actions, it
#  simply returns them when it's value() method is called.
#  For example "up 4" will give the value Key("up:4").
# More information about Key() actions can be found here:
#  http://dragonfly.googlecode.com/svn/trunk/dragonfly/documentation/actionkey.html
class KeystrokeRule(MappingRule):

    exported = False

    mapping  = config.cmd.map
    extras = [
        IntegerRef("n", 1, 100),
        Dictation("text"),
        Dictation("text2"),
        Choice("functionKey", functionKeyMap),
        Choice("controlKey", controlKeyMap),
        Choice("numberKey", numberKeyMap),
        Choice("letterKey", letterKeyMap),
        Choice("symbolKey", symbolKeyMap),
        Choice("modifier1", modifierMap),
        Choice("modifier2", modifierMap),
        Choice("modifierSingle", singleModifierMap),
#        Choice("pressKey", pressKeyMap),
#        Choice("formatType", formatMap),
#        Choice("abbreviation", abbreviationMap),
#        Choice("reservedWord", reservedWord), 
               ]
    defaults = {
                "n": 1,
               }
    # Note: when processing a recognition, the *value* of 
    #  this rule will be an action object from the right side 
    #  of the mapping given above.  This is default behavior 
    #  of the MappingRule class' value() method.  It also 
    #  substitutes any "%(...)." within the action spec
    #  with the appropriate spoken values.


#---------------------------------------------------------------------------
# Here we create an element which is the sequence of keystrokes.

# First we create an element that references the keystroke rule.
#  Note: when processing a recognition, the *value* of this element
#  will be the value of the referenced rule: an action.
alternatives = []
alternatives.append(RuleRef(rule=KeystrokeRule()))
if FormatRule:
    alternatives.append(RuleRef(rule=FormatRule()))
single_action = Alternative(alternatives)

# Second we create a repetition of keystroke elements.
#  This element will match anywhere between 1 and 16 repetitions
#  of the keystroke elements.  Note that we give this element
#  the name "sequence" so that it can be used as an extra in
#  the rule definition below.
# Note: when processing a recognition, the *value* of this element
#  will be a sequence of the contained elements: a sequence of
#  actions.
sequence = Repetition(single_action, min=1, max=16, name="sequence")


#---------------------------------------------------------------------------
# Here we define the top-level rule which the user can say.

# This is the rule that actually handles recognitions. 
#  When a recognition occurs, it's _process_recognition() 
#  method will be called.  It receives information about the 
#  recognition in the "extras" argument: the sequence of 
#  actions and the number of times to repeat them.
class RepeatRule(CompoundRule):

    # Here we define this rule's spoken-form and special elements.
    spec     = "<sequence> [[[and] repeat [that]] <n> times]"
    extras   = [
                sequence,                 # Sequence of actions defined above.
                IntegerRef("n", 1, 100),  # Times to repeat the sequence.
               ]
    defaults = {
                "n": 1,                   # Default repeat count.
               }

    # This method gets called when this rule is recognized.
    # Arguments:
    #  - node -- root node of the recognition parse tree.
    #  - extras -- dict of the "extras" special elements:
    #     . extras["sequence"] gives the sequence of actions.
    #     . extras["n"] gives the repeat count.
    def _process_recognition(self, node, extras):
        sequence = extras["sequence"]   # A sequence of actions.
        count = extras["n"]             # An integer repeat count.
        for i in range(count):
            for action in sequence:
                action.execute()
        release.execute()


#---------------------------------------------------------------------------
# Create and load this module's grammar.

grammar = Grammar("keyboard")   # Create this module's grammar.
grammar.add_rule(RepeatRule())    # Add the top-level rule.
grammar.load()                    # Load the grammar.

# Unload function which will be called at unload time.
def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None

