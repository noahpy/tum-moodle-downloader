import json
import os
import shutil
import subprocess

from .globals import CREDENTIALS_PATH

DEFAULT_PASS_ENTRY = 'otp/tum'


def _pass_entry() -> str:
    """Name of the `pass` entry holding the otpauth:// URI.

    Can be overridden via the "otp_pass_entry" key in credentials.json.
    """
    if os.path.isfile(CREDENTIALS_PATH):
        with open(CREDENTIALS_PATH, 'r') as f:
            entry = json.load(f).get('otp_pass_entry')
            if entry:
                return entry
    return DEFAULT_PASS_ENTRY


def _otpauth_uri_from_pass(entry: str) -> str or None:
    if not shutil.which('pass'):
        return None
    try:
        out = subprocess.run(['pass', 'show', entry], capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith('otpauth://'):
            return line
    return None


def get_otp() -> str:
    """Return a current TOTP code, computed from `pass` if possible, otherwise prompted."""
    uri = _otpauth_uri_from_pass(_pass_entry())
    if uri:
        try:
            import pyotp
            return pyotp.parse_uri(uri).now()
        except ImportError:
            print('pyotp not installed; cannot compute OTP automatically.')
    return input('Enter TOTP code: ').strip()
