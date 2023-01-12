# Copyright 2017 Palantir Technologies, Inc.
import logging
from pyls import hookimpl, uris, _utils

log = logging.getLogger(__name__)


@hookimpl
def pyls_definitions(config, document, position):
    settings = config.plugin_settings('jedi_definition')
    code_position = _utils.position_to_jedi_linecolumn(document, position)
    definitions = document.jedi_script().goto(
        follow_imports=settings.get('follow_imports', True),
        follow_builtin_imports=settings.get('follow_builtin_imports', True),
        **code_position)

    return [
        {
            'uri': format_uri(document, d.module_path),
            'range': {
                'start': {'line': d.line - 1, 'character': d.column},
                'end': {'line': d.line - 1, 'character': d.column + len(d.name)},
            }
        }
        for d in definitions if d.is_definition() and _not_builtin_definition(d)
    ]


def format_uri(document, module_path):
    if module_path is None:
        return document.uri
    else:
        return uris.uri_with(document.uri, path=str(module_path))


def _not_builtin_definition(definition):
    # only supports definition in current document
    return (
        definition.line is not None and
        definition.column is not None and
        definition.module_path is None
    )
