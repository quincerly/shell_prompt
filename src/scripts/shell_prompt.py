#! /usr/bin/env python3

import time
import os
import re
import traceback
import sys
import threading
import json

try:
    import colored
    from colored import stylize
    fancy_colour=True
except:
    from termcolor import colored
    fancy_colour=False

"""Get git status string or return None if it takes more than timeout sec"""
def get_git_status(timeout=2.0):
    def _get_git_status(results):
        results[0]=set([s[:2] for s in os.popen('git status -uno --porcelain .', 'r').read().split("\n") if s])
    results=[None]
    gd=threading.Thread(name='get_git_status', target=_get_git_status, args=(results,), daemon=True)
    gd.start()
    gd.join(timeout=timeout)
    return results[0]

class Icons:
    def __init__(self, use_unicode):
        if use_unicode:
            self.flame_up='\uf490'.encode('utf-8').decode()
            self.flame_left='\ue0c2'.encode('utf-8').decode()
            self.flame_right='\ue0c0'.encode('utf-8').decode()
            self.semi_left='\ue0b6'.encode('utf-8').decode()
            self.semi_right='\ue0b4'.encode('utf-8').decode()
            self.tri_left='\ue0b2'.encode('utf-8').decode()
            self.tri_right='\ue0b0'.encode('utf-8').decode()
            self.watch='\uf49b'.encode('utf-8').decode()
            self.lego='\ue0d1'.encode('utf-8').decode()
            self.house_outline='\uf46d'.encode('utf-8').decode()
            self.house_solid='\uf015'.encode('utf-8').decode()
            self.server1='\uf233'.encode('utf-8').decode()
            self.server2='\uf473'.encode('utf-8').decode()
            self.dataserver1='\uf1c0'.encode('utf-8').decode()
            self.dataserver2='\uf472'.encode('utf-8').decode()
            self.chev_left='\uf47d'.encode('utf-8').decode()
            self.chev_right='\uf460'.encode('utf-8').decode()
            self.git='\ue725'.encode('utf-8').decode()
            self.bookmark='\uf461'.encode('utf-8').decode()
            self.hourglass_full='\uf254'.encode('utf-8').decode()
            self.hourglass_start='\uf251'.encode('utf-8').decode()
            self.bicycle='\uf206'.encode('utf-8').decode()
            self.play='\uf04b'.encode('utf-8').decode()
            self.play_circle='\uf144'.encode('utf-8').decode()
            self.pause='\uf04c'.encode('utf-8').decode()
            self.pause_circle='\uf28b'.encode('utf-8').decode()
            self.container='\uf4b7'.encode('utf-8').decode()

            self.running=self.play
            self.queued=self.hourglass_start
            self.home=self.house_outline
        else:
            self.flame_up=""
            self.flame_left=""
            self.flame_right=""
            self.semi_left=""
            self.semi_right=""
            self.tri_left=""
            self.tri_right=""
            self.watch=""
            self.lego=""
            self.house_outline=""
            self.house_solid=""
            self.server1=""
            self.server2=""
            self.dataserver1=""
            self.dataserver2=""
            self.chev_left="<"
            self.chev_right=">"
            self.git="GIT"
            self.bookmark=""
            self.hourglass_full=""
            self.hourglass_start=""
            self.bicycle=""
            self.play=""
            self.play_circle=""
            self.pause=""
            self.pause_circle=""
            self.container='[]'

            self.running="R"
            self.queued="Q"
            self.home="~"

