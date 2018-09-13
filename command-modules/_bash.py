#
# This file is part of Dragonfly.
# (c) Copyright 2008 by Christo Butcher
# Licensed under the LGPL.
#
#   <http://www.gnu.org/licenses/>.
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

#---------------------------------------------------------------------------
# Set up this module's configuration.

config = Config("bash")
config.load()


#---------------------------------------------------------------------------
# Defined this module's main rule.

bash_rule = MappingRule(
    name="bash",
    mapping={
    
            # terminal  
             "[keyboard] break": Key("c-c"),
             "new terminal": Key("ca-t"),
             
            # Ubuntu
             "pseudo": Text("sudo "),
             "apt get install": Text("apt-get install"),
             "apt get update": Text("apt-get update"),
             "apt get upgrade": Text("apt-get upgrade"),
             "apt [cash] search": Text("apt-cache search"),
             "pseudo I": Text("sudo -i"),
             
            # git
             "git reset hard": Text("#git reset --hard HEAD # deletes everything after last commit"),
             "git reset soft": Text("#git reset --soft HEAD^ # moves head to parent HEAD~1 HEAD@{1}"),
             "git status": Text("git status") + Key("enter"),
             "git [log] follow": Text("git log --follow "),
             "git log": Text("git log ") + Key("enter"),
             
                          
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

bash_grammar  = Grammar("bash")
bash_grammar.add_rule(bash_rule)
bash_grammar.load()

# Unload function which will be called by natlink at unload time.
def unload():
    global bash_grammar
    if bash_grammar:  bash_grammar.unload()
    bash_grammar = None
