# -*- coding: utf-8 -*-
import praw
import urllib, urllib2
from datetime import datetime
from PIL import Image
from pytesseract import image_to_string
from scipy.misc import imsave
import numpy
import re

events_url = 'http://monsterhunterworld.com/eventquest/MHW_EventQuest_EN.pdf'

def main():
  #download PDF from monsterhunterworld.com
  urllib.urlretrieve(events_url,'current.pdf')

  #convert to PDF to image
  pdf_to_image('current.pdf','current.jpg')
  
  #split images based on column and misc.
  fullPic = Image.open('current.jpg')
  w, h = fullPic.size
  quests = fullPic.crop((1277,653,2257,h-512))
  imsave('images/quests.jpg',quests)
  binarize_image('images/quests.jpg','images/quests_bw.jpg')
  #quests.show()
  locale = fullPic.crop((2257,653,2653,h-512))
  imsave('images/locale.jpg',locale)
  binarize_image('images/locale.jpg','images/locale_bw.jpg')
  #locale.show()
  requirements = fullPic.crop((2653,653,3153,h-512))
  imsave('images/requirements.jpg',requirements)
  binarize_image('images/requirements.jpg','images/requirements_bw.jpg')
  #requirements.show()
  objectives = fullPic.crop((3153,653,3781,h-512))
  imsave('images/objectives.jpg',objectives)
  binarize_image('images/objectives.jpg','images/objectives_bw.jpg')
  #objectives.show()
  week1 = fullPic.crop((3781,737,4469,h-512))
  #week1.show()
  week2 = fullPic.crop((4469,737,5161,h-512))
  #week2.show()
  week3 = fullPic.crop((5161,737,5857,h-512))
  #week3.show()
  info = fullPic.crop((85,h-512,5857,h-242))
  imsave('images/info.jpg',info)
  binarize_image('images/info.jpg','images/info_bw.jpg')
  #info.show()
  
  #convert to string...
  quests_txt = image_to_string(Image.open('images/quests_bw.jpg'))
  locale_txt = image_to_string(Image.open('images/locale_bw.jpg'))
  requirements_txt = image_to_string(Image.open('images/requirements_bw.jpg'))
  objectives_txt = image_to_string(Image.open('images/objectives_bw.jpg'))
  info_txt = image_to_string(Image.open('images/info_bw.jpg')).replace('xX','')
  
  #remove blank lines
  #quests_txt = filter(lambda x: not re.match(r'^\s*$',x),quests_txt)
  #locale_txt = filter(lambda x: not re.match(r'^\s*$',x),locale_txt)
  #requirements_txt = filter(lambda x: not re.match(r'^\s*$',x),requirements_txt)
  #objectives_txt = filter(lambda x: not re.match(r'^\s*$',x),objectives_txt)
  #info_txt = filter(lambda x: not re.match(r'^\s*$',x),info_txt)
  
  #put everything in lists
  quests_e,quests_c = string_to_list(quests_txt,['dule'])
  locale_e,locale_c = string_to_list(locale_txt)
  req_e,req_c = string_to_list(requirements_txt)
  obj_e,obj_c = string_to_list(objectives_txt)
  
  #split weeks by quests
  w = 1
  ps4_e = []
  ps4_c = []
  week_e = [[],[],[]]
  week_c = [[],[],[]]
  merged_e = {}
  merged_q = {}
  
  for week in (week1,week2,week3):
    width,h = week.size
    date = week.crop((0,0,width,97))
    imsave('images/week'+str(w)+'/date.jpg',date)
    a = 0
    b = 97
    c = width
    d = 679
    d_tmp = d
    for i in range(0,len(quests_e)):
      q = week.crop((a,b,c,d))
      imsave('images/week'+str(w)+'/quest'+str(i)+'.jpg',q)
      binarize_image('images/week'+str(w)+'/quest'+str(i)+'.jpg','images/week'+str(w)+'/quest'+str(i)+'_bw.jpg')
      txt = image_to_string(Image.open('images/week'+str(w)+'/quest'+str(i)+'_bw.jpg'))
      active,connected = process_quest(txt)
      if active:
        week_e[w-1].append(i)
        if connected:
          if i not in merged_e.keys():
            merged_e[i] = []
          merged_e[i].append(txt)
      q_pix = q.load()
      if is_blue(q_pix[10,10]):
        if i not in ps4_e:
          ps4_e.append(i)
      d_tmp = d
      b = d
      d = d + 582
    b = d_tmp + 424
    d = b + 582
    for i in range(0,len(quests_c)):
      q = week.crop((a,b,c,d))
      imsave('images/week'+str(w)+'/challenge'+str(i)+'.jpg',q)
      binarize_image('images/week'+str(w)+'/challenge'+str(i)+'.jpg','images/week'+str(w)+'/challenge'+str(i)+'_bw.jpg')
      txt = image_to_string(Image.open('images/week'+str(w)+'/challenge'+str(i)+'_bw.jpg'))
      active,connected = process_quest(txt)
      if active:
        week_e[w-1].append(i)
        if connected:
          if i not in merged_q.keys():
            merged_q[i] = []
          merged_q[i].append(txt)
      q_pix = q.load()
      if is_blue(q_pix[10,10]):
        if i not in ps4_c:
          ps4_c.append(i)
      b = d
      d = d + 582
    w = w + 1
  
  special_e = {}
  special_c = {}
  for i in merged_e.keys():
    first = merged_e[i][0].strip().splitlines()[-1]
    last = merged_e[i][1].strip().splitlines()[-1]
    merged = first + last
    if '(x)' in merged:
      special_e[i] = info_txt
    else:
      special_e[i] = merged
  for i in merged_q.keys():
    first = merged_q[i][0].strip().splitlines()[-1]
    last = merged_q[i][1].strip().splitlines()[-1]
    merged = first + last
    if '(x)' in merged:
      special_c[i] = info_txt
    else:
      special_c[i] = merged.encode('utf-8').replace('\xe2\x80\x94','-')
  
  body = '''Weekly Events
===========  
  
Quest Name|Locale|Requirements|Objective|Special Rewards
:---:|:---:|:---:|:---:|:---:  \n'''.encode('utf-8')
  
  specials = ['^†','^‡','※','°','•']
  spec = 0
  ps4 = False
  
  current_week = get_week((week1,week2,week3))
  if current_week != -1:
    events = week_e[current_week - 1]
    challenges = week_c[current_week - 1]
    notes = u""
    for i in range(0,len(quests_e)):
      if i in events:
        rewards = ""
        body += quests_e[i].encode('utf-8')
        if i in special_e.keys():
          body += specials[spec]
          notes += specials[spec] + ' *' + special_e[i].encode('utf-8') + '*  \n'
          spec += 1
        if i in ps4_e:
          body += '*'
          ps4 = True
        body += '|' + locale_e[i].encode('utf-8') + '|' + req_e[i].encode('utf-8') + '|'
        with open('quest_info.txt','r') as f:
          for line in f.readlines():
            if quests_e[i] in line:
              quest_arr = line.split('|')
              obj_e[i] = quest_arr[1]
              rewards = quest_arr[2]
        body += obj_e[i].encode('utf-8') + '|' + rewards.strip().encode('utf-8') + '  \n'
    if ps4:
      body += '* *PS4 only*  \n'
    body += notes.encode('utf-8')
    ps4 = False
    notes = "".encode('utf-8')
    spec = 0
    body += '''  \nWeekly Challenges
==============   
  
Quest Name|Locale|Requirements|Objective|Special Rewards
:---:|:---:|:---:|:---:|:---:  \n'''
    for i in range(0,len(quests_c)):
      if i in challenges:
        rewards = ""
        body += quests_c[i].encode('utf-8')
        if i in special_c.keys():
          body += specials[spec].encode('utf-8')
          notes += specials[spec].encode('utf-8') + ' *' + special_c[i].encode('utf-8') + '*  \n'
          spec += 1
        if i in ps4_c:
          body += '*'
          ps4 = True
        body += '|' + locale_c[i].encode('utf-8') + '|' + req_c[i].encode('utf-8') + '|'
        with open('quest_info.txt','r') as f:
          for line in f.readlines():
            if quests_e[i] in line:
              quest_arr = line.split('|')
              obj_c[i] = quest_arr[1]
              rewards = quest_arr[2]
        body += obj_c[i].encode('utf-8') + '|' + rewards.strip().encode('utf-8') + '  \n'    
    if ps4:
      body += '* *PS4 only*  \n'
    body += notes
    body += '''  \nLimited Bounties
============

Bounty|Conditions|Rewards
:-:|:-:|:-:
Ecology Survey: Hunt xxxxxxx | Hunt 3 specified monsters | Research Points, X x Armor Sphere
Ecology Survey: Hunt xxxxxxx | Hunt 4 specified monsters | Research Points, X x Armor Sphere+, First Wyverian Print
Ecology Survey: Tempered Monster Hunt | Slay 5 specified monsters | Research Points, X x Hard Armor Sphere, Silver Wyverian Print
General: Limited Bounty | Complete all limited bounties | Research Points, Gold Wyverian Print, Golden Egg  
  \n'''
  
  with open ("signature.txt", "r") as file:
    sig = file.read()  
  
  print body + sig
 
