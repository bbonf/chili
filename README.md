# Chili
OS X Desktop Multi-tool.

## About
This project was inspired by some great OS X desktop automation/productivity tools that I liked. I was using them extensively but always felt like improving them for my own needs. Using PyObjC I was quickly able to build something that I liked enough to replace them.

## Features
* Launcher window for launching apps and commands
* Keyboard hotkeys
* Window management
* Fuzzy schedulers with snooze.
* Status bar items

## Installation
Run:
```bash
python setup.py py2app -A
```
and copy `dist/Chili.app` to Applications folder.

Currently doesn't automatically start on system startup.

## Configuration
Chili loads its configuration files from `~/.chili/*.py`.

A sample config file is provided at `config.py`. For a more elaborate example, you can view [my personal config](https://github.com/bbonf/dotchili/blob/master/my.py).

Config files are essentialy python code that gets loaded on startup and make use of decorators to define commands and the `chili` modules for interacting with OS X when standard python libraries don't suffice.
 
### decorators
##### command
```python
@command('say')
def say(text):
    os.system('say %s' % text)
```
registers a launcher command that can be used in the launcher window.
##### every
```python
@every(60, 0.5)
def annoy(done, snooze):
    os.system('say about 30 to 90 seconds have passed')
    done()
```
registers a scheduler with interval in seconds and fuzziness.

##### hotkey
```python
import requests

@hotkey('cmd-j')
def chuck_norris():
    joke = requests.get('http://api.icndb.com/jokes/random').json()['value']['joke']

    # don't do this
    os.system('say "%s"' % joke)
```
registers a global hotkey

## Modules
To be documented...

* `chili.keyboard`
* `chili.ui`
* `chili.wm`
* `chili.timer`

## Thanks and Acknowledgmenets
* Steven Degutis for making [Mjolnir](https://github.com/sdegutis/mjolnir)
* abarnet for [pykeycode](https://github.com/abarnert/pykeycode)
* deets for [Minimal PyObjC app](https://github.com/deets/minimal-pyobjc)