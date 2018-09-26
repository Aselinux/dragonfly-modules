#
# This file is a command-module for Dragonfly.
# (c) Copyright 2018 by AseLinux
# Modified original dragonfly's _multiedit.py https://github.com/t4ngo/dragonfly-modules/blob/master/command-modules/_multiedit.py
# amalgamated with some ideas and thoughts from https://github.com/Aselinux/dragonfly-scripts/tree/master/dynamics
#
# (c) Copyright 2008 by Christo Butcher
# Licensed under the LGPL, see <http://www.gnu.org/licenses/>
#

"""
Command-module for sending **Bash commands**
==============================================

This module implements the "Bash commands" command.

Installation
----------------------------------------------------------------------------

If you are using DNS and Natlink, simply place this file in you Natlink 
macros directory.  It will then be automatically loaded by Natlink when 
you next toggle your microphone or restart Natlink.

"""

try:
    import pkg_resources
    pkg_resources.require("dragonfly >= 0.6.5beta1.dev-r76")
except ImportError:
    pass

from dragonfly import (Grammar, MappingRule, Key, Text, Config)
from lib.text import SCText # this should solve the problem of Text into Virtual box Bash terminal when there is successive for example (( being printed as (9


#---------------------------------------------------------------------------
# Set up this module's configuration.

config = Config("bash")
config.load()


#---------------------------------------------------------------------------
# Defined this module's main rule.

bash_rule = MappingRule(
    name="bash",
    mapping={
    
            # test bash
             "test bash": Text("this is from Text: :: ;; (( )) (((()))))") + SCText("this is from SCText: :: ;; (( )) (((()))))"),
             
            # terminal  
             "[keyboard] break": Key("c-c"),
             "new terminal": Key("ca-t"),
             "copy terminal": Key("cs-c/3"),
             "paste terminal": Key("cs-v/3"),
             
             # grep
             "grep [e]|[e] grep": Text("grep -Ei ''") + Key("left:1"),
             "grep directory": Text("grep -Eir '' ./") + Key("left:4"),
             "pipe grep": Text("grep -Ei ''") + Key("left"),
             "pipe grep": Text(" | grep -Ei ''") + Key("left"),
             "pipe (awkward|och)": Text(" | awk '{print $NF}'") + Key("left:2"),
             "pipe said": Text(" | sed 's///g'") + Key("left:4"),
             "[bash] pipe cut": Text(" | cut -d' ' -f1"),
             
            # Cron
             "cron tab edit": Text("crontab -e") + Key("enter"),
             "cron tab list": Text("crontab -l") + Key("enter"),             
            # directory
             "make (directory|dir)": Text("mkdir "),
             "change (directory|dir)": Text("cd "),
             "(change mode)|C H mod|che mod": Text("chmod "),
             "find file": Text("find ./ -iname '**'") + Key("left:2"),
                     
            # curl
             "curl help": SCText("curl -X --request GET -k --insecure -L --location -u --user $USER:$PASSWORD -A --user-agent 'AselCurl' -H --header 'Host: website.com' --header 'key1: value1' -b --cookie 'key1=value1; key2=value2' -v --verbose -t --trace-ascii /dev/stderr -D --dump-header /dev/stderr -d --data '{\"key1\": \"value1\", \"key2\": \"value2\"}' --url $URL"),
             "curl shabang": Text("curl -v -k -X GET -L --url "),
             
            # Ubuntu
             "pseudo ": Text("sudo "),
             "pseudo i": Text("sudo -i") + Key("enter"),
             "pseudo apt get ": Text("sudo apt-get "),
             "pseudo apt [cash] search": Text("sudo apt-cache search "),
             "debian package": Text("dpkg "),
             
            # processes
             "find process": Text("ps aux | grep -i "),
             "process forest": Text("ps auxf | less"),
             
            # git
             "git reset hard": Text("#git reset --hard HEAD ;# deletes everything after last commit"),
             "git reset soft": Text("#git reset --soft HEAD^ ;# moves head to parent HEAD~1 HEAD@{1}"),
             "git status": Text("git status") + Key("enter"),
             "git [log] follow": Text("git log --follow "),
             "git log": Text("git log ") + Key("enter"),
             
            # my commonly used commands
             "netstat": Text("netstat -v4 -antulp | grep -iE ''") + Key("left:%(n)d"),
             "E grep": Text("egrep -i ''") + Key("left:%(n)d"),
             "pipe grep": Text(" | grep -iE ''") + Key("left:%(n)d"),
             "pipe less": Text(" | less") + Key("enter:%(n)d"),
             "pipe head": Text(" | head") + Key("enter:%(n)d"),
             "pipe sort unique": Text(" | sort | uniq -c | sort -n -k1"),

             "T C P dump headers": SCText("sudo tcpdump -nn -i any -A -s 0 'tcp port 80 and (((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)' | egrep --line-buffered '^........(GET |HTTP\/|POST |HEAD )|^[A-Za-z0-9-]+: ' | sed -r 's/^.{8}(GET |HTTP\/|POST |HEAD )/\\n\\1/g'"),

             "pipe zargz": Text(" | xargs -I") + Key("percent") + Text(" "),

            # my common directories
             "less var log": Text("less /var/log/") + Key("tab:2"),
             "cat var log": Text("cat /var/log/") + Key("tab:2"),
             "var log": Text("/var/log/") + Key("tab:2"),
             "et see": Text("/etc/") + Key("tab:2"),
             "vim et see": Text("vim /etc/") + Key("tab:2"),

            # common bash scripting
             "for i in": Text("for i in "),
             "for loop": Text("for i in ; do echo $i; ; done") + Key("left/5:20"),

            # my vim
             "vim save": Key("escape, colon, w, enter"),
             "vim quit": Key("escape, colon, q, enter"),
             "double dell": Key("d, d"),
             "double yank": Key("y, y"),
        
            },
    )

# shell_command_map = utils.combine_maps({
    # "git commit": Text("git commit -am "),
    # "git commit done": Text("git commit -am done "),
    # "git checkout new": Text("git checkout -b "),
    # "git reset hard head": Text("git reset --hard HEAD "),
    # "(soft|sym) link": Text("ln -s "),
    # "list": Text("ls -l "),
    # "make dear": Text("mkdir "),
    # "ps (a UX|aux)": Text("ps aux "),
    # "kill command": Text("kill "),
    # "pipe": Text(" | "),
    # "CH mod": Text("chmod "),
# }, dict((command, Text(command + " ")) for command in [
    # "echo", 
    # "grep",
    # "ssh",
    # "diff",
    # "cat",
    # "man",
    # "less",
    # "git status",
    # "git branch",
    # "git diff",
    # "git checkout",
    # "git stash",
    # "git stash pop",
    # "git push",
    # "git pull",
#]))


#---------------------------------------------------------------------------
# Load the grammar instance and define how to unload it.

grammar  = Grammar("bash")
grammar.add_rule(bash_rule)
grammar.load()

# Unload function which will be called by natlink at unload time.
def unload():
    global grammar
    if grammar:  grammar.unload()
    grammar = None
