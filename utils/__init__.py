#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum
class BaseEnumeration(Enum):
    def __str__(self):
        return str(self.value).lower()
    def __hash__(self):
        return hash(str(self.value).lower())
class LanguagesSupported(BaseEnumeration):
    English = 'en'
    Portuguese = 'pt'
    Spanish = 'es'
    Polish = 'pl'
class PlatformsSupported(BaseEnumeration):
    PC = 'pc'
    PTS = 'pts'
    Xbox = '10'
    PS4 = '9'
    Switch = '22'
def print_exception(exc):
    print(' : '.join([str(_) for _ in [type(exc), exc.args, exc]]))

def replace(_input, _old, _new='', _split='', replace_or_split=False, _index=1):
    if replace_or_split:
        return _input.split(_split)[_index] or _input.replace(_old, _new)
    return _input.replace(_old, _new)

def random(min=0, max=100, *, as_int=True, args=None):
    import random
    if args:
        return random.choice(args)#if isinstance(args, list) and len(args) > 0:
    if as_int:
        return random.randint(min, max)
    return random.randrange(min, max)

def random_string(chars=None, size=32):
    from random import choice
    if not chars:
        import string
        chars = string.ascii_letters + string.digits # + string.punctuation
    return ''.join(choice(chars) for _ in range(size))

def load_locate_json(lang, folder='lang'):
    from utils.file import read_file, join_path
    return read_file(join_path(['data', folder, '{}.json'.format(lang)]), is_json=True)

def get_url(url, as_json=True):
    import requests
    for _ in range(5):
        try:
            _request = requests.get(url)
            if as_json:
                from json.decoder import JSONDecodeError
                try:
                    return _request.json()
                except (JSONDecodeError, ValueError):
                    pass
            return _request.text
        except requests.exceptions.ConnectionError:
            import time
            time.sleep(1)
    return None
def get_env(name, default=None, verbose=False):
    import os
    try:
        from dotenv import load_dotenv
    except ImportError:
        pass
        #try:
        #    return os.environ[name] or default
        #except KeyError:
        #    return default
    else:
        #from pathlib import Path  # python3 only
        load_dotenv(verbose=verbose)#,dotenv_path=Path('.') / '.env'
    finally:
        return os.getenv(name) or default

"""
https://stackoverflow.com/questions/715417/converting-from-a-string-to-boolean-in-python

>>> import json
>>> json.loads("false".lower())
False
>>> json.loads("True".lower())
True
"""
