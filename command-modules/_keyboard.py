"""A command module for Dragonfly, for generic editing help.

-----------------------------------------------------------------------------
This is a heavily modified version of the _multiedit-en.py script at:
http://dragonfly-modules.googlecode.com/svn/trunk/command-modules/documentation/mod-_multiedit.html  # @IgnorePep8
Licensed under the LGPL, see http://www.gnu.org/licenses/

"""
from natlink import setMicState
from dragonfly import (
    Choice,
    Pause,
    Window,
    FocusWindow,
    Config,
    Section,
    Item,
    Function,
    Dictation,
    IntegerRef,
    MappingRule,
    Alternative,
    RuleRef,
    Grammar,
    Repetition,
    CompoundRule,
    AppContext,
    Mouse,
    Key,
    Text,
)

import win32con
from dragonfly.actions.keyboard import Typeable, keyboard
from dragonfly.actions.typeables import typeables
if not 'Control_R' in typeables:
    keycode = win32con.VK_RCONTROL
    typeables["Control_R"] = Typeable(code=keycode, name="Control_R")
if not 'semicolon' in typeables:
    typeables["semicolon"] = keyboard.get_typeable(char=';')

    
import lib.sound as sound
from lib.format import (
    camel_case_count,
    pascal_case_count,
    snake_case_count,
    title_case_count,
    squash_count,
    expand_count,
    uppercase_count,
    lowercase_count,
    format_text,
    FormatTypes as ft,
)


release = Key("shift:up, ctrl:up, alt:up")


def cancel_and_sleep(text=None, text2=None):
    """Used to cancel an ongoing dictation and puts microphone to sleep.

    This method notifies the user that the dictation was in fact canceled,
    with a sound and a message in the Natlink feedback window.
    Then the the microphone is put to sleep.
    Example:
    "'random mumbling go to sleep'" => Microphone sleep.

    """
    print("* Dictation canceled. Going to sleep. *")
    sound.play(sound.SND_DING)
    setMicState("sleeping")

# this functionaly is already in _dragonfly_tools.py
#def reload_natlink():
#    """Reloads Natlink and custom Python modules."""
#    win = Window.get_foreground()
#    FocusWindow(executable="natspeak",
#        title="Messages from Python Macros").execute()
#    Pause("10").execute()
#    Key("a-f, r").execute()
#    Pause("10").execute()
#    win.set_foreground()


specialCharMap = {
    "(bar|vertical bar)": "|",
    "(pipe)": " | ",
    "(dash|minus|hyphen)": "-",
    "(dotty|period|point|dit|doot)": ".", # replaced the utterance "dot" with "dotty" as it was very frequently getting recognised  when I say the utterance Delta/dell for d
    "(comma|commy|comy)": ",",  # comma not working as a command, so I added alternatives
    "backslash": "\\",
    "([forward]slash)": "/",
    "(underscore)": "_",
    "(star|asterisk)": "*",
    "(colon|colly)": ":",
    "(semicolon|semi)": ";",
    "at (sign|symbol)|atte": "@", # "at sign"  doesn't work, "at" on its own not a good idea
    "[double] quote": '"',
    "(single [quote]|sing)": "'",
    "hash": "#",
    "dollar|dolly": "$", # i just liked dolly as well
    "percent|centy": "%", # just going with the flow
    "and (sign|symbol)|ampersand|sandy": "&",  # ampersand doesn't seem to work, and symbol or sign seems heavy to recognize, sandy is going with the flow
#    "(equal|equals|eeks)": "=",
    "(equal|equals)": "=", # using "eeks" for e instead of the problematic echo|etch|eck
    "plus [sign]": "+",
    "space": " ",
    # adding missing characters
    "(less than|lang|langle)": "<",
    "(greater than|rang|rangle)": ">",
    "(lape|len)": '(',
    "(rape|ren)": ")",
    "lace": "{",
    "race": "}",
    "lack": "[",
    "rack": "]",
    # more missing symbols
    "(question [mark]|quest)": "?",
    "(back tick)": "`", # remove tick confused with teek and bing not used
    "(caret|carrot)": "^",
    "tilde": "~",
    "(exclamation [mark]|bang|clam|clammy)": "!",
}

