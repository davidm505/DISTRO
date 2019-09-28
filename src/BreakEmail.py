from datetime import datetime, timedelta
import re
import os.path
import json

# FilPath Variables
cwd = os.getcwd()
filePath = os.path.dirname(os.path.realpath(__file__))

# JSON
json_path = os.path.join(filePath,"JSON/CrewList.json")

# Date Variables
date = datetime.today().strftime('%Y%m')
month = datetime.today().strftime('%B')
year = datetime.today().strftime('%Y')

def email_distro():

    email_distro_list = ''

    with open(json_path,'r') as f:
        distro_dict = json.load(f)

    for member in distro_dict["Break Email"]:
        email_distro_list += (member['Email'] + ' ')
    
    return email_distro_list


def day_check():
    '''
        Checks the current hour and adjust the day if it past midnight and before noon.
    '''

    hour = datetime.today().strftime('%H')
    hour = int(hour)
    
    if hour in range(0,13):
        yesterday = datetime.today() - timedelta(days=1)
        return yesterday.strftime('%d')
    else:
        return datetime.today().strftime('%d')


def runtime():
    '''
    Prompts for user input. Checks input against a regular expression.

    Returns:
        the trt as a string.
    '''

    while True:
        trt = str(input("Please enter the TRT: "))
        trtRegEX = re.compile(r'\d\d:\d\d:\d\d:\d\d')
        mo = trtRegEX.search(trt)
        
        if mo:
            return trt
        else:
            continue


def camera_rolls(roll):
    '''
    Takes in camera roll(s)

    Returns:
        Camera roll(s) as a string.
    '''

    mag_list = []

    cam_reg_ex = re.compile(r'''
        ([a-z]              # Camera Letter
        \d{3}               # Camera Numerical Roll
        (_\d\d\d\d\d)?)     # (optional) FrameRate
        ''', re.IGNORECASE | re.VERBOSE)

    mtch_obj = cam_reg_ex.findall(roll)

    for mag in mtch_obj:
        mag_list.append(mag[0])
        
        mag_list.sort()
        mtch_obj_string = ', '.join(mag_list)
        print(mtch_obj_string)
        return mtch_obj_string
    
    
def sound_rolls(roll):
    '''
    Prompts for user input. 

    Returns:
        Sound rolls as a string.
    '''

    sr_reg_ex = re.compile(r'(([a-z]{2})?\d\d\d)', re.IGNORECASE)

    sr = roll
    roll_list = []

    mo = sr_reg_ex.findall(sr)

    if mo:
        for roll in mo:
            roll_list.append(roll[0])

        sorted_roll = ', '.join(roll_list)
        return sorted_roll
    else:
        sr = 'None'
        return sr


def subject_generation(dict):

    subject = []

    subject.append("{show_code}_{date_day}_{episode}_{shooting_day} - {am_pm_break} Received".format(
        show_code=dict["show_code"], date_day=(date+dict["day"]), episode=dict["ep"],
        shooting_day=dict["shoot_day"], am_pm_break=dict["email"].capitalize()
    ))

    return subject


def body_generation(dict):

    body = []

    body.append('<strong>&ldquo;{show_name}&rdquo;</strong> {episode} Day {shooting_day}, {month} {day}, {year} - <strong>{am_pm_break} Received.</strong>'.format(
        show_name=dict["show_name"], episode=dict["ep"], shooting_day=dict["shoot_day"], month=month, day=dict["day"], year=year,
        am_pm_break=dict["email"].capitalize()
    ))
    
    body.append("<br>Total Footage Received and Transferred: {trt} ({gigabytes} GBs).".format(
        trt=dict['trt'], gigabytes=dict['gb']
    ))

    body.append("Camera Rolls {cr} and Sound Roll {sr} have been received at the lab.".format(
        cr=dict["cm"], sr=dict["sm"]
    ))

    return body
