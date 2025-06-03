class Utils:
    @staticmethod
    def config_key_helper(key):
        # filter out class - cannot be changed
        if key != "class":
            return True
        return False
    @staticmethod
    def config_value_helper(value):
        # Convert to string for simple checks
        val_str = str(value).strip().lower()

        # Skip empty or zero-like values
        if val_str in ('', '0', 'none', 'false'):
            return False

        # Skip values starting with dash (like '-borderwidth', '-background')
        if val_str.startswith('-'):
            return False
        

        # Skip system placeholders or common "default" words (case-insensitive)
        system_defaults = [
            'systemwindowbackgroundcolor',
            'systemtextcolor',
            'systemhighlightcolor',
            'systemhighlightbackground',
            'systembuttonface',
            'systembuttontext',
            'systemwindowtext',
            'systembuttonshadow',
            'systempressedbuttontextcolor',
            'tkdefaultfont'
        ]
        if val_str in system_defaults:
            return False

        return True
    @staticmethod
    def filter_config_values(config):
            filtered = {}
            for key, values in config.items():
                # The "actual value" may be the last element? Or you pick which?
                # From your example, the last element seems to be the current value
                current_value = values[-1]
                if not Utils.config_key_helper(key):
                    continue
                if Utils.config_value_helper(current_value):
                    filtered[key] = current_value
            return filtered