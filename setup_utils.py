#! /usr/bin/env python3

import ast
from pathlib import Path
from typing import Callable, Optional, Tuple


class VersionTransformer(ast.NodeVisitor):
    def __init__(self,
                 *args,
                 version_tags: Tuple[str, ...] = ('__version__', '__version_info__', 'VERSION'),
                 version_transform: Callable[[str], str] = None,
                 **kwargs):
        super(VersionTransformer, self).__init__(*args, **kwargs)

        self.version_old: Optional[str] = None
        self.version_new: Optional[str] = None
        self.version_tags: Tuple[str, ...] = version_tags
        self.version_transform: Callable[[str], str] = version_transform

        self.version_lineno: Optional[int] = None
        self.version_tag: Optional[str] = None

        self._block_end_lineno: int = -1

    def visit_Assign(self, node):
        if self._block_end_lineno > node.lineno \
                or len(node.targets) != 1 \
                or node.targets[0].id not in self.version_tags:
            return node

        self.version_lineno = node.lineno
        self.version_tag = node.targets[0].id

        if isinstance(node.value, ast.Str):
            self.version_old = node.value.s
        elif isinstance(node.value, ast.Tuple):
            r = []
            for e in node.value.elts:
                if isinstance(e, ast.Str):
                    r.append(e.s)
                elif isinstance(e, ast.Num):
                    r.append(str(e.n))
            self.version_old = '.'.join(r)

        if self.version_transform:
            self.version_new = self.version_transform(self.version_old)
        else:
            self.version_new = self.version_old

        return node

    def generic_visit(self, node: 'ast.AST') -> 'ast.AST':
        if self._is_block(node):
            self._set_block_end_lineno(node.end_lineno)

        return super(VersionTransformer, self).generic_visit(node)

    def _is_block(self, node: 'ast.AST') -> bool:
        return isinstance(node, (ast.ClassDef, ast.FunctionDef))

    def _set_block_end_lineno(self, lineno: int):
        self._block_end_lineno = max(self._block_end_lineno, lineno)


def get_version_from_file(fl: Path, **kwargs) -> str:
    visitor = VersionTransformer(**kwargs)
    visitor.visit(ast.parse(fl.read_text()))
    return visitor.version_old


def get_development_version_from_file(fl: Path, rev_count: int = None, commit: str = None, **kwargs) -> str:
    version = get_version_from_file(fl, **kwargs)
    if rev_count is not None:
        lvl = '-beta'
        suffix = ''

        if commit is not None:
            lvl = '-alpha'
            suffix = f'+git{commit[:7]}'

        version = f'{version}{lvl}.{rev_count}{suffix}'

    return version


def set_version_to_file(fl: Path, new_version: str, **kwargs) -> str:
    visitor = VersionTransformer(version_transform=lambda x: new_version,
                                 **kwargs)
    orig_code = fl.read_text()

    visitor.visit(ast.parse(orig_code))

    orig_code_lines = orig_code.split('\n')

    new_code = '\n'.join([*orig_code_lines[0:visitor.version_lineno - 1],
                          f"{visitor.version_tag} = '{visitor.version_new}'",
                          *orig_code_lines[visitor.version_lineno:]])

    try:
        import autopep8
    except ImportError:
        pass
    else:
        new_code = autopep8.fix_code(new_code,
                                     options={'aggressive': 5,
                                              'max_line_length': 120,
                                              'experimental': True},
                                     apply_config=True)

    try:
        import isort
    except ImportError:
        pass
    else:
        new_code = isort.code(new_code, config=isort.Config(line_length=120,
                                                            reverse_relative=True))

    fl.write_text(new_code)

    return visitor.version_new


def get_requirements_from_file(req_file: Path):
    def parse_imported_reqs(l):
        f = l[len('-r '):].strip()
        if ' ' in l:
            f, r = l[len('-r '):].split(' ', 1)
            r = r.strip()
            if r.startswith('-r '):
                yield from parse_imported_reqs(r)

        yield from get_requirements_from_file(req_file.parent / Path(f))

    with req_file.open() as f:
        reqs = []
        for l in f.readlines():
            if '#' in l:
                l = l[:l.index('#')]
            l = l.strip()

            if not l or l.startswith('-'):
                if l.startswith('-r '):
                    reqs.extend(parse_imported_reqs(l))
                continue

            reqs.append(l)

        return reqs


def increase_version(version: str, level: str = 'bugfix'):
    version = tuple(int(v) for v in version.split('.')[:3])

    if level == 'major':
        version = (version[0] + 1, 0, 0)
    elif level == 'minor':
        version = (version[0], version[1] + 1, 0)
    elif level == 'bugfix':
        version = (version[0], version[1], version[2] + 1)

    return '.'.join([str(v) for v in version])


if __name__ == '__main__':

    try:
        import click
    except ImportError:
        print('Click is not installed!')
    else:
        version_file = Path(__file__).parent / 'configure.py'

        @click.group()
        def cli():
            pass

        @cli.command(name='get-version')
        @click.argument('file',
                        type=click.Path(),
                        default=version_file,
                        required=False)
        def cli_get_version(file):
            file = Path(file)

            version = get_version_from_file(file)

            click.echo(version)

            return version

        @cli.command(name='set-version')
        @click.option('--version', '-v',
                      type=str,
                      required=True,
                      help='New version to set')
        @click.argument('file',
                        type=click.Path(),
                        default=version_file,
                        required=False)
        def cli_set_version(file, version):
            file = Path(file)

            version = set_version_to_file(file, version)

            click.echo(version)

            return version

        @cli.command(name='increase-version')
        @click.option('--level', '-l',
                      type=click.Choice(['major', 'minor', 'bugfix'], case_sensitive=False),
                      default='bugfix',
                      help='Which version number to increase')
        @click.argument('file',
                        type=click.Path(),
                        default=version_file,
                        required=False)
        def cli_increase_version(file, level):
            file = Path(file)

            version = increase_version(get_version_from_file(file), level=level)

            version = set_version_to_file(file, version)

            click.echo(version)

            return version

        @cli.command(name='set-development-version')
        @click.option('--commit', '-c',
                      type=str,
                      required=False,
                      help='Commit reference',
                      envvar='PACKAGE_COMMIT')
        @click.option('--build', '-b',
                      type=str,
                      required=True,
                      help='Build reference',
                      envvar='PACKAGE_DEVELOPMENT')
        @click.argument('file',
                        type=click.Path(),
                        default=version_file,
                        required=False)
        def cli_set_development_version(file, commit, build):
            file = Path(file)

            version = get_development_version_from_file(file, rev_count=build, commit=commit)
            version = set_version_to_file(file, version)

            click.echo(version)

            return version

        cli(obj={})
