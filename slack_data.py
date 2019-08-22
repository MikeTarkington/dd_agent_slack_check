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

    @staticmethod
    def permalink_call(token, channel, message_ts):
        url = 'https://slack.com/api/chat.getPermalink'
        data = [
            ('token', token),
            ('channel', channel),
            ('message_ts', message_ts)
        ]
        r = requests.get(url, data)
        link = json.loads(r.text)
        return link['permalink']

    @staticmethod
    def event_permalinks(permalinks):
        links = []
        for link in permalinks:
            links.append(str(link))
        return links

    def check(self, instance):
        token = instance['slack_app_token']
        channel_id = instance['channel_id']
        dd_api_key = instance['dd_api_key']

        url = 'https://slack.com/api/conversations.history'
        data = [
            ('token', token),
            ('channel', channel_id),
            ('oldest', time.time() - 86400)
        ]
        r = requests.get(url, data)
        chan_history = json.loads(r.text)

        unanswered = []
        response_times = []
        avg_response_time_24hr = None
        for message in chan_history["messages"]:
            if "reply_count" not in message.keys() and "subtype" not in message.keys():
                unanswered.append(self.permalink_call(
                    token, channel_id, message["ts"]))
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
                        # previously collected response times seem to slightly change in some cases
                        # noticed the slight differences to timestamps in API repeat responses
                        # but there shouldn't be a difference from one response to the next
                        # on that same check instance run
                        break
                if self_answer == message["reply_count"]:
                    unanswered.append(self.permalink_call(
                        token, channel_id, message["ts"]))
        if response_times:
            avg_response_time_24hr = sum(response_times) / len(response_times)

        channel_name = 'channel:{}'.format(instance['channel_name'])

        self.gauge('slack.data.unanswered', len(
            unanswered), tags=[channel_name])
        self.gauge('slack.data.24hr_avg_response_time',
                   avg_response_time_24hr, tags=[channel_name])

        if len(unanswered) > 0:
            event_dict = {
                "timestamp": time.time(),
                "event_type": "Unanswerd Slack messages from {}".format(channel_name),
                "api_key": dd_api_key,
                "msg_title": "Unanswerd Slack messages from {}".format(channel_name),
                "msg_text": str(self.event_permalinks(reversed(unanswered))).strip('[]'),
                "tags": ["slack_data", channel_name]
            }

            self.event(event_dict)