def process_quest(txt):
  if txt.strip() == "":
    return (False,False)
  if 'Available' in txt.strip():
    return (True,False)
  else:
    return (True,True)
  
def is_blue(color):
  blue1 = (0,30,90)
  blue2 = (10,40,100)
  for n in range(0,3):
    if not (blue1[n] <= color[n] <= blue2[n]):
      return False
  return True
  
def get_week(weeks):
  now = datetime.utcnow()
  for n in range(1,len(weeks)+1):
    date_txt = image_to_string(Image.open('images/week'+str(n)+'/date.jpg')).strip()
    dates = date_txt.encode('utf-8').split('\xe2\x80\x94')
    print dates
    start_txt = dates[0][5:].strip()
    end_txt = dates[1].strip()
    print start_txt, end_txt
    start = datetime.strptime(start_txt,'%m/%d %H:%M')
    start = start.replace(year=now.year)
    end = datetime.strptime(end_txt,'%m/%d %H:%M')
    end = end.replace(year=now.year)
    if start <= now <= end:
      return n
  return -1
  
  
def pdf_to_image(input, output):
  pdf = file(input, "rb").read()

  startmark = "\xff\xd8"
  startfix = 0
  endmark = "\xff\xd9"
  endfix = 2
  i = 0

  njpg = 0
  while True:
      istream = pdf.find("stream", i)
      if istream < 0:
          break
      istart = pdf.find(startmark, istream, istream+20)
      if istart < 0:
          i = istream+20
          continue
      iend = pdf.find("endstream", istart)
      if iend < 0:
          raise Exception("Didn't find end of stream!")
      iend = pdf.find(endmark, iend-20)
      if iend < 0:
          raise Exception("Didn't find end of JPG!")
       
      istart += startfix
      iend += endfix
      print "JPG %d from %d to %d" % (njpg, istart, iend)
      jpg = pdf[istart:iend]
      jpgfile = file(output, "wb")
      jpgfile.write(jpg)
      jpgfile.close()
       
      njpg += 1
      i = iend

