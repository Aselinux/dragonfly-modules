#
# This file is a command-module for Dragonfly.
# (c) Copyright 2018 by AseLinux
# Modified original dragonfly's _dragonfly_tools.py
# (c) Copyright 2008 by Christo Butcher
# Licensed under the LGPL, see <http://www.gnu.org/licenses/>
#

"""
Command-module for managing **Dragonfly**
============================================================================

This module manages the configuration files used by other 
active Dragonfly command-modules.  It implements a command 
for easy opening and editing of the configuration files. 
It also monitors the files for modifications, and causes 
the associated command-module to be reloaded if necessary.


Installation
----------------------------------------------------------------------------

If you are using DNS and Natlink, simply place this file in you Natlink 
macros directory.  It will then be automatically loaded by Natlink when 
you next toggle your microphone or restart Natlink.


Commands
----------------------------------------------------------------------------

The following voice commands are available:

Command: **"list configs"**
    Lists the currently available configuration files.
    The output is visible in the *Messages from Python Macros*
    window.

Command: **"list modules"**
    Lists the currently available modules.
    The output is visible in the *Messages from Python Macros*
    window.
    
Command: **"edit <config> (config | configuration)"**
    Opens the given configuration file in the default ``*.txt``
    editor.  The *<config>* element should be one of the
    configuration names given by the **"list configs"**
    command.

Command: **"edit <module> (module|mod)"**
    Opens the given module file in "notepad+"
    editor.  The *<module>* element should be one of the
    module/configuration names given by the **"list modules"** or **"list configs"**
    command.

Command: **"show dragonfly version"**
    Displays the version of the currently active Dragonfly library.

Command: **"update dragonfly version"**
    Updates the Dragonfly library to the newest version available online.

Command: **"reload natlink"**
    Reloads Natlink.

"""

try:
    import pkg_resources
    pkg_resources.require("dragonfly >= 0.6.5beta1.dev-r81")
except ImportError:
    pass

import os
from dragonfly import (Grammar, CompoundRule, DictList, DictListRef,
                       MappingRule, Mimic, Key, FocusWindow,
                       Window, Config, Section, Item, Function)

from lib import sound
from natlink import setMicState
import time
import subprocess

#---------------------------------------------------------------------------
# Set up this module's configuration.

config                   = Config("config manager")
#config                   = Config("dragonfly tools") # I like to keep those names consistent with the .py module file names
config.lang              = Section("Language section")

config.lang.list_configs = Item("list configs", doc="Command to ...")
config.lang.edit_config  = Item("edit <config> (config | configuration)", doc="Command to ...")

config.lang.list_modules = Item("list modules", doc="Command to ...")
config.lang.edit_module  = Item("edit <module> (module|mod)", doc="Command to ...")

config.lang.show_dragonfly_version = Item("show dragonfly version", doc="Command to ...")
config.lang.update_dragonfly = Item("update dragonfly version", doc="Command to ...")
config.lang.reload_natlink   = Item("reload natlink", doc="Command to ...")


config.lang.show_natlink_messages_window = Item("show (natlink|messages) [window]", doc="Command to ...")
config.lang.kick_dragon = Item("kick Dragon", doc="Command to ...")
                                
config.load()


#---------------------------------------------------------------------------

config_map = DictList("config_map")


#---------------------------------------------------------------------------

def show_natlink_messages_window(duration=3, msg="show_natlink_messages_window"):
        """
        bring the natlink messages window to focus/front to see what is being printed
        """
        sound.play(sound.SND_MESSAGE)
        FocusWindow("natspeak", "Messages from Python Macros").execute()
        print(msg)
        if duration > 0:
            time.sleep(duration)
            Key("alt:down, tab:down/5, alt:up").execute()

def kick_dragon():
    """
    sending dragon to sleep and up again to reload macros
    """
    
    Key("c-s").execute()
    show_natlink_messages_window(duration=2, msg="** saved notepad, reloading by mic sleeping then on **")
    setMicState("sleeping")
    setMicState("on")
    
#---------------------------------------------------------------------------
    
class ConfigManagerGrammar(Grammar):

    def __init__(self):
        Grammar.__init__(self, name="config manager", context=None)

    def _process_begin(self, executable, title, handle):
        configs = Config.get_instances()

        # Check for modified config files, and if found cause reload.
        new_config_map = {}
        for c in configs:
            new_config_map[c.name] = c
            if not os.path.isfile(c.config_path):
                continue
            #print c.config_path
            #print c.module_path
            config_time = os.path.getmtime(c.config_path)
            module_time = os.path.getmtime(c.module_path)
            if config_time >= module_time:
                print "reloading config",c.name
                os.utime(c.module_path, None) # set the access and modified times to the current time

        # Refresh the mapping of config names -> config files.
        config_map.set(new_config_map)

