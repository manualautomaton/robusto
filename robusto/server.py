from dataclasses import dataclass
from logging import Logger
from typing import Generic
from typing import TypeVar
from actionpack.actions import MakeRequest
from actionpack.actions import RetryPolicy
from flask import Flask

from robusto import LOG_LEVEL
from robusto import LOG_LEVELS


app = Flask(__name__)

@app.route('/<domain>/<tld>')  # <-- some other sevice
def root(domain, tld):
    make_request = MakeRequest('GET', f'http://{domain}.{tld}')
    retry_policy = RetryPolicy(
        action=make_request,
        max_retries=2,
        should_record=True
    )
    result = retry_policy.perform()
    attempts = [
        _result.value.__class__.__name__
        for _result in retry_policy.attempts
    ]
    report = Report[str, list[str]](result.successful, result.value, attempts)
    report.log(app.logger, LOG_LEVELS[LOG_LEVEL].value)
    return str(report)


T = TypeVar('T')
V = TypeVar('V')

@dataclass
class Report(Generic[T, V]):
    success: bool
    value: T
    attempts: list[V]

    def log(self, logger: Logger, level: str):
        collated = self.collate(header = '-' * 30)
        logger.log(level, '\n\t'.join(collated))

    def collate(self, header: str = '') -> list[str]:
        succeded = f'Succeeded --> {self.success}'
        result = f'Result --> {self.value}'
        attempts = f'Attempts --> {self.attempts}'
        report = [header, succeded, result, attempts]
        return report

    def __str__(self) -> str:
        paragraph = lambda _: f'<p>{_}</p>'
        _, *collated = self.collate()
        return ''.join([paragraph(_) for _ in collated])