# need the name for a character when using the Key()function, something like modifierMap vs singleModifierMap
specialCharNameMap = {
#    "(dot|period|point|dit|doot)": "dot",
    "(dotty|period|point|dit|doot)": "dot",
}

# Modifiers for the press-command.
modifierMap = {
    "alt|alternative|meta|diamond|command": "a",
    "control": "c",
    "shift|sky": "s",
    "super": "w",
}

# Modifiers for the press-command, if only the modifier is pressed.
singleModifierMap = {
    "alt": "alt",
    "control": "ctrl",
    "shift": "shift",
    "super": "win",
}

letterMap = {
#        "(arch|alpha|alph|elf)": "a",
        "arch": "a",
#        "(bravo|brav|brov)": "b",
        "brov": "b",
#        "(charlie|char)": "c",
        "char": "c",
#        "delta": "d",
        "dell": "d",
#        "echo|eco|etch|eck": "e",
        "eeks|echo": "e",
#        "(foxtrot|fox|fomp)": "f",
        "fox|fomp": "f",
#        "(golf|goal)": "g",
        "golf|goof": "g",
#        "(hotel|hot|hark)": "h",
        "hark": "h",
#        "(India|indigo|ice)": "i",
        "ice": "i",
#        "(Juliet|Julie|jewel)": "j",
        "Julie": "j",
#        "(kilo|keel|kill)": "k",
        "keel": "k",
#        "(lima|limb)": "l",
        "limb": "l",
#        "(Mike|Mick)": "m",
        "Mick": "m",
#        "(November|nov|nova)": "n",
        "nova": "n",
#        "(oscar|osh)": "o",
        "owsh": "o", # pronounce it as a-w-sh o-u-sh o-sh
#        "(papa|pup|puppy)": "p",
        "pup": "p",
#        "(Quebec|queen)": "q",
        "queen": "q",
#        "(Romeo|Rome|rom)": "r",
        "rom": "r",
#        "(Sierra|souk)": "s",
        "souk": "s",
#        "(Tango|tang|teek)": "t",
        "teek": "t",
#        "(uniform|uni)": "u",
        "uni": "u",
#        "(Victor|vic)": "v",
        "vic": "v",
#        "(whiskey|whis|whisk|womp)": "w",
        "whis": "w",
#        "(x-ray|ex)": "x",
        "x-ray": "x",
#        "(Yankee|yank|yang)": "y",
        "yank": "y",
#        "(Zulu|zoo)": "z",
        "Zulu": "z",
}

numberMap = {
    "zero": "0",
    "one": "1", # this is not getting recognised and I have to say press one
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}

controlKeyMap = {
    "left": "left",
    "right": "right",
    "up": "up",
    "down": "down",
    "page up": "pgup",
    "page down": "pgdown",
    "home": "home",
    "end": "end",
    "space": "space",
    "(enter|return)": "enter",
    "escape": "escape",
    "tab": "tab"
}

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

pressKeyMap = {}
pressKeyMap.update(letterMap)
pressKeyMap.update(numberMap)
pressKeyMap.update(controlKeyMap)
#pressKeyMap.update(functionKeyMap)


formatMap = {
    "camel case": ft.camelCase,
    "pascal case": ft.pascalCase,
    "snake case": ft.snakeCase,
    "title case": ft.titleCase,
    "uppercase": ft.upperCase,
    "lowercase": ft.lowerCase,
    "squash": ft.squash,
    "lowercase squash": [ft.squash, ft.lowerCase],
    "uppercase squash": [ft.squash, ft.upperCase],
    "squash lowercase": [ft.squash, ft.lowerCase],
    "squash uppercase": [ft.squash, ft.upperCase],
    "dashify": ft.dashify,
    "lowercase dashify": [ft.dashify, ft.lowerCase],
    "uppercase dashify": [ft.dashify, ft.upperCase],
    "dashify lowercase": [ft.dashify, ft.lowerCase],
    "dashify uppercase": [ft.dashify, ft.upperCase],
    "dotify": ft.dotify,
    "lowercase dotify": [ft.dotify, ft.lowerCase],
    "uppercase dotify": [ft.dotify, ft.upperCase],
    "dotify lowercase": [ft.dotify, ft.lowerCase],
    "dotify uppercase": [ft.dotify, ft.upperCase],
    "say": ft.spokenForm,
    "environment variable": [ft.snakeCase, ft.upperCase],
}


