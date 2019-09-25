from datetime import datetime, timedelta
import re
import os
import json
import webbrowser


# Date Variables
date = datetime.today().strftime('%Y%m')
month = datetime.today().strftime('%B')
year = datetime.today().strftime('%Y')


class Organizer:

    def __init__(self, media):
        self.media = media

    def shuttle_regex(self):
        """[Compares string to Shuttle Drive regular expression.]

        Returns:
            [string] -- [All shuttle drives sorted inside of a string on their own line.]
        """
        shuttle_regex = re.compile(r'''
        \d  # Shuttle Drive Number
        ''', re.VERBOSE | re.IGNORECASE)

        match_obj = shuttle_regex.findall(self.media)
        match_obj.sort()
        match_obj_string =  ''.join(match_obj)

        return match_obj_string

    def cam_reg_ex(self):
        """[Compares string to camera roll regular expression.]

        Returns:
            [string] -- [All camera rolls sorted inside of a string on their own line.]
        """

        mag_list = []

        cam_reg_ex = re.compile(r'''
        ([a-z]           # Camera Letter
        \d{3}           # Camera Numerical Roll
        (_\d\d\d\d\d)?)     # (optional) FrameRate
        ''', re.IGNORECASE | re.VERBOSE)

        mtch_obj = cam_reg_ex.findall(self.media)

        for mag in mtch_obj:
            mag_list.append(mag[0])
        
        mag_list.sort()
        mtch_obj_string = '<br>'.join(mag_list)
        print(mtch_obj_string)
        return mtch_obj_string

    def sound_regex(self):
        """[Compares string to sound roll regular expression.]

        Returns:
            [string] -- [All sound rolls sorted in a string on their own line.]
        """

        roll_list = []
        sound_regex = re.compile(r'''
        (([a-z]{2})?   # Sound roll letters
        \d{3})       # Sound Roll number
        ''', re.VERBOSE | re.IGNORECASE)

        mtch_obj = sound_regex.findall(self.media)

        for roll in mtch_obj:
            roll_list.append(roll[0])

        roll_list.sort()
        mtch_obj_string = '<br>'.join(roll_list)
        return mtch_obj_string

    def __str__(self):
        return self.media


def episode_organizer(eps, day):

    organized_ep = ''

    for ep_block in eps:
        print(ep_block["ep"])
        print(ep_block["trt"])
        print(ep_block["ctrt"])
        organized_ep += ('<strong>Running Times:</strong><br>'
                        + ep_block["ep"] + ' Day ' + day + '<br>'
                        + "Total Viewing TRT: " + ep_block["ctrt"] + '<br>'
                        + "Total Editorial TRT: " + ep_block["trt"] + '<br><br>')

    return organized_ep


def shuttle_organizer():
    '''
        Returns:
                Organized shuttle(s), and displays them on their
                own line.
    '''

    shuttle_drives = ''

    while shuttle_drives == '':
        shuttle_drives = str(input("Please Enter Shuttle Drives: "))

        s = Organizer(shuttle_drives)
        new_shuttles = s.shuttle_regex()

        appended_shuttle_list = ''

        for drive in new_shuttles:
            appended_shuttle_list += "Shuttle Drive: " + drive + '<br>'

        return appended_shuttle_list


def camera_roll_organizer():
    '''
        Calls for input of camera roll(s).

        Returns:
                Camera roll(s), and displays them on their
                own line.
        '''

    camera_rolls = ''

    while camera_rolls == '':
        camera_rolls = str(input('Please Enter Camera Rolls: '))

        new_camera_rolls = Organizer(camera_rolls)
        return new_camera_rolls.cam_reg_ex().upper()


def sound_roll_organizer():
    """[Prompts for sound roll input,]

    Returns:
        [string] -- [returns sound rolls formatted on a new line per roll]
    """

    sound_rolls = ''

    while sound_rolls == '':

        sound_rolls = str(input("Please Enter Sound Rolls: "))
        new_sound_roll = Organizer(sound_rolls)

        return new_sound_roll.sound_regex().upper()


def complete_subject(dict):
    pass
    subject = f'''
        {dict["show_code"]}_{date + dict["day"]}_{dict["ep"]}_{dict["shoot_day"]} - Dailies Complete
    '''

    return subject


def complete_body(dict):
    """Generates Complete Email body in HTML
    
    Arguments:
        dict {dictionary} -- dictionary containing trts, master media, shoot day,
                            current day, current ep, potential ep & trt groups,
                            show name, show code.
    
    Returns:
        string -- Complete email body in html
    """

    body = f'''
        <div>
            <strong>\"{dict["show_name"]}\"</strong>
            <br>
            Shoot Date: {date + dict["day"]}
            <br>
            Transfer Date: {date + dict["day"]}
        </div>
            <br> 
            <p>
                All dailies work for <strong>\"{dict["show_name"]}\"</strong> {dict["ep"]} Day {dict["shoot_day"]}, {month} {dict["day"]}, {year} is now complete.
            </p>
            <br> 
            <p>
                <strong>Discrepancy Highlights:</strong> {dict["discrepancies"]}
            </p>
            <br> 
            <p>
                <strong>Editorial Files:</strong> All Editorial Dailies for <strong>\"{dict["show_name"]}\"</strong> 
                {dict["ep"]} Day {dict["shoot_day"]}, have been transferred over Aspera and can be found on The NEXIS.
            </p>
            <br> 
            <p>
                <strong>PIX:</strong> All PIX Screeners for <strong>\"{dict["show_name"]}\"</strong> {dict["ep"]}, 
                Day {dict["shoot_day"]}, have been uploaded to the Dailies unreleased folder.
            </p>
            <br> 
            <p>
                The <strong>Break & Wrap</strong> On Set Rotation Drives are available for pickup from 
                the dailies office at any time. Building A room 211.
            </p>
            <br> 
            <p>
                <strong>Reports:</strong>  Please find all attached reports from production and the dailies lab. 
                The following Rotation Drives and Camera Rolls have been received, backed up, 
                and QC\'d at the lab.
            </p>
            <br> 
            <div>
                <strong>Drives Received:</strong>
                <br>
                {dict["shuttles"]}
                <br>
                <strong>Camera Rolls Completed:</strong>
                <br>
                {dict["cm"]}
                <br>
                <br>
                <strong>Sound Rolls:</strong>
                <br>
                {dict["sm"]}
            </div>
            <br> 
            <p>
                {dict["trts"]}
                Total TB: {dict["gb"]}
            </p>
            <br><br>
    '''

    return body


#     stills_email = f'''
#     <html>
#         <head>
#             <title>Stills Email</title>
#         </head>
#         <body>
#             <p>{stills_distro_list}</p>
#             <p>
#                 {show_code}_{date + day}_{episode}_{shooting_day} - Stills
#             </p>
#             <div>
#                 Hello,
#             </div>
#             <br>
#             <div>
#                 Included is a link​​​​​ to the stills​ for, <strong>\"{show_name}\"</strong> ​Episode {episode}, Day {shooting_day}​.
#             </div>
#         </body>
#     </html>
#     '''
    