from enum import Enum

LogLevel = Enum("LogLevel", [
    'INFO',
    'TRACE',
    'DEBUG',
    'WARN',
    'ERROR'
])


class CounterData:

    def __init__(self):
        self.counter_dictionary = {
            log_level.name: {} for log_level in LogLevel
        }

    def reset(self):
        self.counter_dictionary = {
            log_level.name: {} for log_level in LogLevel
        }

    def add_message(self, log_level: str, message: str, count=1) -> None:
        if message not in self.counter_dictionary[log_level]:
            self.counter_dictionary[log_level][message] = 0
        self.counter_dictionary[log_level][message] += count

    def add_counted_messages(self, messages: 'CounterData') -> None:
        for log_level, message_dict in messages.counter_dictionary.items():
            for message, count in message_dict.items():
                self.add_message(log_level, message, count)
