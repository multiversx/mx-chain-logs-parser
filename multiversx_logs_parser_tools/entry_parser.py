import json
import re
from typing import Any

log_entry_pattern = re.compile(
    r'^(?P<logger_level>WARN|ERROR|DEBUG|TRACE|INFO)\s*\['      # Log level
    r'(?P<timestamp>[^\]]+)\]\s*'              # Timestamp
    r'\[(?P<logger_name>[^\]]+)\]\s*'          # Logger name
    r'\[(?P<context>[^\]]*)\]\s*'              # context inside brackets
    r'(?P<message>.*)$',                       # The rest of the log message
    re.MULTILINE
)

context_pattern = re.compile(
    r'(?P<shard>\S+)/(?P<epoch>\d+)/(?P<round>\d+)(?:/\((?P<subround>[^\)]+)\))?/?')

separator = '  '


class EntryParser:
    '''
    Parses entries with the format:
        log_level [2025-04-29 07:46:37.102] [logger]  [shard/epoch/round/(subround)] entry_content

    The context [shard/epoch/round/(subround)] can be either fully formed like in '0/4/805/(END_ROUND)' or 'metachain/13/2648/(START_ROUND)'
    or partially formed, like in '/0/0/', 'metachain/2/400/'

    The content of the entry is separated using the predefined separator. If the separator is not present, and a distinction cannot be made
    between the message and parameters, it returns the entire entry content as message

    '''

    def __init__(self, node_name: str):
        self.alerts = []

    def parse_context(self, context: str) -> dict[str, Any]:
        # Parse shard, epoch, round, subround from context
        context_match = context_pattern.match(context)
        if context_match:
            subround = context_match.group('subround')
            return {'shard': context_match.group('shard').strip(), 'epoch': context_match.group('epoch').strip(),
                    'round': context_match.group('round').strip(), 'subround': subround.strip() if subround else ''}
        else:
            return {'shard': '', 'epoch': 0, 'round': 0, 'subround': ''}

    def parse_message(self, message: str):
        if separator in message:
            # if the separator is present, split the content between message and parameters using the separator
            message, parameters = message.split(separator, 1)
            return message.strip(), parameters.strip()

        elif ' = ' in message:
            # if no separator, but the content includes '=', assume first parameter is the word before the '=' and split before that word
            message_parts = message.split(' = ', 1)
            message, first_parameter_label = message_parts[0].rsplit(' ', 1)
            return message.strip(), first_parameter_label.strip() + ' = ' + message_parts[1].strip()

        else:
            # no parameters in the entry or cannot determine if there are parameters present
            return message.strip(), ''

    def parse_log_entry(self, log_content: str) -> dict[str, str]:
        data = {}
        match = log_entry_pattern.search(log_content)
        if match:
            data = match.groupdict()
            context = self.parse_context(data.pop('context'))
            data.update(context)

            message, parameters = self.parse_message(match['message'])
            data['message'] = message
            data['parameters'] = parameters

        return data


if __name__ == "__main__":
    content = 'DEBUG[2025-11-11 17:09:06.028] [..nsus/spos/bls/v1] [metachain/0/3/(BLOCK)] Proposed header received v1              header = {"accumulatedFees": "0","accumulatedFeesInEpoch":"0","chainID":"6c6f63616c2d746573746e6574","devFeesInEpoch":"0","developerFees":"0","epoch":0,"epochStart":{"economics":{"nodePrice":null,"prevEpochStartHash":"","prevEpochStartRound":0,"rewardsForProtocolSustainability":null,"rewardsPerBlock":null,"totalNewlyMinted":null,"totalSupply":null,"totalToDistribute":null},"lastFinalizedHeaders":[]},"leaderSignature":"","miniBlockHeaders":[],"nonce":3,"peerInfo":[],"prevHash":"bbc1249e07d98aabfdb3e735e35142800df013694780497df76778a27db62033","prevRandSeed":"8b6a73f9f4d34f9355cd4399f8c6f14e1296184ea32636ebd58709d62bd35bbe6b992dd3104fa0a64e5fcff9398e0502","pubKeysBitmap":"","randSeed":"41e9c758555f4a33f5de954d6e7cc2d252cacf3ddadfd3fbac1d9ddca2382681e56ab30c65029b29212eb69b13a47906","receiptsHash":"0e5751c026e543b2e8ab2eb06099daa1d1e5df47778f7787faab45cdf12fe3a8","reserved":"","rootHash":"e4a0f900f1ea487a61d3832776d05871e81f7975670a69b1febbf212f4cea5cc","round":3,"shardInfo":[{"accumulatedFees":"0","developerFees":"0","epoch":0,"headerHash":"8da01a5fbda1484d915740b824ebb1de11722ae501e3c8a4e21d9ce96d1a4c1d","lastIncludedMetaNonce":0,"nonce":1,"numPendingMiniBlocks":0,"prevHash":"00fd532ea2e896b86cd70e189c5e716fcfaaac8b7a060e75421d369c19db78e3","prevRandSeed":"f501347f089b236bdd605babb0e27af0b7df76e45628d35072bc87eec4178c0c","pubKeysBitmap":"07","round":1,"shardID":0,"shardMiniBlockHeaders":[],"signature":"","txCount":0},{"accumulatedFees":"0","developerFees":"0","epoch":0,"headerHash":"3897723b58aa6e1949a415a54598e5655363b4a4c967827ef045326f1ca9e216","lastIncludedMetaNonce":0,"nonce":1,"numPendingMiniBlocks":0,"prevHash":"5a62b8bd0aa019e8967dbdc446ab610b98bf59525cc0672e77ea8e74d3e6a3b3","prevRandSeed":"e626f319e5c70a6c3b4e96258a635b8f7e1efb224c285c830cbb4e473b187c1a","pubKeysBitmap":"07","round":1,"shardID":1,"shardMiniBlockHeaders":[],"signature":"","txCount":0}],"signature":"","softwareVersion":"64656661756c74","timeStamp":1762873746,"txCount":0,"validatorStatsRootHash":"d3f82f56f69f4c26a913a8a5721dfdd85cdd70ad4efdfb464c4f1f6ddd4f8dea"} '
    result = EntryParser('').parse_log_entry(content)
    parameter = result.pop('parameters').split(' = ', 1)[1]
    header = json.loads(parameter)
    print(json.dumps(result, indent=4))
    print(json.dumps(header, indent=4))
