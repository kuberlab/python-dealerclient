
"""
Command-line interface to the Dealer APIs
"""

import argparse
import logging
import os
import sys

from cliff import app
from cliff import command
from cliff import commandmanager

from dealerclient.api import client
import dealerclient.commands.apps
import dealerclient.commands.organizations
import dealerclient.commands.projects
import dealerclient.commands.workspaces


def env(*args, **kwargs):
    """Returns the first environment variable set.

    If all are empty, defaults to '' or keyword arg `default`.
    """
    for arg in args:
        value = os.environ.get(arg)
        if value:
            return value
    return kwargs.get('default', '')


class HelpFormatter(argparse.HelpFormatter):

    def __init__(self, prog, indent_increment=2, max_help_position=32,
                 width=None):
        super(HelpFormatter, self).__init__(
            prog,
            indent_increment,
            max_help_position,
            width
        )

    def start_section(self, heading):
        # Title-case the headings.
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)


class HelpAction(argparse.Action):
    """Custom help action.

    Provide a custom action so the -h and --help options
    to the main app will print a list of the commands.

    The commands are determined by checking the CommandManager
    instance, passed in as the "default" value for the action.

    """

    def __call__(self, parser, namespace, values, option_string=None):
        outputs = []
        max_len = 0
        app = self.default
        parser.print_help(app.stdout)
        app.stdout.write('\nCommands for API:\n')

        for name, ep in sorted(app.command_manager):
            factory = ep.load()
            cmd = factory(self, None)
            one_liner = cmd.get_description().split('\n')[0]
            outputs.append((name, one_liner))
            max_len = max(len(name), max_len)

        for (name, one_liner) in outputs:
            app.stdout.write('  %s  %s\n' % (name.ljust(max_len), one_liner))

        sys.exit(0)


class BashCompletionCommand(command.Command):
    """Prints all of the commands and options for bash-completion."""

    def take_action(self, parsed_args):
        commands = set()
        options = set()

        for option, _action in self.app.parser._option_string_actions.items():
            options.add(option)

        for command_name, _cmd in self.app.command_manager:
            commands.add(command_name)

        print(' '.join(commands | options))


class DealerShell(app.App):

    def __init__(self):
        super(DealerShell, self).__init__(
            description=__doc__.strip(),
            version=dealerclient.__version__,
            command_manager=commandmanager.CommandManager('dealer.cli'),
        )

        # Set commands by default
        self._set_shell_commands(self._get_commands())

    def configure_logging(self):
        log_lvl = logging.DEBUG if self.options.debug else logging.WARNING
        logging.basicConfig(
            format="%(levelname)s (%(module)s) %(message)s",
            level=log_lvl
        )
        logging.getLogger('iso8601').setLevel(logging.WARNING)

        if self.options.verbose_level <= 1:
            logging.getLogger('requests').setLevel(logging.WARNING)

    def build_option_parser(self, description, version,
                            argparse_kwargs=None):
        """Return an argparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.

        :param description: full description of the application
        :paramtype description: str
        :param version: version number for the application
        :paramtype version: str
        :param argparse_kwargs: extra keyword argument passed to the
                                ArgumentParser constructor
        :paramtype extra_kwargs: dict
        """
        argparse_kwargs = argparse_kwargs or {}

        parser = argparse.ArgumentParser(
            description=description,
            add_help=False,
            formatter_class=HelpFormatter,
            **argparse_kwargs
        )

        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version),
            help='Show program\'s version number and exit.'
        )

        parser.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.',
        )

        parser.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='Suppress output except warnings and errors.',
        )

        parser.add_argument(
            '-h', '--help',
            action=HelpAction,
            nargs=0,
            default=self,  # tricky
            help="Show this help message and exit.",
        )

        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='Show tracebacks on errors.',
        )

        parser.add_argument(
            '--dealer-url',
            action='store',
            dest='dealer_url',
            default=env('DEALER_URL') or 'https://dev.kuberlab.io/api/v0.2',
            help='Dealer API base url (Env: DEALER_URL)'
        )

        parser.add_argument(
            '--username',
            action='store',
            dest='username',
            default=env('DEALER_USERNAME'),
            help='Authentication username (Env: DEALER_USERNAME)'
        )

        parser.add_argument(
            '--password',
            action='store',
            dest='password',
            default=env('DEALER_PASSWORD'),
            help='Authentication password (Env: DEALER_PASSWORD)'
        )

        parser.add_argument(
            '--insecure',
            action='store_true',
            dest='insecure',
            default=env('DEALER_CLIENT_INSECURE', default=False),
            help='Disables SSL/TLS certificate verification '
                 '(Env: DEALER_CLIENT_INSECURE)'
        )

        parser.add_argument(
            '--client-id',
            action='store',
            dest='client_id',
            default=env('DEALER_CLIENT_ID'),
            help='Client ID.'
                 ' (Env: DEALER_CLIENT_ID)'
        )

        parser.add_argument(
            '--client-secret',
            action='store',
            dest='client_secret',
            default=env('DEALER_CLIENT_SECRET'),
            help='Client secret'
                 ' (Env: DEALER_CLIENT_SECRET)'
        )

        return parser

    def initialize_app(self, argv):
        self._clear_shell_commands()

        self._set_shell_commands(self._get_commands())

        completion = ('bash-completion' in argv)
        if completion:
            return

        # if not (self.options.client_id or self.options.client_secret):
        #     if not self.options.username:
        #         raise exe.IllegalArgumentException(
        #             ("You must provide a username "
        #              "via --username env[DEALER_USERNAME]")
        #         )
        #
        #     if not self.options.password:
        #         raise exe.IllegalArgumentException(
        #             ("You must provide a password "
        #              "via --password env[DEALER_PASSWORD]")
        #         )

        session = client.create_session(
            self.options.dealer_url,
            username=self.options.username,
            password=self.options.password,
            insecure=self.options.insecure,
            client_id=self.options.client_id,
            client_secret=self.options.client_secret,
        )
        self.client = client.Client(
            session,
            dealer_url=self.options.dealer_url,
            insecure=self.options.insecure,
        )

    def _set_shell_commands(self, cmds_dict):
        for k, v in cmds_dict.items():
            self.command_manager.add_command(k, v)

    def _clear_shell_commands(self):
        exclude_cmds = ['help', 'complete']

        cmds = self.command_manager.commands.copy()
        for k, v in cmds.items():
            if k not in exclude_cmds:
                self.command_manager.commands.pop(k)

    @staticmethod
    def _get_commands():
        return {
            'bash-completion': BashCompletionCommand,
            'workspace-list': dealerclient.commands.workspaces.List,
            'workspace-get': dealerclient.commands.workspaces.Get,

            'org-list': dealerclient.commands.organizations.List,
            'org-get': dealerclient.commands.organizations.Get,
            'org-create': dealerclient.commands.organizations.Create,
            'org-delete': dealerclient.commands.organizations.Delete,
            'org-update': dealerclient.commands.organizations.Update,

            'project-list': dealerclient.commands.projects.List,
            'project-get': dealerclient.commands.projects.Get,
            'project-create': dealerclient.commands.projects.Create,
            'project-delete': dealerclient.commands.projects.Delete,
            'project-update': dealerclient.commands.projects.Update,

            'app-list': dealerclient.commands.apps.List,
            'app-get': dealerclient.commands.apps.Get,
            'app-get-config': dealerclient.commands.apps.GetConfig,
            'app-delete': dealerclient.commands.apps.Delete,
        }


def main(argv=sys.argv[1:]):
    return DealerShell().run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
