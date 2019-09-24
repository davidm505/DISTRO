from datetime import datetime, timedelta
import re
import os
import json
import webbrowser



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

def email_distro():

    email_distro_list = ''

    with open(json_path,'r') as f:
        distro_dict = json.load(f)

    for member in distro_dict["Complete Email"]:
        email_distro_list += (member['Email'] + ' ')
    
    return email_distro_list

def stills_distro():

    still_distro_list = ''

    with open(json_path, 'r') as f:
        distro_dict = json.load(f)

    for member in distro_dict["Stills Email"]:
        still_distro_list += (member['Email'] + ' ')

    return still_distro_list

def day_check():
    '''
        Checks the current hour and adjusts the day if it past midnight and before noon
    '''

    hour = datetime.today().strftime('%H')

    hour = int(hour)

    if hour in range(0, 12):
        yesterday = datetime.today() - timedelta(days=1)
        return yesterday.strftime('%d')
    else:
        return datetime.today().strftime('%d')

def episode_gatherer():
    episodes = []

    while True:
        episode_num = str(input('Please Enter the Episode Number: '))
        episode_ctrt = str(input("Please Enter the Circle TRT: "))
        episode_trt = str(input("Please Enter the Total TRT: "))
        episodes.append((episode_num, episode_ctrt, episode_trt))

        cont = input("Are there more episode? [y/n]: ")
        if not cont.lower() in ('y' or 'yes'):
            return episodes

def episode_organizer(eps):

    organized_ep = ''

    i = 0
    for ep_block in eps:
        for key in ep_block:
            print(key)
            # organized_ep += ('<strong>Running Times:</strong><br>'
            #                 + ep_block[0] + ' Day ' + shooting_day + '<br>'
            #                 + "Total Viewing TRT:" + ep_block[1] + '<br>'
            #                 + "Total Editorial TRT: " + ep_block[2] + '<br><br>')

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

def discrepancy():
    '''
        Calls for input of discrepancies

        Returns:
                If no discrepancies, returns N/A.
                Else returns the discrepancies.
        '''

    discrep = str(input("Enter Discrepancies. If none, enter N: "))

    if discrep.upper() == 'N':
        discrep = 'N/A'

    return discrep

# def complete_email():

#     # Create Txt File
#     f = open('Complete.txt', 'w')
#     f.write(distr_list + '\n\n')
#     f.write(f'{show_code}_{date + day}_{episode}_{shooting_day} - Dailies Complete')
#     f.write(f'\n\n\"{show_name}\"\nShoot Date: {date + day}\nTransfer Date: {date + day}')
#     f.write(f'\n\nAll dailies work for \"{show_name}\" {episode} Day {shooting_day}, {month} {day}, {year} is now complete.')
#     f.write(f'\n\nDiscrepancy Highlights: {discrepancies}')
#     f.write(f'\n\nEditorial Files: All Editorial Dailies for {show_name} {episode} Day {shooting_day}, have been transferred over Aspera and can be found on The NEXIS.')
#     f.write(f'\n\nPIX: All PIX Screeners for {show_name} {episode}, Day {shooting_day}, have been uploaded to the Dailies unreleased folder.')
#     f.write(f'\n\nThe Break & Wrap On Set Rotation Drives are available for pickup from the dailies office at any time.  Building A room 216.')
#     f.write(f'\n\nReports:  Please find all attached reports from production and the dailies lab. The following Rotation Drives and Camera Rolls have been received, backed up, and QC’d at the lab.')
#     f.write(f'\n\nDrives Received:\n{shuttles}\nCamera Rolls Completed:\n{camera_rolls}\n\nSound Rolls:\n{sound_rolls}')
#     f.write(f'\n\n{ep_list}Total GB: {gigabytes}')
#     f.close()

#     complete_email = f'''
#     <html>
#         <title>Dailies Complete</title>
#         <body>
#             <h1>Dailies Complete</h1>
#             <p>
#                 {distr_list}
#             </p>
#             <br>
#             <p>
#                 {show_code}_{date + day}_{episode}_{shooting_day} - Dailies Complete
#             </p>
#             <br> 
#             <div>
#                 <strong>\"{show_name}\"</strong>
#                 <br>
#                 Shoot Date: {date + day}
#                 <br>
#                 Transfer Date: {date + day}
#             </div>
#             <br> 
#             <p>
#                 All dailies work for <strong>\"{show_name}\"</strong> {episode} Day {shooting_day}, {month} {day}, {year} is now complete.
#              </p>
#              <br> 
#             <p>
#                 <strong>Discrepancy Highlights:</strong> {discrepancies}
#             </p>
#             <br> 
#             <p>
#                 <strong>Editorial Files:</strong> All Editorial Dailies for <strong>\"{show_name}\"</strong> 
#                 {episode} Day {shooting_day}, have been transferred over Aspera and can be found on The NEXIS.
#             </p>
#             <br> 
#             <p>
#                 <strong>PIX:</strong> All PIX Screeners for <strong>\"{show_name}\"</strong> {episode}, 
#                 Day {shooting_day}, have been uploaded to the Dailies unreleased folder.
#             </p>
#             <br> 
#             <p>
#                 The <strong>Break & Wrap</strong> On Set Rotation Drives are available for pickup from 
#                 the dailies office at any time. Building A room 211.
#             </p>
#             <br> 
#             <p>
#                 <strong>Reports:</strong>  Please find all attached reports from production and the dailies lab. 
#                 The following Rotation Drives and Camera Rolls have been received, backed up, 
#                 and QC\'d at the lab.
#             </p>
#             <br> 
#             <div>
#                 <strong>Drives Received:</strong>
#                 <br>
#                 {shuttles}
#                 <br>
#                 <strong>Camera Rolls Completed:</strong>
#                 <br>
#                 {camera_rolls}
#                 <br>
#                 <br>
#                 <strong>Sound Rolls:</strong>
#                 <br>
#                 {sound_rolls}
#             </div>
#             <br> 
#             <p>
#                 {ep_list}
#                 Total TB: {gigabytes}
#             </p>
#             <br><br><br>
           
#         </body>
#     </html>
#     '''

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
#     html_file.write(complete_email)
#     stills_html.write(stills_email)
#     html_file.close()
#     stills_html.close()
    
#     webbrowser.get('chrome').open_new_tab('file://' + stills_html_path)
#     webbrowser.get('chrome').open_new_tab('file://' + html_path)


# complete_email()
