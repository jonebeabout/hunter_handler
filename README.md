# Hunter Handler
*A Reddit bot to create informative Monster Hunter posts*

Licensed under the MIT License.

## Patch Notes Poster
* Scrapes monsterhunterworld.com for new patch notes
* Formats html to reddit markdown
* Posts updates to /r/monsterhunter

## Future Updates

### Weekly Reset Post
Post will include: 
* Weekly event quests from monsterhunterworld.com
* Limited bounties
* Collection of useful PSAs from the previous week

### Links to Gear Pages in Comments
* Commenter posts gear in a certain format
* Bot will reply with link to kiranico gear page

## How to Contribute

### I'm not a developer
* Direct Message the bot on Reddit
* Post an issue on github for feature requests or bugs

### I'm a developer
* Direct Message the bot on Reddit with a request to be a contributor
* Create a pull request

## How to Modify for Your Own Reddit Bot
1. Install latest python 2.7 distribution
2. Install praw  
`pip install praw`
3. Create a personal script under a reddit user https://www.reddit.com/prefs/apps/
4. Modify praw_example.ini with credential details and rename to praw.ini
5. Modify patch_notes.py for your own purposes

*Currently, the bot is split into different functions, each with different Windows Scheduled Tasks.  Future updates will require different sections to always be running (i.e. python built in sleep functions).*