def binarize_image(img_path, target_path, threshold=200):
    """Binarize an image."""
    image_file = Image.open(img_path)
    image = image_file.convert('L')  # convert image to monochrome
    image = numpy.array(image)
    image = binarize_array(image, threshold)
    imsave(target_path, image)


def binarize_array(numpy_array, threshold=200):
    """Binarize a numpy array."""
    for i in range(len(numpy_array)):
        for j in range(len(numpy_array[0])):
            if numpy_array[i][j] > threshold:
                numpy_array[i][j] = 255
            else:
                numpy_array[i][j] = 0
    return numpy_array

def string_to_list(str,ignore=[]):
  n = 0
  header = ""
  events = []
  challenges = []
  event = True
  temp = ""
  for line in str.encode('utf-8').splitlines():
    if n == 0:
      header = line.strip()
    elif line.strip() == "":
      pass
    elif line.strip() == header:
      event = not event
    elif line.strip()[-1] == ':':
      temp = line.strip() + ' '
    elif (line.strip() not in ignore):
      if event:
        events.append(temp + line.strip().replace('\xe2\x80\x94','-'))
        temp = ""
      else:
        challenges.append(temp + line.strip())
        temp = ""
    n = n + 1
  return (events,challenges)
        
if __name__ == '__main__':
    main()
