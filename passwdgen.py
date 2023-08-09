#!/usr/bin/env python

import os, sys, string, random, argparse, pdb
import rumps, pyperclip3 # type: ignore
import tkinter as tk

menuiconfn='menubaricon.png'
appiconfn='appicon.png'
default_len = 64
max_len = 256
default_specials = string.punctuation
base_alpha = [string.ascii_lowercase, string.ascii_uppercase, string.digits]

def copy_to_clipboard(s: str) -> None:
    pyperclip3.copy(s)

def min_length(use_specials: bool) -> int:
    global base_alpha
    return len(base_alpha) + (1 if use_specials else 0)

def validate_length(l: str, use_specials: bool) -> int:
    length = int(l)
    global max_len
    min_len = min_length(use_specials)
    if not (min_len <= length <= max_len):
        raise ValueError(f'REQUIRE {min_len} <= {length} <= {max_len}')
    return length

def validate_specials(s: str) -> str:
    if not s: # must be a nonempty set
        raise ValueError(f'REQUIRE {s} be nonempty')
    specials = set(s)
    global default_specials
    if not specials.issubset(set(default_specials)):
        raise ValueError(f'REQUIRE {s} be a subset of {default_specials}')
    return ''.join(specials)

#
# no_specials: don't use any specials
# my_specials: override specials explicitly. If empty then it's assumed that
# default specials will be used (unless no_specials is set)
# no_specials and my_specials are mutually exclusive
def generate_passwd(length: int = default_len, no_specials: bool = False,
                    my_specials: str = '', debug: bool = True) -> str:
    if debug:
        print(f"generate_passwd length={length} no_specials={no_specials} "
              f"my_specials='{my_specials}'")
    if no_specials and my_specials:
        raise ValueError(f'no_specials and my_specials are mutually exclusive')
    length = validate_length(str(length), not no_specials)

    global base_alpha, default_specials
    alpha = base_alpha
    if not no_specials:
        specials = default_specials
        if my_specials:
            # guard: should be checked elsewhere
            specials = validate_specials(my_specials)
        alpha = base_alpha + [specials]

    chars = []

    if length < len(alpha):
        sys.exit('Minimum length is {}'.format(len(alpha)))

    take = round(length / len(alpha))
    swing = round(take / 2)
    amts = [take + random.randint(-swing, swing) for a in alpha]
    while (s := sum(amts)) != length:
        if s > length:
            m = max(amts)
            i = amts.index(m)
            amts[i] -= 1
        else:
            m = min(amts)
            i = amts.index(m)
            amts[i] += 1

    assert len(amts) == len(alpha)

    amts_i = iter(amts)

    # O(n) for this section... there are no sorts
    for a in alpha:
        sample_size = next(amts_i)
        assert sample_size >= 1
        if debug:
            print(f'Adding\t{sample_size}\tchars from {a}')
        chars += random.choices(a, k=sample_size)

    if debug:
        print(f'Total\t{length}\tchars')

    # Sort, so O(length^2) or potentially O(length·log(length))
    chars = sorted(chars, key=lambda _: random.random())

    assert(len(chars) == length)
    return ''.join(chars)

