"""
Тест SMTP-підключення та відправки через Brevo.
Запустити: python test_smtp.py
"""
import smtplib
import sys
import os

# Вручну встановлюємо змінні (щоб не залежати від .env при запуску поза app)
SMTP_HOST     = "smtp-relay.brevo.com"
SMTP_PORT     = 587
SMTP_USER     = "aa01a6001@smtp-brevo.com"
SMTP_PASSWORD = "fQbNJzjA10CtXTrM"
SMTP_FROM     = "anubis.develop@gmail.com"
RECIPIENT     = "yuzko.s@gmail.com"

print(f"[1] З'єднання з {SMTP_HOST}:{SMTP_PORT}...")
try:
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
    code, msg = server.ehlo()
    print(f"    EHLO: {code} {msg.decode()[:80]}")

    print("[2] STARTTLS...")
    server.starttls()
    print("    OK")

    print(f"[3] Логін як {SMTP_USER!r}...")
    server.login(SMTP_USER, SMTP_PASSWORD)
    print("    OK")

    print(f"[4] Відправка тестового листа від {SMTP_FROM!r} до {RECIPIENT!r}...")
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart()
    msg["From"]    = SMTP_FROM
    msg["To"]      = RECIPIENT
    msg["Subject"] = "✅ SMTP тест — Store Check"
    msg.attach(MIMEText(
        "Це тестовий лист від системи Store Check.\n"
        "Якщо ви бачите цей лист — SMTP налаштовано правильно! 🎉",
        "plain", "utf-8"
    ))

    refused = server.sendmail(SMTP_FROM, [RECIPIENT], msg.as_string())
    if refused:
        print(f"    ⚠️  Відхилені отримувачі: {refused}")
    else:
        print(f"    ✅ Відправлено успішно!")

    server.quit()
    print("\n✅ Все ОК — перевіряйте вхідні листи (і папку Спам).")

except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ Помилка автентифікації: {e}")
    print("   Перевірте SMTP_USER та SMTP_PASSWORD у Brevo.")
    sys.exit(1)
except smtplib.SMTPRecipientsRefused as e:
    print(f"\n❌ Отримувача відхилено: {e}")
    print("   Перевірте чи підтверджено адресу відправника у Brevo.")
    sys.exit(1)
except smtplib.SMTPSenderRefused as e:
    print(f"\n❌ Відправника відхилено: {e}")
    print("   Adresa {SMTP_FROM!r} не верифікована у Brevo акаунті!")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Помилка: {type(e).__name__}: {e}")
    sys.exit(1)
