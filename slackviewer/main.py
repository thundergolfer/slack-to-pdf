import os
import webbrowser

import click
import flask

from collections import Counter # for analytics
import datetime

from slackviewer.app import app
from slackviewer.archive import (   extract_archive,
                                    get_users,
                                    get_channels,
                                    compile_channels )


def envvar(name, default):
    """Create callable environment variable getter

    :param str name: Name of environment variable
    :param default: Default value to return in case it isn't defined
    """
    return lambda: os.environ.get(name, default)


def flag_ennvar(name):
    return os.environ.get(name) == '1'


def configure_app(app, archive, debug):
    app.debug = debug
    if app.debug:
        print("WARNING: DEBUG MODE IS ENABLED!")
    app.config["PROPAGATE_EXCEPTIONS"] = True

    path = extract_archive(archive)
    user_data = get_users(path)
    channel_data = get_channels(path)
    channels = compile_channels(path, user_data, channel_data)

    # RUN TEAM ANALYSIS
    top = flask._app_ctx_stack
    top.channels = channels
    print(type(channels))
    usernames = []
    timestamps = []
    for ch_id, messages in channels.items():
        for message in messages:
            usernames.append(message.username)
            timestamps.append(datetime.datetime.strptime(message.time, "%Y-%m-%d %H:%M:%S"))

    # Get num messages per user in descending order
    count_users = Counter(usernames).most_common()
    count_date_of_message = Counter([t.date() for t in timestamps]).most_common()
    count_hour_of_message = Counter([t.hour for t in timestamps]).most_common()
    # TODO get most active channel
    # TODO get num of messages per user in bar graph
    # TODO get number of words written by user
    # TODO get ave length of message by user



@click.command()
@click.option('-p', '--port', default=envvar('SEV_PORT', '5000'),
              type=click.INT, help="Host port to serve your content on")
@click.option("-z", "--archive", type=click.Path(), required=True,
              default=envvar('SEV_ARCHIVE', ''),
              help="Path to your Slack export archive (.zip file)")
@click.option('-I', '--ip', default=envvar('SEV_IP', 'localhost'),
              type=click.STRING, help="Host IP to serve your content on")
@click.option('--no-browser', is_flag=True,
              default=flag_ennvar("SEV_NO_BROWSER"),
              help="If you do not want a browser to open "
                   "automatically, set this.")
@click.option('--debug', is_flag=True, default=flag_ennvar("FLASK_DEBUG"))
def main(port, archive, ip, no_browser=False, debug=False):
    if not archive:
        raise ValueError("Empty path provided for archive")

    configure_app(app, archive, debug)

    if not no_browser:
        webbrowser.open("http://{}:{}".format(ip, port))

    app.run(
        host=ip,
        port=port
    )
