import argparse
import json
import logging
import logging.config
import re

import wolframalpha
from snipslistener import SnipsListener, intent

LOG = logging.getLogger(__name__)
ANSWER_REGEX = re.compile(r'^([\d\.eE+-]+)\s+\w+\s+\((\w+)\)$')


class WolframAlphaListener(SnipsListener):

    def __init__(self, app_id, mqtt_host, mqtt_port=1883):
        super().__init__(mqtt_host, mqtt_port)
        self.wa_client = wolframalpha.Client(app_id)

    @intent('ConvertUnits')
    def convert_units(self, data):
        if all(slot in data.slots for slot in ('quantity', 'from_unit', 'to_unit')):
            query = "convert {} {} to {}".format(
                data.slots['quantity'].value, data.slots['from_unit'].value, data.slots['to_unit'].value
            )
            reply = "{} {} is ".format(data.slots['quantity'].value, data.slots['from_unit'].value)
        else:
            query = data.input
            reply = ''
        res = self.wa_client.query(query)

        if res.success != "true":
            LOG.info("Wolfram Alpha couldn't answer: %s", data.input, extra={'response': res})
            data.session_manager.end_session("Sorry, I couldn't answer that.")
            return
        else:
            LOG.debug("Wolfram Alpha success for %s", data.input, extra={'response': res})

        interpretation = None
        answer = None
        for pod in res.pods:
            if pod.title == "Input interpretation" and pod.numsubpods > 0:
                subpod = next(pod.subpods)
                interpretation = subpod.plaintext
            if pod.primary and pod.numsubpods > 0:
                subpod = next(pod.subpods)
                answer = subpod.plaintext

        if interpretation is not None:
            LOG.debug('Interpretation of "%s": %s', data.input, interpretation)

        if answer is not None:
            LOG.debug('Answer to "%s": %s', data.input, answer)
            match = ANSWER_REGEX.match(answer)
            if match:
                # Sometimes answers come in the form "473.2 mL (milliliters)"
                # Reformat that to "473.2 milliliters"
                reply += "{} {}".format(match.group(1), match.group(2))
            else:
                reply += answer.replace('\n', ', ')
            data.session_manager.end_session(reply)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Configuration JSON file", default="config.json")
    args = parser.parse_args()
    with open(args.config, 'r') as infile:
        config = json.load(infile)
        listener_args = {
            "mqtt_host": config["mqtt_host"],
            "app_id": config["app_id"],
        }
        if 'mqtt_port' in config:
            listener_args['mqtt_port'] = int(config['mqtt_port'])
        if 'logging_config' in config:
            logging.config.dictConfig(config['logging_config'])
        else:
            logging.basicConfig(level=logging.INFO)
        listener = WolframAlphaListener(**listener_args)
        listener.loop_forever()
