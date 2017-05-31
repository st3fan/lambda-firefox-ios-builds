#!/usr/bin/env python3


import re

import requests
from flask import Flask, render_template, redirect, url_for, Markup


app = Flask(__name__)
app.config.from_pyfile('app.cfg', silent=True)


def bug_links(summary):
    summary = re.sub(r"(Bug (\d+))", r'Bug <a href="https://bugzilla.mozilla.org/show_bug.cgi?id=\2">\2</a>', summary)
    summary = re.sub(r"\(#(\d+)\)", r'(<a href="https://github.com/mozilla-mobile/firefox-ios/pull/\1">#\1</a>)', summary)
    return summary

def bb_builds(api_key, app_id, branch, scheme, limit=5):
    url = "https://api.buddybuild.com/v1/apps/%s/builds" % app_id
    r = requests.get(url, params={"branch": branch, "scheme": scheme, "limit": limit}, headers={"Authorization": "Bearer " + api_key})
    r.raise_for_status()
    builds = r.json()
    # Add a one line summary to the commit_info
    for build in builds:
        build["commit_info"]["summary"] = bug_links(build["commit_info"]["message"].split("\n")[0])
    return builds

@app.route("/builds/<branch>/<scheme>")
def builds(branch, scheme, event=None, context=None):
    builds = bb_builds(app.config["BUDDYBUILD_ACCESS_TOKEN"], app.config["FIREFOX_APP_ID"], branch, scheme, limit=50)
    return render_template('builds.html', builds=builds, branch=branch,scheme=scheme)

@app.route("/")
def index(event=None, context=None):
    return redirect(url_for('builds', branch="master", scheme="Fennec_Enterprise"))


if __name__ == "__main__":
    app.run(debug=True)

