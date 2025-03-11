# Google Sheet Auto-Reply with Template Instruction
I wrote a well-subscribed Google Sheet ([link](https://www.reddit.com/r/AusFinance/s/VHJ25VpNKu) for those interested), unfortunately due to the limitation of Google Sheet it can only be used by end-user by "make a copy". Unfortunately despite clear instructions on the page, I continue to get plenty of "edit request" from interested users where I have to reject and provide instruction. 

Unfortunately both Google Sheet and GMail do not provide automatic response capabilities. While GMail allows filter-based automatic reply, the reply-to address for Google Sheet response defaults to drive-shares-dm-noreply@google.com rather than the actual requester's email. 

This Python script parses the standard request and extracts the email address (typically first word on the body), and send the templated response. 

## Instructions

1. You have to obtain an app password for your GMail account first. ([Instruction](https://support.google.com/mail/answer/185833?hl=en))

2. In **config.ini**, replace
   - your **password** with the _app-password_ (DO NOT use your actual password), and
   - **username** with your email address (_youremailaddress@gmail.com_)

4. In **autoreply.py**, replace
   - line 31 **TRIGGER SUBJECT** with the subject,
   - line 35 **auto_reply_text** with your own template email text,
   - line 57 **msg['Subject']** with the reply email subject,
   - line 151 **line.sleep(300)** with your preferred **interval in seconds**. 

6. Run the Python script on a suitable machine. I have mine running on RaspberryPi by adding the following line to **/etc/rc.local**. (The path is the folder where the script and config.ini are located)

   `cd /home/pi/Desktop/AutoReply && sudo python3 autoreply.py &`

## Usage

When properly set up, this script will:
- Automatically check your email every 5 minutes.
- Detect standard Google Sheet request email by matching the subject line.
- Correctly replies to the sender's email address with a canned response (instead of the incorrect reply-to email of Google Sheets). 
- Mark the sent email as read. 
