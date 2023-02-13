# -*- coding: utf-8 -*-
"""
This helper script will be used to clean and transform the data.
By separating the logic into module will make the program testable / readable
"""
from __future__ import print_function

import re
from datetime import datetime
from hashlib import sha256
from typing import Optional

def clean_mobile_number(mobile: str) -> Optional[int]:
    """
    This function to clean / normalize mobile number
    :param mobile:
    :return mobile number in Integer:
    """
    if mobile is None:
        return None
    try:
        return int(mobile.replace(' ', ''))
    except ValueError:
        return None


def clean_birthday(date_of_birth: str) -> Optional[datetime]:
    """
    This function will be used to cleanup mixed date format and return a standard format of YYYY-MM-DD with an assumption:
     + input string will only contain / or -
     + day first will always be prioritized: for example, 02/03/1974 will be parsed to 1974-03-02, but not 1974-02-03
    @:param date_of_birth: a date string input
    @:return datetime
    """
    possible_fmt = ['%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y']
    for fmt in possible_fmt:
        try:
            return datetime.strptime(date_of_birth, fmt)
        except ValueError as e:
            continue
    return None


def split_fullname(name: str) -> Optional[list]:
    """
    This function will be used to extract first name and last name
    :param name: fullname of applicant
    :return: a list of [first_name, last_name]
    """
    if name is None or len(name) == 0:
        return [None, None]
    tokens = name.split()
    prefixes = ['Mr.', 'Dr.', 'Mrs.', 'Ms.', 'Miss']
    suffixes = ['MD', 'DDS', 'DVM', 'PhD', 'Jr.', 'III', 'II', 'I']

    if tokens[0] in prefixes:
        tokens = tokens[1:]

    if tokens[-1] in suffixes:
        tokens = tokens[:-1]

    if len(tokens) == 1:
        return tokens + [None]
    else:
        return [tokens[0], ' '.join(tokens[1:])]


def gen_membership_id(last_name: str, date_of_birth: str) -> Optional[str]:
    """
    Membership IDs for successful applications should be the user's last name, followed by a SHA256 hash of the
    applicant's birthday, truncated to first 5 digits of hash (i.e <last_name>_<hash(YYYYMMDD)>)
    :param last_name:
    :param date_of_birth:
    :return:
    """
    if last_name is None or date_of_birth is None:
        return None
    else:
        uuid = sha256(date_of_birth.encode('utf-8')).hexdigest()
        return f'{last_name}_{uuid[:5]}'


def is_valid_email(email: str) -> bool:
    """
    This function will be used to validate an email address. An accepted email must ends with @emailprovider.com or @emailprovider.net
    :param email:
    :return True or False:
    """
    return re.match(pattern=r'^[\w_\.]+@([\w-]+\.)+[com|net]', string=email) is not None


def is_valid_mobile_number(mobile: int) -> bool:
    """
    Check if mobile number is valid. A valid number must have 8 digits
    :param mobile:
    :return True or False:
    """
    return len(str(mobile)) == 8


def is_over_18(date_of_birth: datetime) -> bool:
    """
    Check if applicant is over 18 years old as of 1 Jan 2022

    :param date_of_birth: datetime
    :return True or False:
    """
    age = 2022 - date_of_birth.year - ((1, 1) < (date_of_birth.month, date_of_birth.day))
    return age > 18
