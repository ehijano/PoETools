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

orb_locations = {
'Orb of Augmentation': (300, 450)
, 'Orb of Alteration': (150, 350)
}
orb_counts = {
'Orb of Augmentation': 0
, 'Orb of Alteration': 0
}

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


def check_orb_available(orb_name):
    pa.hotkey("ctrlleft",'altleft', "c")
    orb_description = pyperclip.paste()
    if orb_name not in orb_description:
        error_message = 'No alterations available'
        logging.error(error_message)
        raise SystemExit(error_message)

def apply_orb(orb_name, safe = True):
    pa.moveTo(orb_locations[orb_name], duration = random.random()/2)
    if safe:
        check_orb_available(orb_name)
    pa.rightClick()
    pa.moveTo(item_location, duration = random.random()/2)
    pa.click()
    orb_counts[orb_name] = orb_counts[orb_name] + 1

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
        apply_orb('Orb of Augmentation')

    for prefix in mods_dict['Prefix Modifier']:
        if 'Twinned' in prefix[0]:
            logging.info('Item is twinned.')
            done = True


    while not done:

        logging.info('Item is not twinned -> Alterate.')
        apply_orb('Orb of Alteration')

        mods_dict, item_properties = measure_item()
        logging.info('NEW STATE: ')
        logging.info(mods_dict)

        prefix_list = mods_dict['Prefix Modifier']

        if len(prefix_list) == 0:
            logging.info('Item has no prefixtes -> Augment.')
            apply_orb('Orb of Augmentation')

            mods_dict, item_properties = measure_item()
            logging.info('NEW STATE: ')
            logging.info(mods_dict)

        for prefix in mods_dict['Prefix Modifier']:
            if 'Twinned' in prefix[0]:
                done = True
                logging.info('Item is twinned.')

        if orb_counts['Orb of Alteration'] > max_alts:
            done = True
        if keyboard.is_pressed('space'):
            done = True