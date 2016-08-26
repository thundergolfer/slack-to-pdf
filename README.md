# Slack Export Viewer

A Slack Export archive viewer that allows you to easily view and share a report of your
Slack team's interactions (instead of having to dive into hundreds of JSON files).

![Preview](screenshot.png)


## Overview

`slack-to-pdf` is best used to report the team interactions on Slack for a University/College assignment. Some group project assignments require you do log and present your communications to assess member contribution.

`slack-to-pdf` can be used locally on one machine for yourself to explore an export or it can be run on a headless server (as it is a Flask web app) if you also want to serve the content to the rest of your team.


## Usage

### 1) Grab your Slack team's export

* Visit [https://my.slack.com/services/export](https://my.slack.com/services/export)
* Create an export
* Wait for it to complete
* Refresh the page and download the export (.zip file) into whatever directory

### 2) Point `slack-export-viewer` to it

Point slack-export-viewer to the .zip file and let it do its magic

```bash
slack-to-pdf -z /path/to/export/zip
```

If everything went well, your archive will have been extracted, processed, and browser window will have opened showing your *#general* channel from the export.


## Installation

```bash
pip install slack-export-viewer
```

`slack-export-viewer` will be installed as an entry-point; run from anywhere.

```bash
$ slack-export-viewer --help
Usage: slack-export-viewer [OPTIONS]

Options:
  -p, --port INTEGER  Host port to serve your content on
  -z, --archive PATH  Path to your Slack export archive (.zip file)
                      [required]
  -I, --ip TEXT       Host IP to serve your content on
  --no-browser        If you do not want a browser to open automatically, set
                      this.
  --debug
  --help              Show this message and exit.
```


## Acknowledgements

* Credit to Pieter Levels for his original [blog post](https://levels.io/slack-export-to-html/) on a Slack-to-html solution.

* Credit to [Hamza Faran](https://github.com/hfaran) for his work on a Slack-to-HTML solution in python.

### License

[![CC0](http://i.creativecommons.org/p/zero/1.0/88x31.png)](http://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, [Thundergolfer](http://www.jonathonbelotti.com) has waived all copyright and related or neighboring rights to this work.
