# reminder for self: windows task scheduled with wiki-news.bat under 

import datetime
from dotenv import load_dotenv
import json
import requests
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import re

load_dotenv()

###############################################################################################################################################################
# boiler plate borrowed from WikiMedia's tutorial
today = datetime.datetime.now()
date = today.strftime('%Y/%m/%d')

language_code = 'en' # which language's wiki
headers = {
  'Authorization': f'Bearer {os.environ["WIKIMEDIA_API_KEY"]}',
  'User-Agent': 'email-day (brushnit.online@gmail.com)'
}

base_url = 'https://api.wikimedia.org/feed/v1/wikipedia/'
url = base_url + language_code + '/featured/' + date
response = requests.get(url, headers=headers)

headlines = []

response = json.loads(response.text)

for story in response['news']:
  headline = story['story']
  # Replace relative URLs with absolute URLs
  headline = headline.replace('"./', '"https://' + language_code + '.wikipedia.org/wiki/')
  headlines.append(headline)

###############################################################################################################################################################
# function to format HTML response; can be modified to
def create_headlines_html(headlines_list, date):
    html_output = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wikipedia Headlines {date}</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f9f9f9;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f9f9f9;">
        <tr>
            <td align="center">
                <table width="600" border="0" cellspacing="0" cellpadding="20" style="max-width: 600px; width: 100%; background-color: #ffffff; border-radius: 8px; margin-top: 20px; margin-bottom: 20px;">
                    <tr>
                        <td>
                            <h1 style="font-size: 24px; color: #333333; margin-top: 0;">Wikinews for {date}</h1>
                            <ul style="list-style-type: none; padding: 0; margin: 0;">
    """

    for index, headline in enumerate(headlines_list):
        cleaned_headline = re.sub(r'<!--.*?-->', '', headline)

        def clean_anchor_tag(match):
            tag = match.group(0)
            href_match = re.search(r'href="([^"]+)"', tag)
            if href_match:
                href = href_match.group(1)
                content = re.sub(r'<.*?>', '', tag)
                return f'<a href="{href}" style="color: #0066cc; text-decoration: none;">{content}</a>'
            return tag 

        anchors = re.findall(r'<a[^>]*>.*?</a>', cleaned_headline)
        for anchor in anchors:
            cleaned_anchor = clean_anchor_tag(re.match(r'.*', anchor)) 
            cleaned_headline = cleaned_headline.replace(anchor, cleaned_anchor, 1)

        border_style = "border-bottom: 1px solid #eeeeee;" if index < len(headlines_list) - 1 else ""
        html_output += f"""
                                <li style="padding: 15px 0; font-size: 16px; color: #555555; {border_style}">
                                    {cleaned_headline.strip()}
                                </li>
        """
    
    html_output += """
                            </ul>

                            <!-- More Current Events Link -->
                            <p style="text-align: center; margin-top: 20px;">
                                <a href="https://en.wikipedia.org/wiki/Portal:Current_events" style="color: #0066cc; text-decoration: none; font-size: 16px;">More Current Events</a>
                            </p>

                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>

</body>
</html>
    """
    return html_output

###############################################################################################################################################################
# send email
message = Mail(
    from_email="dabcrc@umsystem.edu",
    to_emails="dabcrc@umsystem.edu",
    subject=f'Wiki News for {date}',
    html_content=create_headlines_html(headlines, date),
)
try:
    sg = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(str(e))