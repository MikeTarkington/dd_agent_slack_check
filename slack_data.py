# the following try/except block will make the custom check compatible with any Agent version
try:
    # first, try to import the base class from old versions of the Agent...
    from checks import AgentCheck
except ImportError:
    # ...if the above failed, the check is running in Agent version 6 or later
    from datadog_checks.checks import AgentCheck

# content of the special variable __version__ will be shown in the Agent status page
__version__ = "1.0.0"

import requests
import json
import time


class SlackData(AgentCheck):
    def check(self, instance):
        channel_id = instance['channel_id']

        url = 'https://slack.com/api/conversations.history'
        data = [
            ('token', instance['slack_app_token']),
            ('channel', channel_id),
            ('oldest', time.time() - 86400)
        ]
        r = requests.get(url, data)
        chan_history = json.loads(r.text)

        unanswered = 0
        response_times = []
        avg_response_time_24hr = None
        for message in chan_history["messages"]:
            if "reply_count" not in message.keys() and "subtype" not in message.keys():
                unanswered += 1
            elif "reply_count" in message.keys() and "subtype" not in message.keys():
                self_answer = 0
                reply_time = 0
                for reply in reversed(message["replies"]):
                    if reply["user"] == message["user"]:
                        self_answer += 1
                    elif reply["user"] != message["user"]:
                        reply_time = (
                            float(reply["ts"]) - float(message["ts"])) / 60
                        response_times.append(reply_time)
                        # additional replies from users other than original poster might
                        # still be slightly affecting the average despite breaking the loop
                        # after finding the original reply... further analysis needed
                        # previously collected response times seem to slightly change in
                        # some cases might have something to do with the slight
                        # adjustments to timestamps in the API
                        break
                if self_answer == message["reply_count"]:
                    unanswered += 1
        if response_times:
            avg_response_time_24hr = sum(response_times) / len(response_times)

        channel_name = 'channel:{}'.format(instance['channel_name'])

        self.gauge('slack.data.unanswered', unanswered, tags=[channel_name])
        self.gauge('slack.data.24hr_avg_response_time',
                   avg_response_time_24hr, tags=[channel_name])
