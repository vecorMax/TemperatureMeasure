import configparser
import os


class CConfigManager:

    def create_config(path):
        """
        Create a config file
        """
        config = configparser.ConfigParser()
        config.add_section("Settings")
        config.set("Settings", "timedelay", "5")

        with open(path, "w") as config_file:
            config.write(config_file)

    def get_config(path):
        """
        Returns the config object
        """
        if not os.path.exists(path):
            CConfigManager.create_config(path)

        config = configparser.ConfigParser()
        config.read(path)
        return config

    def get_setting(path, section, setting):
        """
        Print out a setting
        """
        config = CConfigManager.get_config(path)
        value = config.get(section, setting)
        msg = "{section} {setting} is {value}".format(
            section=section, setting=setting, value=value
        )

        return value

    def update_setting(path, section, setting, value):
        """
        Update a setting
        """
        config = CConfigManager.get_config(path)
        config.set(section, setting, value)
        with open(path, "w") as config_file:
            config.write(config_file)

    def delete_setting(path, section, setting):
        """
        Delete a setting
        """
        config = CConfigManager.get_config(path)
        config.remove_option(section, setting)
        with open(path, "w") as config_file:
            config.write(config_file)

    if __name__ == "__main__":
        path = "settings1.ini"
