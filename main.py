import requests,json,re,os
from datetime import datetime, timedelta
from flask import Flask, render_template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# 获取信息
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
url = 'https://ciee.cau.edu.cn/col/col50390/index.html'
response = requests.get(url, headers=headers)
response.encoding = response.apparent_encoding
cdata_content = response.text
time_matches = re.findall(r'<h3>(\d+)</h3>\s*<h6>(\d{4}-\d{2})</h6>', cdata_content)
title_matches = re.findall(r'<h5 class="overfloat-dot">(.+?)</h5>', cdata_content)
announcements = {}
for i, (day, year_month) in enumerate(time_matches):
    full_date = f"{year_month}-{day}"
    announcements[full_date] = title_matches[i]


# today = datetime(2024, 3， 17)
today = datetime.now().date()
filtered_announcements = {}
for full_date, title in announcements.items():
    date = datetime.strptime(full_date, "%Y-%m-%d").date()
    if date == today:
        key = "今天"
    elif date == today - timedelta(days=1):
        key = "昨天"
    elif date == today - timedelta(days=2):
        key = "前天"
    else:
        continue
    if key not in filtered_announcements:
        filtered_announcements[key] = [title]
    else:
        filtered_announcements[key].append(title)
# print(filtered_announcements)


app = Flask(__name__)


SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 465
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
recipients = ['gzh031@foxmail.com', '1796987794@qq.com']


def send_email(subject, body, recipient):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    server.sendmail(SMTP_USERNAME, [recipient], msg.as_string())
    server.quit()

# Flask 路由，用于发送邮件
@app.route('/send-announcements')
def send_announcements():
    html_body = render_template('model.html', filtered_announcements=filtered_announcements)
    # print(html_body)
    for recipient in recipients:
        send_email(subject, html_body, recipient)
    return today.strftime("%Y-%m-%d")

if __name__ == '__main__':
    app.run(debug=True)
