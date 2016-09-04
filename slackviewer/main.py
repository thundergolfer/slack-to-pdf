import os
import webbrowser

import click
import flask

from collections import Counter, OrderedDict # for analytics
import datetime

from slackviewer.app import app
from slackviewer.archive import (   extract_archive,
                                    get_users,
                                    get_channels,
                                    compile_channels )

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pdfkit

if os.name == 'nt': # if we are running on Windows
    print("Current File Path Dir : " + os.path.dirname(__file__))
    path_wkthmltopdf = os.path.join(os.path.dirname(__file__),
                                    'wkhtmltopdf','bin','wkhtmltopdf.exe').encode('utf-8')
    kit_config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
else:
    kit_config = None # Note: 'config' clashes with app.config somehow

plt.style.use('fivethirtyeight') # SET THE STYLING FOR OUT GRAPHS


def envvar(name, default):
    """Create callable environment variable getter

    :param str name: Name of environment variable
    :param default: Default value to return in case it isn't defined
    """
    return lambda: os.environ.get(name, default)


def flag_ennvar(name):
    return os.environ.get(name) == '1'


def plotGraph_fromDict( D , title=None):
    fig = plt.figure()
    if title:
        fig.suptitle(title, fontsize=12)
    plot = fig.add_subplot(111) # fake subplot to access tick_params
    plot.tick_params(axis='both', which='major', labelsize=7)
    plot.tick_params(axis='both', which='minor', labelsize=6)
    plt.gcf().subplots_adjust(bottom=0.16)
    plt.bar(range(len(D)), D.values(), align='center')
    plt.xticks(rotation=90)
    plt.xticks(range(len(D)), list(D.keys()))
    return fig

def plotGraph_fromList( L, title=None ):
    fig = plt.figure()
    if title:
        fig.suptitle(title, fontsize=12)
    plot = fig.add_subplot(111) # fake subplot to access tick_params
    plot.tick_params(axis='both', which='major', labelsize=7)
    plot.tick_params(axis='both', which='minor', labelsize=6)
    plt.bar(range(len(L)), [value for (key,value) in L], align='center')
    plt.xticks(rotation=90)
    plt.xticks(range(len(L)), [key for key, value in L], align='center')
    return fig

def configure_app(app, archive, debug):
    app.debug = debug
    if app.debug:
        print("WARNING: DEBUG MODE IS ENABLED!")
    app.config["PROPAGATE_EXCEPTIONS"] = True

    path = extract_archive(archive)
    user_data = get_users(path)
    channel_data = get_channels(path)
    channels = compile_channels(path, user_data, channel_data)
    # Creat our cover
    create_cover(channels)
    #
    # RUN TEAM ANALYSIS
    top = flask._app_ctx_stack
    top.channels = channels
    print(type(channels))
    usernames = []
    timestamps = []
    channel_popularity = dict()
    user_num_words = dict()
    for ch_id, messages in channels.items():
        channel_popularity[ch_id] = len(messages)
        for message in messages:
            if message.username in user_num_words and not message.username.isupper():
                user_num_words[message.username] += len(message.msg.split())
            elif not message.username.isupper():
                user_num_words[message.username] = len(message.msg.split())
            usernames.append(message.username)
            timestamps.append(datetime.datetime.strptime(message.time, "%Y-%m-%d %H:%M:%S"))

    # Get num messages per user in descending order
    count_users = {k:v for k,v in Counter(usernames).items() if not k.isupper()}
    count_date_of_message = Counter([t.date() for t in timestamps])
    count_hour_of_message = OrderedDict()
    for k,v in Counter([t.hour for t in timestamps]).items():
        count_hour_of_message[str(k+1)+':00'] = v

    # TODO get number of words written by user
    # TODO get ave length of message by user

    pp = PdfPages('report_src/report_graphs.pdf')
    # plot the graphs
    plot1 = plotGraph_fromDict(count_users, "Most Messages")
    plot2 = plotGraph_fromDict(count_date_of_message, "Posts Per Day")
    plot3 = plotGraph_fromDict(count_hour_of_message, "Most Frequent Posting Hours")
    plot4 = plotGraph_fromDict(user_num_words, "Number of words written per user")
    plot5 = plotGraph_fromDict(channel_popularity, "Channel Popularity By Number of Messages")
    pp.savefig(plot1)
    pp.savefig(plot2)
    pp.savefig(plot3)
    pp.savefig(plot4)
    pp.savefig(plot5)
    pp.close()

def create_cover(channel_data):
    channels = [ch_id for ch_id, _ in channel_data.items()]
    directory = 'report_src'
    css = [str(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'report.css'))]
    users = set()
    str_html = "<h2>Slack Chat Report</h2>"
    for ch_id, messages in channel_data.items():
        for message in messages:
            users.add(message.username)
    str_html += '<h3>Participants</h3>'
    for user in [u for u in users if not u.isupper()]:
        str_html += '<h4>{}</h4>'.format(user)
    str_html += '<h3>Channel Names</h3>'
    for channel in channels:
        str_html += '<h4>{}</h4>'.format(channel)
    pdfkit.from_string(str_html, output_path=os.path.join(directory, 'cover.pdf'),
                       css=css, configuration=kit_config)

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

    # Combine all the PDFs
    from PyPDF2 import PdfFileWriter, PdfFileReader

    # Creating a routine that appends files to the output file
    def append_pdf(input,output):
        [output.addPage(input.getPage(page_num)) for page_num in range(input.numPages)]

    # Creating an object where pdf pages are appended to
    output = PdfFileWriter()

    # First append the cover page
    append_pdf(PdfFileReader(open("report_src/cover.pdf", "rb")), output)
    # Then append the graphs for report
    append_pdf(PdfFileReader(open("report_src/report_graphs.pdf","rb")),output)
    for file in os.listdir('report_src'):
        if file.endswith('.pdf') and 'report_graphs' not in file and 'cover.pdf' not in file:
            append_pdf(PdfFileReader(open('report_src/'+file,"rb")),output)
    # Writing all the collected pages to a file
    output.write(open("Your_Report.pdf","wb"))

    app.run(
        host=ip,
        port=port
    )



