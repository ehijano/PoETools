import pyautogui as pa
import time
import pyperclip
import re
import random
import logging
from datetime import datetime
import keyboard

time_now = datetime.now().strftime('%Y%m%d%H%M%S')
logging.basicConfig(level=logging.DEBUG, filename=f'log/PoECraftLog_{time_now}.log')

item_location = 450, 600
alt_location = 150, 350
aug_location = 300, 450
screen_size = pa.size()

def get_mods(item_mods:str):
    #print(item_mods)

    mods_dict = {'Prefix Modifier':[], 'Suffix Modifier':[]}
    pattern = re.compile(r"""{ ([^"]+) "([^"]+)" \(Tier: (\d)\)([^\}]+)}([^\{]+)""")

    
    for match in pattern.finditer(item_mods.replace('—','TAG').replace('\r\n','')):
        mod_type = match.group(1)
        mod_name = match.group(2)
        mod_tier = int(match.group(3))
        mod_tags =  match.group(4)
        mod_description = match.group(5)

        mods_dict[mod_type].append((mod_name, mod_tier, mod_tags, mod_description))

    return mods_dict

def measure_item():
    pa.moveTo(item_location, duration=0.1)
    pa.hotkey("ctrlleft",'altleft', "c")
    item_description = pyperclip.paste()
    item_mods = item_description.split('--------')[-2]
    item_properties = item_description.split('--------')[0]
    
    mods_dict = get_mods(item_mods)
    return mods_dict, item_properties

def augment():
    pa.moveTo(aug_location, duration = random.random()/2)
    pa.rightClick()
    pa.moveTo(item_location, duration = random.random()/2)
    pa.click()

def alterate(global_alt_count):
    pa.moveTo(alt_location, duration = random.random()/2)
    pa.rightClick()
    pa.moveTo(item_location, duration = random.random()/2)
    pa.click()
    global_alt_count += 1
    return global_alt_count

def craft_twinned_map(max_alts = 30):
    done = False
    global_alt_count = 0

    mods_dict, item_properties = measure_item()
    logging.info('NEW STATE: ')
    logging.info(mods_dict)

    prefix_list = mods_dict['Prefix Modifier']
    if 'Rare' in item_properties:
        logging.error('Item is rare')
        raise SystemExit('Item is rare')

    if len(prefix_list) == 0:
        logging.info('Item has no prefixtes -> Augment.')
        augment()

    for prefix in mods_dict['Prefix Modifier']:
        if 'Twinned' in prefix[0]:
            logging.info('Item is twinned.')
            done = True


    while not done:

        logging.info('Item is not twinned -> Alterate.')
        global_alt_count = alterate(global_alt_count)

        mods_dict, item_properties = measure_item()
        logging.info('NEW STATE: ')
        logging.info(mods_dict)

        prefix_list = mods_dict['Prefix Modifier']

        if len(prefix_list) == 0:
            logging.info('Item has no prefixtes -> Augment.')
            augment()

            mods_dict, item_properties = measure_item()
            logging.info('NEW STATE: ')
            logging.info(mods_dict)

        for prefix in mods_dict['Prefix Modifier']:
            if 'Twinned' in prefix[0]:
                done = True
                logging.info('Item is twinned.')

        if global_alt_count>max_alts:
            done = True
        if keyboard.is_pressed('space'):
            done = True