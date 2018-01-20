from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import json

import flask

from git_code_debt.server import logic
from git_code_debt.server.presentation.commit_delta import CommitDelta
from git_code_debt.server.presentation.delta import Delta
from git_code_debt.server.render_mako import render_template


changes = flask.Blueprint('changes', __name__)


@changes.route('/changes/<metric_name>/<start_timestamp>/<end_timestamp>')
def show(metric_name, start_timestamp, end_timestamp):
    start_timestamp = int(start_timestamp)
    end_timestamp = int(end_timestamp)

    metric_changes = sorted(logic.get_major_changes_for_metric(
        flask.g.db, start_timestamp, end_timestamp, metric_name,
    ))
    metric_changes = [
        (
            datetime.datetime.fromtimestamp(timestamp).strftime(
                '%Y-%m-%d %H:%M:%S',
            ),
            sha,
            CommitDelta.from_data(
                metric_name, Delta('javascript:;', value),
                color_overrides=flask.g.config.color_overrides,
            ),
        )
        for timestamp, sha, value in metric_changes
    ]

    override_classname = (
        'color-override'
        if metric_name in flask.g.config.color_overrides
        else ''
    )

    rendered_template = render_template(
        'changes.mako',
        changes=metric_changes,
        override_classname=override_classname,
    )

    return json.dumps({'body': rendered_template})