# abbreviationMap = {
    # "administrator": "admin",
    # "administrators": "admins",
    # "application": "app",
    # "applications": "apps",
    # "argument": "arg",
    # "arguments": "args",
    # "attribute": "attr",
    # "attributes": "attrs",
    # "(authenticate|authentication)": "auth",
    # "binary": "bin",
    # "button": "btn",
    # "class": "cls",
    # "command": "cmd",
    # "(config|configuration)": "cfg",
    # "context": "ctx",
    # "control": "ctrl",
    # "database": "db",
    # "(define|definition)": "def",
    # "description": "desc",
    # "(develop|development)": "dev",
    # "(dictionary|dictation)": "dict",
    # "(direction|directory)": "dir",
    # "dynamic": "dyn",
    # "example": "ex",
    # "execute": "exec",
    # "exception": "exc",
    # "expression": "exp",
    # "(extension|extend)": "ext",
    # "function": "func",
    # "framework": "fw",
    # "(initialize|initializer)": "init",
    # "instance": "inst",
    # "integer": "int",
    # "iterate": "iter",
    # "java archive": "jar",
    # "javascript": "js",
    # "keyword": "kw",
    # "keyword arguments": "kwargs",
    # "language": "lng",
    # "library": "lib",
    # "length": "len",
    # "number": "num",
    # "object": "obj",
    # "okay": "ok",
    # "package": "pkg",
    # "parameter": "param",
    # "parameters": "params",
    # "pixel": "px",
    # "position": "pos",
    # "point": "pt",
    # "previous": "prev",
    # "property": "prop",
    # "python": "py",
    # "query string": "qs",
    # "reference": "ref",
    # "references": "refs",
    # "(represent|representation)": "repr",
    # "regular (expression|expressions)": "regex",
    # "request": "req",
    # "revision": "rev",
    # "ruby": "rb",
    # "session aidee": "sid",  # "session id" didn't work for some reason.
    # "source": "src",
    # "(special|specify|specific|specification)": "spec",
    # "standard": "std",
    # "standard in": "stdin",
    # "standard out": "stdout",
    # "string": "str",
    # "(synchronize|synchronous)": "sync",
    # "system": "sys",
    # "utility": "util",
    # "utilities": "utils",
    # "temporary": "tmp",
    # "text": "txt",
    # "value": "val",
    # "window": "win",
# }

# For use with "say"-command. Words that are commands in the generic edit
# grammar were treated as separate commands and could not be written with the
# "say"-command. This overrides that behavior.
# Other words that won't work for one reason or another, can also be added to
# this list.
reservedWord = {
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "home": "home",
    "end": "end",
    "space": "space",
    "tab": "tab",
    "backspace": "backspace",
    "delete": "delete",
    "enter": "enter",
    "paste": "paste",
    "copy": "copy",
    "cut": "cut",
    "undo": "undo",
    "release": "release",
    "page up": "page up",
    "page down": "page down",
    "say": "say",
    "select": "select",
    "select all": "select all",
    "abbreviate": "abbreviate",
    "uppercase": "uppercase",
    "lowercase": "lowercase",
    "expand": "expand",
    "squash": "squash",
    "dash": "dash",
    "underscore": "underscore",
    "dot": "dot",
    "period": "period",
    "minus": "minus",
    "semi-colon": "semi-colon",
    "hyphen": "hyphen",
    "triple": "triple",
    "snore": "snore",
}


def copy_command():
    # Add Command Prompt, putty, ...?
    context = AppContext(executable="console")
    window = Window.get_foreground()
    if context.matches(window.executable, window.title, window.handle):
        return
    release.execute()
    Key("c-c/3").execute()


