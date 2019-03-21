from django.conf import settings
from django.utils.log import AdminEmailHandler
from django.views.debug import ExceptionReporter

from copy import copy
import json
import requests

from ontask.settings import TEAMS_WEBHOOK


class TeamsExceptionHandler(AdminEmailHandler):
    def emit(self, record):
        try:
            request = record.request
            subject = "%s (%s IP): %s" % (
                record.levelname,
                (
                    "internal"
                    if request.META.get("REMOTE_ADDR") in settings.INTERNAL_IPS
                    else "EXTERNAL"
                ),
                record.getMessage(),
            )
        except Exception:
            subject = "%s: %s" % (record.levelname, record.getMessage())
            request = None
        subject = self.format_subject(subject)

        connector_body = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": subject,
            "sections": [
                {
                    "activityTitle": subject,
                    "facts": [
                        {"name": "Level", "value": record.levelname},
                        {
                            "name": "Method",
                            "value": request.method if request else "No Request",
                        },
                        {
                            "name": "Path",
                            "value": request.path if request else "No Request",
                        },
                        {
                            "name": "User",
                            "value": (
                                f"{request.user.name} ({request.user.email})"
                                if request.user.is_authenticated
                                else "Anonymous User"
                            )
                            if request
                            else "No Request",
                        },
                        {"name": "Status Code", "value": record.status_code},
                        {
                            "name": "URL Params",
                            "value": json.dumps(request.GET)
                            if request
                            else "No Request",
                        },
                        {
                            "name": "Payload",
                            "value": json.dumps(request.POST)
                            if request
                            else "No Request",
                        },
                    ],
                }
            ],
        }

        requests.post(TEAMS_WEBHOOK, json=connector_body)