grammar = ConfigManagerGrammar()


#---------------------------------------------------------------------------

class ListConfigsRule(CompoundRule):

    spec = config.lang.list_configs

    def _process_recognition(self, node, extras):
        print "Active configuration files i.e. _name.txt:"
        configs = config_map.keys()
        configs.sort()
        for config in configs:
            print "  - %s" % config

grammar.add_rule(ListConfigsRule())

#---------------------------------------------------------------------------

class ListModulesRule(CompoundRule):

    spec = config.lang.list_modules

    def _process_recognition(self, node, extras):
        print "Active dragonfly modules i.e. _name.py:"
        configs = config_map.keys()
        configs.sort()
        
        print( "{:>20} {:>20} {:>20}".format("module name", "module file", "config file") )
        print( "{:>20} {:>20} {:>20}".format("-"*20, "-"*20, "-"*20) )
        
        for config in configs:
            #print "  - %s: %s" % ( config, str(config_map[config].module_path.split("\\")[-1]) )
            print( "{:>20} {:>20} {:>20}".format( config, str(config_map[config].module_path.split("\\")[-1]), str(config_map[config].config_path.split("\\")[-1]) ) )

grammar.add_rule(ListModulesRule())


#---------------------------------------------------------------------------

class EditConfigRule(CompoundRule):

    spec = config.lang.edit_config
    extras = [DictListRef("config", config_map)]

    def _process_recognition(self, node, extras):
        config_instance = extras["config"]
        path = config_instance.config_path
        if not os.path.isfile(path):
            try:
                config_instance.generate_config_file(path)
            except Exception, e:
                self._log.warning("Failed to create new config file %r: %s" % (path, e))
                return
        #os.startfile(path) # this seems to open the config file in notepad++, but it crashes Dragon 15 altogether on Windows 7 and Windows 10 both 64-bit and the rest of the stack of dragonfly NatLink python and pywin32 are all 32-bit
        #print(path)
        subprocess.Popen([r"C:\Program Files\Notepad++\notepad++.exe", path])

grammar.add_rule(EditConfigRule())


#---------------------------------------------------------------------------

class EditModuleRule(CompoundRule):

    spec = config.lang.edit_module
    extras = [DictListRef("module", config_map)]

    def _process_recognition(self, node, extras):
        module_instance = extras["module"]
        path = module_instance.module_path
        if not os.path.isfile(path):
            print("I can't find the module file you want to edit!!")

        subprocess.Popen([r"C:\Program Files\Notepad++\notepad++.exe", path])

grammar.add_rule(EditModuleRule())


#---------------------------------------------------------------------------

class ShowVersionRule(CompoundRule):

    spec = config.lang.show_dragonfly_version

    def _process_recognition(self, node, extras):
        dragonfly_dist = pkg_resources.get_distribution("dragonfly")
        print "Current Dragonfly version:", dragonfly_dist.version
        import dragonfly.engines
        engine = dragonfly.get_engine()
        print "Current language: %r" % engine.language
        
        show_natlink_messages_window(duration=3, msg="")

grammar.add_rule(ShowVersionRule())


#---------------------------------------------------------------------------

class UpdateDragonflyRule(CompoundRule):

    spec = config.lang.update_dragonfly

    def _process_recognition(self, node, extras):
        from pkg_resources import load_entry_point
        import sys
        class Stream(object):
            stream = sys.stdout
            def write(self, data): self.stream.write(data)
            def flush(self): pass
        sys.argv = [""]; sys.stdout = Stream()
#        load_entry_point('setuptools', 'console_scripts', 'easy_install')(["--verbose", "--upgrade", "dragonfly"])
#        load_entry_point('setuptools', 'console_scripts', 'easy_install')(["--dry-run", "--upgrade", "dragonfly"])

        show_natlink_messages_window(duration=3, msg="update dragonfly version: IS COMMENTED OUT")

grammar.add_rule(UpdateDragonflyRule())


#---------------------------------------------------------------------------

class StaticRule(MappingRule):

    mapping = {
#               config.lang.reload_natlink: FocusWindow("natspeak", "Messages from Python Macros") + Key("a-f, r"),
                config.lang.reload_natlink: Function(show_natlink_messages_window, duration=4, msg="reload natlink: COMMENTED OUT, causing an error, requiring restart of Dragon."),
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

                config.lang.show_natlink_messages_window: Function(show_natlink_messages_window, duration=0),
                config.lang.kick_dragon: Function(kick_dragon),
              }

grammar.add_rule(StaticRule())


#---------------------------------------------------------------------------
# Load this module's grammar.

grammar.load()
def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None