def paste_command():
    # Add Command Prompt, putty, ...?
    context = AppContext(executable="console")
    window = Window.get_foreground()
    if context.matches(window.executable, window.title, window.handle):
        return
    release.execute()
    Key("c-v/3").execute()


grammarCfg = Config("keyboard")
grammarCfg.cmd = Section("Language section")
grammarCfg.cmd.map = Item(
    {
        # Navigation keys.
        "(up|gup|gope) [<n>]": Key("up:%(n)d"),
        "(up|gup|gope) [<n>] slow": Key("up/15:%(n)d"),
        "(down|gun|gown) [<n>]": Key("down:%(n)d"),
        "(down|gun|gown) [<n>] slow": Key("down/15:%(n)d"),
        "(left|leaf) [<n>]": Key("left:%(n)d"),
        "(left|leaf) [<n>] slow": Key("left/15:%(n)d"),
        "(right|Ross) [<n>]": Key("right:%(n)d"),
        "(right|Ross) [<n>] slow": Key("right/15:%(n)d"),
        "(page up|pope|powp) [<n>]": Key("pgup:%(n)d"),
        "(page down|pown|pound) [<n>]": Key("pgdown:%(n)d"),    # pown is getting confused with home
        "up <n> (page|pages)": Key("pgup:%(n)d"),
        "down <n> (page|pages)": Key("pgdown:%(n)d"),
        "left <n> (word|words)": Key("c-left/3:%(n)d/10"),
        "right <n> (word|words)": Key("c-right/3:%(n)d/10"),
        "home|West": Key("home"),
        "end|East": Key("end"),
        "doc home|North": Key("c-home/3"),
        "doc end|South": Key("c-end/3"),
        # Shorthand word jumps and deletes
        "fomble [<n>]": Key("c-right/5:%(n)d"),
        "kimble [<n>]": Key("c-del/5:%(n)d"),
        "bamble [<n>]": Key("c-left/5:%(n)d"),
        "dumbbell [<n>]": Key("c-backspace/5:%(n)d"),
        # Functional keys.
        "space|ace|spooce": release + Key("space"),
        "(space|ace|spooce) [<n>]": release + Key("space:%(n)d"),
        "(enter|slap|loon|shock) [<n>]": release + Key("enter:%(n)d"),
        "(tab|tabby|tub|tubby) [<n>]": Key("tab:%(n)d"),
        "(delete|crack) [<n>]": Key("del/3:%(n)d"),
        "(delete|crack) [this] line": Key("home, s-end, del"),  # @IgnorePep8
        "(backspace|chook) [<n>]": release + Key("backspace:%(n)d"),
        "(application key|context menu)": release + Key("apps/3"),
        "win key": release + Key("win/3"),
        "paste [that]": Function(paste_command),
        "copy [that]": Function(copy_command),
        "cut [that]": release + Key("c-x/3"),
        "select all": release + Key("c-a/3"),
        "undo": release + Key("c-z/3"),
        "undo <n> [times]": release + Key("c-z/3:%(n)d"),
        "redo": release + Key("c-y/3"),
        "redo <n> [times]": release + Key("c-y/3:%(n)d"),
        "[(hold|press)] alt": Key("alt:down/3"),
        "release alt": Key("alt:up"),
        "[(hold|press)] shift": Key("shift:down/3"),
        "release shift": Key("shift:up"),
        "[(hold|press)] control": Key("ctrl:down/3"),
        "release control": Key("ctrl:up"),
        "release [all]": release,
        # Closures.
        "angle brackets": Key("langle, rangle, left/3"),
        "brackets": Key("lbracket, rbracket, left/3"),
        "braces": Key("lbrace, rbrace, left/3"),
        "parens": Key("lparen, rparen, left/3"),
        "quotes": Key("dquote/3, dquote/3, left/3"),
        "single quotes": Key("squote, squote, left/3"),
        # Shorthand multiple characters.
        "double <char>": Text("%(char)s%(char)s"),
        "triple <char>": Text("%(char)s%(char)s%(char)s"),
        "double escape": Key("escape, escape"),  # Exiting menus.
        # Punctuation and separation characters, for quick editing.
        #"colon [<n>]": Key("colon/2:%(n)d"),
        #"semi-colon [<n>]": Key("semicolon/2:%(n)d"),
        #"comma [<n>]": Key("comma/2:%(n)d"),
        #"(dot|period) [<n>]": Key("dot/2:%(n)d"),
        #"(dash|hyphen|minus) [<n>]": Key("hyphen/2:%(n)d"),
        #"underscore [<n>]": Key("underscore/2:%(n)d"),
        # To release keyboard capture by VirtualBox.
        "press right control": Key("Control_R"),
        # Formatting <n> words to the left of the cursor.
        "camel case <n> [words]": Function(camel_case_count),
        "pascal case <n> [words]": Function(pascal_case_count),
        "snake case <n> [words]": Function(snake_case_count),
        "title case <n> [words]": Function(title_case_count),
        "squash <n> [words]": Function(squash_count),
        "expand <n> [words]": Function(expand_count),
        "uppercase <n> [words]": Function(uppercase_count),
        "lowercase <n> [words]": Function(lowercase_count),
        # Format dictated words. See the formatMap for all available types.
        # Ex: "camel case my new variable" -> "myNewVariable"
        # Ex: "snake case my new variable" -> "my_new_variable"
        # Ex: "uppercase squash my new hyphen variable" -> "MYNEW-VARIABLE"
        "<formatType> <text>": Function(format_text),
        # For writing words that would otherwise be characters or commands.
        # Ex: "period", tab", "left", "right", "home".
        "say <reservedWord>": Text("%(reservedWord)s"),
        # Abbreviate words commonly used in programming.
        # Ex: arguments -> args, parameters -> params.
#        "abbreviate <abbreviation>": Text("%(abbreviation)s"),
        # Text corrections.
        "(add|fix) missing space": Key("c-left/3, space, c-right/3"),
        "(delete|remove) (double|extra) (space|whitespace)": Key("c-left/3, backspace, c-right/3"),  # @IgnorePep8
        "(delete|remove) (double|extra) (type|char|character)": Key("c-left/3, del, c-right/3"),  # @IgnorePep8
        # Microphone sleep/cancel started dictation.
        "[<text>] (snore|go to sleep|cancel and sleep) [<text2>]": Function(cancel_and_sleep),  # @IgnorePep8
        # Reload Natlink.
        # errors and fails on win7_64bit i think because pywin is 32bit
        # Reloading Python subsystem...
        # some error occurred
        # Traceback (most recent call last):
        # File "C:\NatLink\NatLink\MacroSystem\core\natlinkmain.py", line 146, in <module>
        # import natlinkstatus    # for extracting status info (QH)
        # File "C:\NatLink\NatLink\MacroSystem\core\natlinkstatus.py", line 180, in <module>
        # import RegistryDict, natlinkcorefunctions
        # File "C:\NatLink\NatLink\MacroSystem\core\natlinkcorefunctions.py", line 31, in <module>
        # from win32com.shell import shell, shellcon
        # File "C:\Python27\lib\site-packages\win32com\__init__.py", line 82, in <module>
        # SetupEnvironment()
        # File "<string>", line 3, in __init__
        # TypeError: 'NoneType' object is not callable
        #"reload Natlink": Function(reload_natlink),
    },
    namespace={
        "Key": Key,
        "Text": Text,
    }
)

