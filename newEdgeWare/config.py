import json
import os
import configparser
from dataclasses import dataclass, asdict

@dataclass
class Configuration:
    version: str
    delay: int
    fill: int
    replace: int
    webmod: int
    popupmod: int
    audiomod: int
    promptmod: int
    vidmod: int
    replacethresh: int
    slowmode: int
    pip_installed: int
    is_configed: int
    fill_delay: int
    start_on_logon: int
    hibernatemode: int
    hibernatemin: int
    hibernatemax: int
    wakeupactivity: int
    pypres_installed: int
    showdiscord: int
    pil_installed: int
    showloadingflair: int
    showcaptions: int
    maxfillthreads: int
    panicbutton: str
    panicdisabled: int
    promptmistakes: int
    squarelim: int
    mitosismode: int
    onlyvid: int
    webpopup: int
    rotatewallpaper: int
    wallpapertimer: int
    wallpapervariance: int
    timeoutpopups: int
    popuptimeout: int
    mitosisstrength: int
    avoidlist: str
    booruname: str
    booruminscore: int
    taglist: str
    downloadenabled: int
    downloadmode: str
    usewebresource: int
    runonsavequit: int
    timermode: int
    timersetuptime: int
    safeword: str
    lkcorner: int
    lkscaling: int
    lktoggle: int
    videovolume: int
    denialmode: int
    denialchance: int
    popupsubliminals: int
    drivepath: str
    default: dict
    resource: str
    captions: dict = None
    web: list = None
    prompts: dict = None

    @classmethod
    def load_configuration(cls):
        config_dir = 'configs'
        config_file = os.path.join(config_dir, 'configuration.cfg')

        # Check if configuration file exists
        if os.path.isfile(config_file):
            config = configparser.ConfigParser()
            config.read(config_file)

            # Check if there is a USER section
            if 'USER' in config:
                user_config = dict(config['USER'])
                user_config = {key: cls._convert_value(key, value) for key, value in user_config.items()}
                return cls(**user_config)
            else:
                default_config = dict(config['DEFAULT'])
                default_config = {key: cls._convert_value(key, value) for key, value in default_config.items()}
                config.add_section('USER')
                for key, value in default_config.items():
                    config.set('USER', key, str(value))
                
                with open(config_file, 'w') as config_file:
                    config.write(config_file)
                
                return cls(**default_config)
        else:
            raise FileNotFoundError("Configuration file not found.")

    @staticmethod
    def _convert_value(key, value):
        if key in ['delay', 'fill', 'replace', 'webmod', 'popupmod', 'audiomod', 'promptmod', 'vidmod',
                   'replacethresh', 'slowmode', 'pip_installed', 'is_configed', 'fill_delay', 'start_on_logon',
                   'hibernatemode', 'hibernatemin', 'hibernatemax', 'wakeupactivity', 'pypres_installed',
                   'showdiscord', 'pil_installed', 'showloadingflair', 'showcaptions', 'maxfillthreads',
                   'panicdisabled', 'promptmistakes', 'squarelim', 'mitosismode', 'onlyvid', 'webpopup',
                   'rotatewallpaper', 'wallpapertimer', 'wallpapervariance', 'timeoutpopups', 'popuptimeout',
                   'mitosisstrength', 'booruminscore', 'downloadenabled', 'usewebresource', 'runonsavequit',
                   'timermode', 'timersetuptime', 'lkcorner', 'lkscaling', 'lktoggle', 'videovolume', 'denialmode',
                   'denialchance', 'popupsubliminals']:
            return int(value)
        elif key in ['wallpaperdat']:
            return eval(value)
        else:
            return value

    def save(self):
        config_dir = 'configs'
        config_file = os.path.join(config_dir, 'configuration.cfg')

        config = configparser.ConfigParser()
        config.read(config_file)

        if 'USER' not in config: config.add_section('USER')

        for field, value in asdict(self).items():
            config.set('USER', field, str(value))

        with open(config_file, 'w') as config_file:
            config.write(config_file)

    def load_jsons(self):
        if os.path.exists(self.resource + '\\captions.json'):
            with open(self.resource + '\\captions.json', 'r') as file:
                self.captions = json.load(file)
        
        if os.path.exists(self.resource + '\\web.json'):
            with open(self.resource + '\\web.json', 'r') as file:
                self.web = json.load(file)

        if os.path.exists(self.resource + '\\prompt.json'):
            with open(self.resource + '\\prompt.json', 'r') as file:
                self.prompts = json.load(file)

        
        

if __name__ == "__main__":
    config = Configuration.load_configuration()
    print(config)
    