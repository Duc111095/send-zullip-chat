import os

import zulip
import markdown

client = zulip.Client(config_file=os.path.dirname(__file__)+"/zuliprc")


def send_msg(msg: str, to: int) -> any:
    request = {
        "type": "stream",
        "to": to,
        "topic": "channel events",
        "content": markdown.markdown(msg).replace("<p>", "").replace("</p>", "").replace("<pre><code>", "").replace(
            "</code></pre>", ""),
    }
    result = client.send_message(request)
    return result