# general windows and browser navigation command
grammarCfg.cmd.map.update({
    # tab control in browsers and gnome-shell
    "(preet|pret) [<n>]": Key("c-pgup/5:%(n)d"),
    "(neat|net) [<n>]": Key("c-pgdown/5:%(n)d"),
    "clote": Key("c-w"),
    
    # for browsers and for Windows Explorer / file manager
    "backward":    Key("a-left"),
    "forward":    Key("a-right"),
    "upward":    Key("a-up"),
    
    # Windows control
    "win toggle": Key("win:down, tab/25:3, win:up"),
    "win stack": Key("ctrl:down, win:down, tab:down") + Key("control:up, win:up, tab:up"),
    "win flip": Key("alt:down, tab:down/5, alt:up"),    # the 5 is outerpause and is about the minimum for this to work
    "win slide": Key("ctrl:down, alt:down, tab:down") + Key("control:up, alt:up, tab:up"),

    "volume up [<n>]": Key("volumeup:%(n)d"),
    "volume down [<n>]": Key("volumedown:%(n)d"),

    # mouse clicks
    # somtimes some clicks may not work well into Oracle irtual box, but the middle click seems to kind of always work
    "do click": Mouse("left"),
    "do right click": Mouse("right"),
    "do middle click": Mouse("middle"),
    "do double click": Mouse("left:2"),
    "do triple click": Mouse("left:3"),
    "do start drag": Mouse("left:down"),
    "do stop drag": Mouse("left:up"),
    })


