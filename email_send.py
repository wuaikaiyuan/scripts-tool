import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# 设置邮箱服务器
smtp_server_global = 'smtp.126.com'

def send_email(sender_email, sender_password, receiver_email, subject, body, attachment=None):
    # 设置邮箱服务器
    smtp_server = smtp_server_global  # 根据你的邮箱提供商设置

    # 创建一个 MIMEMultipart 对象来组合邮件内容
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # 添加邮件正文
    msg.attach(MIMEText(body, 'plain'))

    # 添加附件（如果有）
    if attachment:
        with open(attachment, 'rb') as file:
            part = MIMEApplication(file.read())
            part.add_header('Content-Disposition', 'attachment', filename=attachment)
        msg.attach(part)

    # 连接到邮箱服务器并发送邮件
    with smtplib.SMTP_SSL(host=smtp_server, port=smtplib.SMTP_SSL_PORT) as server:
        # server.starttls()  # 开启 TLS 加密
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

# 设置发送者和接收者的邮箱地址以及授权密码
sender_email = '[Your Send Email]'
sender_password = os.environ.get("AUTH_EMAIL_PASSWORD")
receiver_email = '[Receiver Email]'

# 设置邮件主题和内容
subject = 'Daily Report'
body = 'This is your daily report. Have a nice day!'

# 发送邮件
send_email(sender_email, sender_password, receiver_email, subject, body)