class PasswdgenApp(rumps.App):
    def __init__(self):
        global menuiconfn, default_len, default_specials
        super(PasswdgenApp, self).__init__(name='PasswdGen',
                                           icon=menuiconfn,
                                           template=True)
        self.menu = ['Generate password', 'Avoid special characters',
        'Configure password length', 'Configure special characters']
        rumps.debug_mode(True)

        self.length: int = default_len
        self.nospecials: bool = False
        self.override_specials: str = ''

    @rumps.clicked('Generate password')
    def gen_password(self, _) -> None:
        password = generate_passwd(length=self.length,
                                   no_specials=self.nospecials,
                                   my_specials='' if self.nospecials else
                                   self.override_specials)
        copy_to_clipboard(password)
        global appiconfn
        rumps.alert(title='New password generated',
                    message=f'New password\n{password}\n copied to clipboard!',
                    icon_path=appiconfn)

    @rumps.clicked('Avoid special characters')
    def toggle_specials(self, sender) -> None:
        sender.state = not sender.state
        self.nospecials = True if sender.state else False

    @rumps.clicked('Configure password length')
    def chg_length(self, _) -> None:
        global appiconfn, default_len, max_len
        w = rumps.Window(
                title='Configure password length',
                message='Choose length',
                default_text=str(self.length),
                cancel=True,
                dimensions=(64, 32))
        w.icon = appiconfn
        r = w.run()
        assert r.clicked in range(0,2)
        if r.clicked == 1: # OK
            try:
                self.length = validate_length(r.text, not self.nospecials)
            except ValueError as e:
                err = """Invalid length: {}. Must be a number between
{} and {}.""".format(r.text, min_length(not self.nospecials), max_len)
                print(err)
                rumps.alert(title='Invalid length setting',
                            message=err,
                            icon_path=appiconfn)

    @rumps.clicked('Configure special characters')
    def chg_specials(self, _) -> None:
        global appiconfn, default_specials
        w = rumps.Window(
                title='Configure special characters',
                message='Choose which special characters are used',
                default_text=(self.override_specials
                              if self.override_specials
                              else default_specials),
                cancel=True,
                dimensions=(240, 32))
        w.icon = appiconfn
        w.add_button("Use defaults")
        r = w.run()
        assert r.clicked in range(0,3)
        if r.clicked == 1: # OK
            try:
                self.override_specials = validate_specials(r.text)
            except ValueError as e:
                err = """Invalid specified special chars: 
[{}]. Specified string of special characters must be nonempty, and be a
subset of default specials, which are [{}].""".format(r.text, default_specials)
                print(err)
                rumps.alert(title='Invalid special character setting',
                            message=err,
                            icon_path=appiconfn)
        elif r.clicked == 2: # Default specials
            self.override_specials = ''

def app_main():
    global default_len
    length = default_len # default

    app = PasswdgenApp()
    app.run()

def cmdline_main():
    global default_len, max_len, default_specials
    length = default_len # default
    specials = default_specials
    description=f"""Generate a password randomly. Always includes letters and
numbers. Includes special chars by default (drawing from all possible special
chars), but this can be overridden. Length is {length} by default but this can
be overridden. Generated password is automatically saved to clipboard."""
    p = argparse.ArgumentParser(description)
    # Required arguments
    p.add_argument('-l', '--length', action='store',
                   help=(f'Specify length of password. Must be > 0 '
                         f'and < {max_len}'))
    p.add_argument('-S', '--no-special-chars', action='store_true',
                   help='Do not use any special chars.')
    p.add_argument('-s', '--special-chars', action='store',
                   help='Specify what the special chars should be.')
    p.add_argument('-d', '--debug', action='store_true',
                   help='Print debug statements')
    ns = p.parse_args()

    if ns.special_chars and ns.no_special_chars:
        sys.exit('-s and -S are mutually exclusive')

    if ns.length:
        try:
            length = validate_length(ns.length, not ns.no_special_chars)
        except ValueError as e:
            length = default_len
            sys.exit('Length given is invalid. Must be an integer between {} '
                     'and {}. {}'.format(min_length(not ns.no_special_chars),
                                         max_len, e))

    specials = ''
    if not ns.no_special_chars:
        if ns.special_chars:
            try:
                specials = validate_specials(ns.special_chars)
            except ValueError as e:
                sys.exit(f"""Special chars given are invalid.
Characters must be drawn from {default_specials}. {e}""")

    pwd = generate_passwd(length, ns.no_special_chars, specials, ns.debug)

    print(pwd)
    copy_to_clipboard(pwd)
    if ns.debug:
        print('New password saved to clipboard. ⌘-V to paste.')

if __name__ == '__main__':
    if os.path.basename(__file__) == 'passwdgen':
        cmdline_main()
    else:
        app_main()