def prompt(cfg):

    bookmarks=cfg['bookmarks']
    servers=cfg['servers']

    use_unicode=(not os.environ['TERM'] in ['linux', 'xterm'] or 'ROXTERM_NUM' in os.environ) and "PROMPT_NO_UNICODE" not in os.environ
    host=os.popen('hostname', 'r').read().strip()

    sym=Icons(use_unicode)
    symtext=Icons(False)

    def simple_job_queue_info():
        return None

    def strip_ansi_escape(string):
        ansi_escape = re.compile(r'\x1b[^m]*m')
        result=ansi_escape.sub('', string)
        return result

    def vis_length(string):
        return len(strip_ansi_escape(string))

    def black_on(colour, text):
        if fancy_colour:
            return stylize(text, colored.fg("black")+colored.bg(colour))
        return colored(text, colour, attrs=['reverse'])
    def clr(text, colour):
        if fancy_colour:
            return stylize(text, colored.fg(colour))
        return colored(text, colour)

    def square_bar(text, colour):
        return black_on(colour, " "+text+" ")
    def round_bar(text, colour):
        return clr(sym.semi_left, colour)+black_on(colour, text)+clr(sym.semi_right, colour)
    def pointed_bar(text, colour):
        return clr(sym.tri_left, colour)+black_on(colour, text)+clr(sym.tri_right, colour)

    def replace_start(string, old, new, bra="", ket=""):
        if string[:len(old)]==old:
            return bra+new+ket+string[len(old):]
        return string
    def replace_path(path, old, new):
        return replace_start(path, old, new, sym.chev_left, sym.chev_right)
    def bookmark_replace(path, old, new):
        return replace_start(path, old, new, sym.bookmark+sym.chev_left, sym.chev_right)
    def server_replace(path, old, new):
        return replace_start(path, old, new, sym.dataserver2+sym.chev_left, sym.chev_right)
    def replace_path_noicons(path, old, new):
        return replace_start(path, old, new, symtext.chev_left, symtext.chev_right)
    def bookmark_replace_noicons(path, old, new):
        return replace_start(path, old, new, symtext.bookmark+symtext.chev_left, symtext.chev_right)
    def server_replace_noicons(path, old, new):
        return replace_start(path, old, new, symtext.dataserver2+symtext.chev_left, symtext.chev_right)
    def interpolate(path):
        return path.replace("{USER}", os.environ['USER'])

    user=os.environ['USER']
    rows, columns = list(map(int, os.popen('stty size', 'r').read().split()))
    cwd=os.getcwd()
    git_branch=os.popen('git rev-parse --abbrev-ref HEAD', 'r').read().strip() if os.system('git rev-parse 2> /dev/null > /dev/null')==0 else None
    job_info=simple_job_queue_info()

    if use_unicode:
        bar=round_bar
    else:
        bar=square_bar

    apptainer_bgcol='dark_goldenrod' if fancy_colour else 'yellow'
    userhost_bgcol='orchid' if fancy_colour else 'magenta'
    git_bgcol='light_sky_blue_1' if fancy_colour else 'cyan'
    cwd_bgcol='dark_sea_green_4b' if fancy_colour else 'green'
    clock_bgcol='light_goldenrod_1' if fancy_colour else 'yellow'

    # Build cwd text for prompt
    cwdtext=cwd
    cwdtext=replace_path(cwdtext, os.environ['HOME'], sym.home)
    for bookmark_path, bookmark_name in bookmarks:
        cwdtext=bookmark_replace(cwdtext, interpolate(bookmark_path), bookmark_name)
    for server_path, server_name in servers:
        cwdtext=server_replace(cwdtext, interpolate(server_path), server_name)

    # Build cwd text for window title
    cwdtextwtitle=cwd
    cwdtextwtitle=replace_start(cwdtextwtitle, os.environ['HOME'], "~")
    for bookmark_path, bookmark_name in bookmarks:
        cwdtextwtitle=bookmark_replace_noicons(cwdtextwtitle, interpolate(bookmark_path), bookmark_name)
    for server_path, server_name in servers:
        cwdtextwtitle=server_replace_noicons(cwdtextwtitle, interpolate(server_path), server_name)

    if git_branch is not None:
        git_bar_text = sym.git+" "+git_branch
        git_status=get_git_status()
        if git_status is None:
            git_bar_text += " |"+sym.hourglass_start+"..|"
        elif git_status:
            git_bar_text += " |{}|".format("|".join(sorted(git_status)))
        gitbar=[bar(git_bar_text, git_bgcol)]
    else:
        gitbar=[]

    if job_info is not None:
        jobbar=[bar(job_info, 'red')]
    else:
        jobbar=[]

    if "APPTAINER_CONTAINER" in os.environ:
        container_bar=[bar(sym.container+" Apptainer "+os.path.split(os.environ["APPTAINER_CONTAINER"])[1], apptainer_bgcol)+"\n"]
        #container_bar=[pointed_bar(sym.container+" Apptainer "+os.environ["APPTAINER_CONTAINER"], apptainer_bgcol)+"\n"]
        #container_bar=[bar(sym.container+" A", apptainer_bgcol)+"\n"]
        containertextwtitle="[A] "
    else:
        container_bar=[]
        containertextwtitle=""

    userhostbar=[bar(user+"@"+host, userhost_bgcol)]
    clockbar=[bar(sym.watch+" "+time.strftime("%H:%M:%S", time.localtime()), clock_bgcol)]
    cwdbar=[bar(cwdtext, cwd_bgcol)]

    #bars=container_bar+userhostbar+gitbar+cwdbar+jobbar+clockbar
    bars=userhostbar+gitbar+cwdbar+jobbar+clockbar

    length=vis_length("".join(bars))
    remainder=columns-length
    if remainder!=0:
        if remainder<0:
            chop=-remainder+2
            newlen=len(cwdtext.encode().decode('utf-8'))-chop
            cwdtext=sym.flame_up+" "+cwdtext[-newlen:] # Chop from end to avoid issues with unicode char length (unicode chars are at start)
        else:
            cwdtext+=" "*remainder
        cwdbar=[bar(cwdtext, cwd_bgcol)]
        #bars=container_bar+userhostbar+gitbar+cwdbar+jobbar+clockbar
        bars=userhostbar+gitbar+cwdbar+jobbar+clockbar

    window_title=containertextwtitle+cwdtextwtitle
    window_title_set_string="\033]0;"+window_title+"\007"

    #return window_title_set_string+"".join(container_bar+bars)+"\n$"
    return window_title_set_string+"".join(bars)+"\n"+"".join(container_bar)+"$ "

def main_cli():
    cfgfilepath=os.path.join(os.environ['HOME'], '.config', 'shell_prompt.conf')
    if os.path.exists(cfgfilepath):
        with open(cfgfilepath, 'r') as cfgfile:
            cfg=json.load(cfgfile)
    else:
        cfg={"bookmarks": [], "servers": []}

    try:
        p=prompt(cfg)
        print(p)
    except Exception as err:
        print("--- Prompt error -------------------------------------")
        traceback.print_exc(file=sys.stdout)
        print("-------------------------------------------------------")
        print("$ ")
