import praw
import urllib2
import datetime

reddit = praw.Reddit('bot1')
subreddit=reddit.subreddit("monsterhunter")
patch_notes_url = 'http://monsterhunterworld.com/us/topics/update_ver101/'


def get_current_version(lines):
  for line in lines:
    if '<section id="v' in line:
      return line.strip()[13:19]

#subreddit.submit("Testing",selftext="This is only a test")
response = urllib2.urlopen(patch_notes_url)
lines = response.readlines()

current_version = get_current_version(lines)

with open("mhw_version.txt", "r") as file:
  last_known = file.read()

if last_known != current_version:

  in_section = False
  html = ""
  body = ""

  for line in lines:
    if current_version in line:
      in_section = not in_section
    if in_section:
      html += line.strip()
      l = line.strip()
      if l.startswith('<h3>'):
        body += '[' + l[4:len(l)-5] + '](' + patch_notes_url + ')  \n=========  \n'
      if l.startswith('<h4>'):
        body += l[4:len(l)-5] + '  \n---------  \n'
      if l.startswith('<h5>'):
        body += '### ' + l[4:len(l)-5] + '  \n'
      if l.startswith('<p>'):
        body += l[3:len(l)-4] + '  \n'
      if l.startswith('<li>'):
        body += '*   ' + l[4:len(l)-5] + '  \n'
      if l.startswith('</'):
        body += '  \n'

  with open ("signature.txt", "r") as file:
    sig = file.read()      

  with open ("mhw_version.txt", "w") as file:
    file.write(current_version)
    
  post = body.strip() + sig
  title = 'Monster Hunter World - Patch Notes ' + datetime.date.today().strftime("%d %B %Y")
  subreddit.submit(title,selftext=post)
  with open ("patch_notes.log", "a") as file:
    file.write(datetime.datetime.now().strftime("%y-%m-%d %H%M") + ': Posted new patch notes to /r/monsterhunter \n')
else:
  with open ("patch_notes.log", "a") as file:
    file.write(datetime.datetime.now().strftime("%y-%m-%d %H%M") + ': No new patch notes found \n')
