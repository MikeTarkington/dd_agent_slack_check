# dd_agent_slack_check

A custom agent check that (so far) can report on the number of posts in a Slack channel that haven’t had a reply and average post response times in a channel for the past 24 hours.  It can also produce events to be used as posts back to the originating channel effectively "bumping" the unanswered posts by listing hyperlinks back to those threads.  The main goal being, that we can use it to alert (perhaps checking hourly) if any of the channels have stale/missed posts in them.  

https://cl.ly/19de5cb840c8
![example dashboard](https://cl.ly/19de5cb840c8/Image%2525202019-08-13%252520at%2525207.06.08%252520PM.png)

example of notifications from a metric and event monitor in a slack channel:
https://cl.ly/ce7543c62b99
![example of notifs in channel](https://cl.ly/ce7543c62b99/Image%2525202019-08-13%252520at%2525208.02.13%252520PM.png)

This will help teams learn how effective they are at helping one another over Slack.  It will also be a tool to help people recognize and respond to gaps in the discussions over Slack so that fewer questions/issues go unanswered.

big dreams: I also think it could potentially be a useful customer facing integration if it's polished and fully featured.  Though for that scenario it might be best as a crawler or credential based integration.

# Installation/Usage

1. Create a "Slack App" and obtain your authentication token here: https://api.slack.com/apps
2. Install the Datadog agent: https://docs.datadoghq.com/agent/
3. Pull the `slack_data.yaml` file from this repository and place it in your agents `conf.d` directory. https://docs.datadoghq.com/agent/guide/agent-configuration-files/?tab=agentv6
4. Apply configurations to your yaml file by replacing the placeholders with actual values for channel ID, channel name, Slack token, Datadog API key, and preferred collection interval.
5. Pull the `slack_data.py` file from this repository and place it in your agents `checks.d` directory.
6. Create monitors/dashboards with metrics found under the `slack.data.*` namespace or events tagged with `slack_data` and `channel:your_chan_name`
7. Profit
