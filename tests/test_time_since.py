#
#    Copyright (c) 2023 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""Render a small skin with the search list extension against an SQLite archive."""

import os
import pathlib
import re
import sys
import time

import configobj
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bin'))
sys.path.insert(0, str(ROOT))

pytest.importorskip('weecfg.extension', reason="needs weewx on the path")

import weewx
import weewx.manager
import weewx.reportengine
import weewx.schemas.wview_extended
import weewx.station
from weecfg.extension import ExtensionInstaller
import weewx_data

import install
import user.time_since
from install import TimeSinceInstaller

HOUR = 3600
SKIN_CONF = """
[CheetahGenerator]
    search_list_extensions = user.time_since.TimeSince
    encoding = utf8
    [[ToDate]]
        [[[index]]]
            template = index.html.tmpl
[Units]
    [[TimeFormats]]
        current = %Y-%m-%d %H:%M
[Generators]
    generator_list = weewx.cheetahgenerator.CheetahGenerator
"""
TEMPLATE = """\
since=$time_since('rain>0').long_form
at=$time_at('rain>0')
never=$time_since('rain>1000')
never_at=$time_at('rain>1000')
other=$time_at('rain>0', 'alt_binding')
"""


def local(day, hour=0):
    """Timestamp of a local time in January 2026.

    Args:
        day (int): Day of the month.
        hour (int): Hour of the day.

    Returns:
        int: The timestamp.
    """
    return int(time.mktime((2026, 1, day, hour, 0, 0, 0, 0, -1)))


@pytest.fixture(autouse=True)
def local_timezone():
    old = os.environ.get('TZ')
    os.environ['TZ'] = 'Europe/Berlin'
    time.tzset()
    yield
    if old is None:
        del os.environ['TZ']
    else:
        os.environ['TZ'] = old
    time.tzset()


@pytest.fixture
def station(tmp_path):
    """A station directory with an archive and a one-template skin.

    Rain fell at 2 Jan 06:00 and 3 Jan 12:00, it is dry from then on. A second
    archive, bound as 'alt_binding', has rain on 4 Jan 18:00 only.

    Returns:
        configobj.ConfigObj: The configuration, with WEEWX_ROOT in tmp_path.
    """
    conf_path = pathlib.Path(weewx_data.__file__).parent / 'weewx.conf'
    config_dict = configobj.ConfigObj(str(conf_path), encoding='utf-8')
    config_dict['WEEWX_ROOT'] = str(tmp_path)
    config_dict['Station']['station_type'] = 'Simulator'
    config_dict['StdReport'] = {
        'SKIN_ROOT': 'skins',
        'HTML_ROOT': 'public_html',
        'Defaults': config_dict['StdReport']['Defaults'],
        'TimeSinceTest': {'skin': 'TimeSinceTest'},
    }
    skin = tmp_path / 'skins' / 'TimeSinceTest'
    skin.mkdir(parents=True)
    (skin / 'skin.conf').write_text(SKIN_CONF)
    (skin / 'index.html.tmpl').write_text(TEMPLATE)

    db_dict = {'database_name': str(tmp_path / 'archive.sdb'),
               'driver': 'weedb.sqlite', 'SQLITE_ROOT': str(tmp_path)}
    config_dict['DatabaseTypes']['SQLite']['SQLITE_ROOT'] = str(tmp_path)
    config_dict['Databases']['archive_sqlite']['database_name'] = 'archive.sdb'
    with weewx.manager.DaySummaryManager.open_with_create(
            db_dict, schema=weewx.schemas.wview_extended.schema) as manager:
        for stamp in range(local(1) + HOUR, local(5) + HOUR, HOUR):
            rain = 0.1 if stamp in (local(2, 6), local(3, 12)) else 0.0
            manager.addRecord({'dateTime': stamp, 'usUnits': weewx.METRIC,
                               'interval': 60, 'rain': rain})
    config_dict['DataBindings']['alt_binding'] = dict(
        config_dict['DataBindings']['wx_binding'], database='alt_sqlite')
    config_dict['Databases']['alt_sqlite'] = dict(
        config_dict['Databases']['archive_sqlite'], database_name='alt.sdb')
    alt_dict = dict(db_dict, database_name=str(tmp_path / 'alt.sdb'))
    with weewx.manager.DaySummaryManager.open_with_create(
            alt_dict, schema=weewx.schemas.wview_extended.schema) as manager:
        manager.addRecord({'dateTime': local(4, 18), 'usUnits': weewx.METRIC,
                           'interval': 60, 'rain': 0.1})
    return config_dict


def numbers(text):
    """The numbers in a text, so that the labels of the unit system do not matter.

    Args:
        text (str): A text such as '1 day, 12 hours, 0 minutes'.

    Returns:
        list[int]: The numbers in the text, here [1, 12, 0].
    """
    return [int(x) for x in re.findall(r'\d+', text)]


def render(config_dict, gen_ts):
    """Run the report engine for the test skin.

    Returns:
        dict: The lines of the rendered page, name -> value.
    """
    stn_info = weewx.station.StationInfo(**config_dict['Station'])
    engine = weewx.reportengine.StdReportEngine(config_dict, stn_info, gen_ts=gen_ts)
    engine.run()
    out = pathlib.Path(config_dict['WEEWX_ROOT']) / 'public_html' / 'index.html'
    return dict(line.split('=', 1) for line in out.read_text().splitlines())


def test_time_since_counts_from_the_last_matching_record(station):
    page = render(station, local(5))

    # Last rain 3 Jan 12:00, report time 5 Jan 00:00.
    assert numbers(page['since']) == [1, 12, 0]


def test_time_at_gives_the_time_of_the_last_matching_record(station):
    page = render(station, local(5))

    assert page['at'] == '2026-01-03 12:00'


def test_the_report_time_bounds_the_search(station):
    page = render(station, local(3))

    # Report time 3 Jan 00:00. Only the rain on 2 Jan 06:00 is before it.
    assert numbers(page['since']) == [0, 18, 0]


def test_second_argument_selects_another_data_binding(station):
    page = render(station, local(5))

    assert page['other'] == '2026-01-04 18:00'


def test_no_match_gives_the_none_string(station):
    page = render(station, local(5))

    assert page['never'].strip() == page['never_at'].strip() == 'N/A'


def test_installer_copies_the_module():
    installer = TimeSinceInstaller()

    assert isinstance(installer, ExtensionInstaller)
    assert installer['name'] == 'time_since'
    assert installer['files'] == [('bin/user', ['bin/user/time_since.py'])]


def test_module_and_installer_agree_on_the_version():
    assert user.time_since.VERSION == install.VERSION == TimeSinceInstaller()['version']
