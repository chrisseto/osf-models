from addons.base.apps import BaseAddonConfig


class TwoFactorAddonConfig(BaseAddonConfig):

    name = 'addons.twofactor'
    full_name = 'Two-factor Authentication'

    # FOLDER_SELECTED = 'dropbox_folder_selected'
    # NODE_AUTHORIZED = 'dropbox_node_authorized'
    # NODE_DEAUTHORIZED = 'dropbox_node_deauthorized'

    actions = tuple()
    # actions = (FOLDER_SELECTED, NODE_AUTHORIZED, NODE_DEAUTHORIZED, )

    @property
    def user_settings(self):
        return self.get_model('TwoFactorUserSettings')
