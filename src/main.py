# Initialize
print('Loading config')
from config import loadConfig, config
loadConfig()
del loadConfig

from utils import checkAndRemoveFile
previousBootSuccessful = checkAndRemoveFile("successfulBoot")
silentBoot = checkAndRemoveFile("silentBoot")
del checkAndRemoveFile

if previousBootSuccessful and silentBoot:
    print("Silent rebooting")
else:
    from display import displayLogo
    displayLogo()
    del displayLogo

if previousBootSuccessful and config['wificlient']['ssid'] != '':
    import loop
    loop.normalBoot(config, silentBoot)
    del loop
else:
    print('Enabling AP to allow configuration')
    from httpServer import configBoot
    # At this level, only configBoot should be loaded
    configBoot(config)
    del configBoot

