import flask
import os
from PyPDF2 import PdfFileMerger
import pdfkit
import shutil

if os.name == 'nt': # if we are running on Windows
    print("Current File Path Dir : " + os.path.dirname(__file__))
    path_wkthmltopdf = os.path.join(os.path.dirname(__file__),
                                    'wkhtmltopdf','bin','wkhtmltopdf.exe').encode('utf-8')
    kit_config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
else:
    kit_config = None # Note: 'config' clashes with app.config somehow
# TODO: find solution for Linux and OSX

app = flask.Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)


@app.route("/channel/<name>")
def channel_name(name):
    messages = flask._app_ctx_stack.channels[name]
    channels = flask._app_ctx_stack.channels.keys()
    return flask.render_template("viewer.html", messages=messages,
                                 name=name.format(name=name),
                                 channels=sorted(channels))


@app.route("/")
def index():
    channels = flask._app_ctx_stack.channels.keys()
    if "general" in channels:
        print('Creating Report....')
        create_report(channels)
        return channel_name("general")
    else:
        print('Creating Report....')
        create_report(channels)
        return channel_name(channels[0])


def create_report(channels):

    directory = 'report_src'
    if not os.path.exists(directory):
        os.makedirs(directory)
    css_dir = 'report_src/static'
    if not os.path.exists(css_dir):
        os.makedirs(css_dir)
    # write css file
    css_fn = os.path.join(os.path.dirname(__file__), 'static', 'viewer.css')
    shutil.copy2(css_fn, css_dir)
    for ch in channels:
        # Write HTML
        with open(os.path.join(directory,ch+'.html'), 'w', encoding='utf-8') as output:
            print('writing ' + ch)
            str_html = channel_name(ch)
            output.write(str_html)
            # Create PDF
            # the HTML's internal CSS link is failing, so we can replace it.
            # we user a different css (report.css) to hide the unnessecary sidebar
            css = [str(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'static',
                                    'report.css'))]
            print(css)
            pdfkit.from_string(str_html,
                               output_path=os.path.join(directory, ch + '.pdf'),
                               css=css,
                               configuration=kit_config)


def merge_pdfs(directory):
    """
    Combine the analytics and channel pdfs into one report pdf
    """

    # get all filenames of pdfs in directory
    pdfs = []
    outfile = PdfFileMerger()

    for f in pdfs:
        outfile.append(open(f, 'rb'))

    outfile.write(open('report.pdf', 'wb')) # done

