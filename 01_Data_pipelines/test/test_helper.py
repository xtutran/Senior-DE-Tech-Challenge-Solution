from module import helper
from datetime import datetime


def test_is_valid_email():
    assert helper.is_valid_email('Allison_Guzman@jackson-frazier.com')
    assert helper.is_valid_email('Allison@jackson-frazier.net')
    assert not helper.is_valid_email('Melissa_Riley@murray.biz')
    assert not helper.is_valid_email('Allison@jackson-frazier..net')
    assert not helper.is_valid_email('Allison@abc')


def test_clean_birthday():
    assert helper.clean_birthday('1986/01/10') == datetime(1986, 1, 10)
    assert helper.clean_birthday('1974-09-10') == datetime(1974, 9, 10)
    assert helper.clean_birthday('02/03/1974') == datetime(1974, 3, 2)
    assert helper.clean_birthday('12/23/1974') == datetime(1974, 12, 23)
    assert helper.clean_birthday('12.23.1974') is None


def test_gen_membership_id():
    assert helper.gen_membership_id(None, '19870101') is None
    assert helper.gen_membership_id('tran', None) is None
    assert helper.gen_membership_id('tran', '19860110') == 'tran_3864b'


def test_clean_mobile_number():
    assert helper.clean_mobile_number('2387 9991') == 23879991
    assert helper.clean_mobile_number('23879991') == 23879991
    assert helper.clean_mobile_number('a2387 9991') is None


def test_is_valid_mobile_number():
    assert helper.is_valid_mobile_number(23879991)
    assert not helper.is_valid_mobile_number(2389991)


def test_split_fullname():
    assert helper.split_fullname("Mr. Scott Martinez") == ["Scott", "Martinez"]
    assert helper.split_fullname("") == [None, None]
    assert helper.split_fullname("Mr. Scott Martinez PhD") == ["Scott", "Martinez"]
    assert helper.split_fullname("Scott Martinez PhD") == ["Scott", "Martinez"]
    assert helper.split_fullname("Mr. Scott") == ["Scott", None]


def test_is_over_18():
    assert not helper.is_over_18(datetime(2018, 1, 1))
    assert helper.is_over_18(datetime(1988, 1, 1))
