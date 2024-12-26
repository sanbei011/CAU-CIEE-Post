import requests, re, os
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template

# 获取信息
def fetch_announcements():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    url = 'https://ciee.cau.edu.cn/col/col50390/index.html'
    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        cdata_content = response.text
        time_matches = re.findall(r'<h3>(\d+)</h3>\s*<h6>(\d{4}-\d{2})</h6>', cdata_content)
        title_matches = re.findall(r'<h5 class="overfloat-dot">(.+?)</h5>', cdata_content)
        announcements = {}
        for i, (day, year_month) in enumerate(time_matches):
            full_date = f"{year_month}-{day}"
            announcements[full_date] = title_matches[i]

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
        return filtered_announcements
    except Exception as e:
        print(f"获取公告失败: {e}")
        return {}

# 发送邮件
def send_email(subject, body, recipient):
    SMTP_SERVER = 'smtp.qq.com'
    SMTP_PORT = 465
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, [recipient], msg.as_string())
        server.quit()
        print(f"邮件成功发送至 {recipient}")
    except Exception as e:
        print(f"邮件发送失败至 {recipient}: {e}")

def generate_html(filtered_announcements):
    template = Template("""
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>新闻摘要</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 20px;
            }
            .news-section {
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .news-section h2 {
                color: #333;
                margin-bottom: 10px;
            }
            .news-item {
                margin-bottom: 10px;
            }
            .news-item h3 {
                color: #007bff;
                margin-bottom: 5px;
            }
            .news-item p {
                color: #666;
                line-height: 1.6;
            }
        </style>
    </head>
    <body>
        <div class="news-section" id="today">
            <h2>今日CAU信电学院报</h2>
            {% if filtered_announcements.get('今天') %}
                {% for title in filtered_announcements['今天'] %}
                    <div class="news-item">
                        <h3>{{ title }}</h3>
                    </div>
                {% endfor %}
            {% else %}
                <h3>今天没有消息哦!</h3>
            {% endif %}
        </div>
        <div class="news-section" id="yesterday">
            <h2>昨日信电学院报</h2>
            {% if filtered_announcements.get('昨天') %}
                {% for title in filtered_announcements['昨天'] %}
                    <div class="news-item">
                        <h3>{{ title }}</h3>
                    </div>
                {% endfor %}
            {% else %}
                <h3>昨天没有消息哦!</h3>
            {% endif %}
        </div>
        <div class="news-section" id="day-before-yesterday">
            <h2>前日信电学院报</h2>
            {% if filtered_announcements.get('前天') %}
                {% for title in filtered_announcements['前天'] %}
                    <div class="news-item">
                        <h3>{{ title }}</h3>
                    </div>
                {% endfor %}
            {% else %}
                <h3>前日没有消息哦!</h3>
            {% endif %}
        </div>
    </body>
    </html>
    """)
    return template.render(filtered_announcements=filtered_announcements)

def main():
    filtered_announcements = fetch_announcements()
    if not filtered_announcements:
        print("没有新的公告。")
        return

    html_body = generate_html(filtered_announcements)
    subject = "中国农业大学信电学院新闻推送"
    send_email(subject, html_body, 'gzh031@foxmail.com')
    print("邮件发送成功！")

if __name__ == '__main__':
    main()