grammarCfg.cmd.map.update({
    "[press] <pressKey>": Key("%(pressKey)s"),  # @IgnorePep8 # enabling pressKey = pressKeyMap = (letterMap), (numberMap), (controlKeyMap), (functionKeyMap)
    "[press] <char>":     Text("%(char)s"),  # @IgnorePep8 # enabling char/specialCharMap
    "[press] <modifier1> <pressKey>": Key("%(modifier1)s-%(pressKey)s"),  # @IgnorePep8 # This did not seem to be  necessary when I tested earlier for combinations like super+right or super+left or super+d or super+1 or super+5 etc to work
    "[press] <modifier1> <modifier2> <pressKey>": Key("%(modifier1)s%(modifier2)s-%(pressKey)s"),  # @IgnorePep8 # this did not seem to be necessary when I tested earlier for combinations like control+alt+t to open a new terminal in X11 on Ubuntu Linux
    "[press] <modifier1> <charName>": Key("%(modifier1)s-%(charName)s"),  # @IgnorePep8 # I discovered this missing when I was using meta+dot (=escape followed/with dot) to repeat the last commandline argument from the previous command in bash
})




# I couldn't get round this error
#  File "C:\Users\uc222343\Documents\GitHub\dragonfly-modules\command-modules\_dragonfly_tools.py", line 102, in _process_begin
#    if not os.path.isfile(c.config_path):
#  File "C:\Python27\Lib\genericpath.py", line 37, in isfile
#    st = os.stat(path)
#TypeError: coercing to Unicode: need string or buffer, NoneType found
# until I added this
config = grammarCfg
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
#---------------------------------------------------------------------------




class KeystrokeRule(MappingRule):
    exported = False
    mapping = grammarCfg.cmd.map
    extras = [
        IntegerRef("n", 1, 100),
        Dictation("text"),
        Dictation("text2"),
        Choice("char", specialCharMap),
        Choice("charName", specialCharNameMap),
        Choice("modifier1", modifierMap),
        Choice("modifier2", modifierMap),
        Choice("modifierSingle", singleModifierMap),
        Choice("pressKey", pressKeyMap),
        Choice("formatType", formatMap),
#        Choice("abbreviation", abbreviationMap),
        Choice("reservedWord", reservedWord),
    ]
    defaults = {
        "n": 1,
    }


alternatives = []
alternatives.append(RuleRef(rule=KeystrokeRule()))
single_action = Alternative(alternatives)


sequence = Repetition(single_action, min=1, max=16, name="sequence")


class RepeatRule(CompoundRule):
    # Here we define this rule's spoken-form and special elements.
    spec = "<sequence> [[[and] repeat [that]] <n> times]"
    extras = [
        sequence,  # Sequence of actions defined above.
        IntegerRef("n", 1, 100),  # Times to repeat the sequence.
    ]
    defaults = {
        "n": 1,  # Default repeat count.
    }

    def _process_recognition(self, node, extras):  # @UnusedVariable
        sequence = extras["sequence"]  # A sequence of actions.
        count = extras["n"]  # An integer repeat count.
        for i in range(count):  # @UnusedVariable
            for action in sequence:
                action.execute()
        release.execute()

grammar = Grammar("keyboard", context=None)
grammar.add_rule(RepeatRule())  # Add the top-level rule.
grammar.load()  # Load the grammar.


def unload():
    """Unload function which will be called at unload time."""
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
