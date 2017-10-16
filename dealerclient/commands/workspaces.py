
import json

from cliff import show

from dealerclient.commands import base


def format_list(workspace=None):
    return format(workspace, lister=True)


def format(workspace=None, lister=False):
    columns = (
        'Name',
        'Type',
        'Display name',
        'Picture'
    )

    if workspace:
        data = (
            workspace.Name,
            workspace.Type,
            workspace.DisplayName,
            #
            workspace.Picture
        )
        if not lister:
            columns += ('Can',)
            data = data + (json.dumps(workspace.Can, indent=4),)
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.DealerLister):
    """List all workspaces."""

    def _get_format_function(self):
        return format_list

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)

        return parser

    def _get_resources(self, parsed_args):
        dealer_client = self.app.client

        return dealer_client.workspaces.list()


class Get(show.ShowOne):
    """Show specific workspace."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('workspace', help='Workspace name.')

        return parser

    def take_action(self, parsed_args):
        dealer_client = self.app.client
        ws = dealer_client.workspaces.get(parsed_args.workspace)

        return format(ws)
