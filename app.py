from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import random
import smtplib
import time
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# আপনার জিমেইল এবং অ্যাপ পাসওয়ার্ড (নিরাপত্তার জন্য Environment Variable-ও ব্যবহার করতে পারেন)
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "income2007.20@gmail.com")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "izou sxyc kgot dcfz")

registration_store = {}


@app.route("/", methods=["GET"])
def home():
  return jsonify({
      "success": True,
      "message": "KS Gaming SHOP API is running successfully!",
  })


@app.route("/api/register-request-otp", methods=["POST"])
def register_request_otp():
  data = request.get_json() or {}
  email = data.get("email")
  password = data.get("password")

  if not email or not password:
    return (
        jsonify(
            {"success": False, "message": "Email and password are required."}
        ),
        400,
    )

  otp = str(random.randint(100000, 999999))
  expires_at = time.time() + 600  # ১০ মিনিট মেয়াদ

  registration_store[email] = {
      "otp": otp,
      "expires_at": expires_at,
      "password": password,
  }

  message = MIMEMultipart("alternative")
  message["Subject"] = f"Your KS Gaming SHOP security code: {otp}"
  message["From"] = f"KS Gaming SHOP <{SENDER_EMAIL}>"
  message["To"] = email

  # ভার্সেলের মতো প্রিমিয়াম ডিজাইন এবং KS Gaming SHOP ব্র্যান্ডিং
  html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #0f172a;
                margin: 0;
                padding: 40px 0;
                color: #f3f4f6;
            }}
            .email-wrapper {{
                width: 100%;
                table-layout: fixed;
                background-color: #0f172a;
                padding: 20px 0;
            }}
            .email-content {{
                max-width: 480px;
                margin: 0 auto;
                background: linear-gradient(135deg, #1e1b4b 0%, #311045 100%);
                border-radius: 20px;
                padding: 40px 30px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            h1 {{
                font-size: 24px;
                margin: 0 0 15px 0;
                font-weight: 800;
                letter-spacing: 1px;
                color: #ffffff;
            }}
            p {{
                color: #9ca3af;
                font-size: 14px;
                line-height: 1.6;
                margin-bottom: 25px;
            }}
            .otp-box {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 25px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .otp-label {{
                font-size: 12px;
                color: #38bdf8;
                text-transform: uppercase;
                letter-spacing: 2px;
                margin-bottom: 10px;
                font-weight: 600;
            }}
            .otp-code {{
                font-size: 40px;
                font-weight: 800;
                letter-spacing: 10px;
                color: #38bdf8;
                margin-left: 10px;
            }}
            .copy-btn {{
                background: #ffffff;
                color: #1e1b4b;
                text-decoration: none;
                padding: 13px 32px;
                font-size: 15px;
                font-weight: bold;
                border-radius: 10px;
                display: inline-block;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            }}
            .footer-text {{
                margin-top: 30px;
                color: #6b7280;
                font-size: 12px;
                margin-bottom: 0;
            }}
        </style>
    </head>
    <body>
        <table class="email-wrapper" width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td align="center">
                    <div class="email-content">
                        <h1>KS Gaming SHOP</h1>
                        <p>We received a request to verify your email for your KS Gaming SHOP account. Use the security code below:</p>
                        
                        <div class="otp-box">
                            <div class="otp-label">Code Requested</div>
                            <div class="otp-code">{otp}</div>
                        </div>

                        <a href="https://api.whatsapp.com/send?text={otp}" class="copy-btn" target="_blank">Copy code</a>

                        <p class="footer-text">This code expires in 10 minutes. If you did not request this, you can safely ignore this email.</p>
                    </div>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
  message.attach(MIMEText(html, "html"))

  try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
      server.login(SENDER_EMAIL, SENDER_PASSWORD)
      server.sendmail(SENDER_EMAIL, email, message.as_string())
    return jsonify({"success": True, "message": "Verification code sent!"})
  except Exception as e:
    return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/register-verify-otp", methods=["POST"])
def register_verify_otp():
  data = request.get_json() or {}
  email = data.get("email")
  user_otp = data.get("otp")

  record = registration_store.get(email)

  if not record:
    return jsonify({"success": False, "message": "Request not found."}), 400

  if time.time() > record["expires_at"]:
    del registration_store[email]
    return jsonify({"success": False, "message": "OTP expired."}), 400

  if record["otp"] == str(user_otp):
    del registration_store[email]
    return jsonify({"success": True, "message": "Account created successfully!"})
  else:
    return jsonify({"success": False, "message": "Invalid OTP."}), 400


if __name__ == "__main__":
  app.run(debug=True, port=5000)
