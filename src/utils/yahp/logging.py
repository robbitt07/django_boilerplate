import logging
import os
import sys


class PackagePathFilter(logging.Filter):
    def filter(self, record):
        pathname = record.pathname
        record.relativepath = None
        abs_sys_paths = map(os.path.abspath, sys.path)
        for path in sorted(abs_sys_paths, key=len, reverse=True):  # longer paths first
            if not path.endswith(os.sep):
                path += os.sep
            if pathname.startswith(path):
                record.relativepath = (
                    os.path.relpath(pathname, path)
                    .replace('/', '.').replace('\\', '.').replace('.py', '')
                )
                break
        return True


class LoggerAdapter(logging.LoggerAdapter):
    def __init__(self, logger, extra_fields: dict):
        super(LoggerAdapter, self).__init__(logger, {})
        self.extra_fields = extra_fields
        self.prefix = ' '.join([f'{key}={value}' for key, value in extra_fields.items()])

    def process(self, msg, kwargs):

        return '[%s] %s' % (self.prefix, msg), kwargs
