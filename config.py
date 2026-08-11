# ============================================================
# SHSD Link - School Communication System
# PART 2 : Configuration File
# ============================================================

import os
from pathlib import Path


# ------------------------------------------------------------
# এই ফাইলটি যেখানে আছে, সেটাকেই আমাদের Project Folder ধরা হবে
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent


# ------------------------------------------------------------
# Database Configuration
# ------------------------------------------------------------
# আমরা SQLite Database ব্যবহার করছি।
# Database-এর নাম হবে shsd_link.db
#
# পরবর্তীতে Student, Teacher, Admin, Chat Message,
# Request Form ইত্যাদি এই Database-এ সংরক্ষণ করা হবে।
# ------------------------------------------------------------

DATABASE_FILE = BASE_DIR / "shsd_link.db"

DATABASE_URL = "sqlite:///" + str(DATABASE_FILE)


# ------------------------------------------------------------
# Flask Secret Key
# ------------------------------------------------------------
# Login session এবং নিরাপদ session management-এর জন্য
# এই Secret Key ব্যবহার হবে।
#
# Environment variable থাকলে সেটি ব্যবহার করবে।
# না থাকলে নিচের default key ব্যবহার করবে।
# ------------------------------------------------------------

SECRET_KEY = os.environ.get(
    "SHSD_SECRET_KEY",
    "SHSD-Link-School-Secret-Key-2026-Change-Later"
)


# ------------------------------------------------------------
# Website Information
# ------------------------------------------------------------

SCHOOL_NAME = "SHSD Link"

SCHOOL_TAGLINE = "School Communication & Student Management System"

SCHOOL_SHORT_NAME = "SHSD"


# ------------------------------------------------------------
# Flask Configuration
# ------------------------------------------------------------

DEBUG_MODE = True


# ------------------------------------------------------------
# SocketIO Configuration
# ------------------------------------------------------------
# Public Text Chat-এর Real-Time Message System-এর জন্য
# Flask-SocketIO ব্যবহার করা হবে।
# ------------------------------------------------------------

SOCKETIO_ASYNC_MODE = "eventlet"


# ------------------------------------------------------------
# SSL Wireless SMS Configuration
# ------------------------------------------------------------
#
# IMPORTANT:
# এখানে এখন তোমার API Key লিখতে হবে না।
#
# পরবর্তীতে আমরা Environment Variable ব্যবহার করব।
# এতে API Key website-এর HTML/JavaScript-এর মধ্যে
# প্রকাশ পাবে না।
#
# SSL Wireless-এর API Token এবং SID পরবর্তীতে
# আলাদা Environment Variable থেকে নেওয়া হবে।
# ------------------------------------------------------------

SSL_WIRELESS_API_TOKEN = os.environ.get(
    "SSL_WIRELESS_API_TOKEN",
    ""
)

SSL_WIRELESS_SID = os.environ.get(
    "SSL_WIRELESS_SID",
    ""
)


# ------------------------------------------------------------
# SSL Wireless SMS API URL
# ------------------------------------------------------------

SSL_WIRELESS_SMS_URL = (
    "https://smsplus.sslwireless.com/api/v3/send-sms"
)


# ------------------------------------------------------------
# SMS Sender / Application Information
# ------------------------------------------------------------
# এগুলো SMS Service তৈরি করার সময় প্রয়োজন অনুযায়ী ব্যবহার হবে।
# ------------------------------------------------------------

SMS_COUNTRY_CODE = "880"


# ------------------------------------------------------------
# Default Admin Account
# ------------------------------------------------------------
#
# প্রথমবার Website চালু হলে Database-এ একটি Default Admin
# Account তৈরি করার ব্যবস্থা আমরা পরের Part-এ করব।
#
# এখানে শুধু Default Information রাখা হচ্ছে।
#
# SECURITY NOTE:
# Production Website-এ অবশ্যই এই password পরিবর্তন করতে হবে।
# ------------------------------------------------------------

DEFAULT_ADMIN_NAME = "School Admin"

DEFAULT_ADMIN_USERNAME = "admin"

DEFAULT_ADMIN_PASSWORD = "admin12345"

DEFAULT_ADMIN_ROLE = "admin"


# ------------------------------------------------------------
# User Roles
# ------------------------------------------------------------
# Website-এ প্রধানত তিন ধরনের User থাকবে।
# ------------------------------------------------------------

ROLE_ADMIN = "admin"

ROLE_TEACHER = "teacher"

ROLE_STUDENT = "student"


# ------------------------------------------------------------
# Chat Configuration
# ------------------------------------------------------------

# Public Chat-এ সর্বোচ্চ কত অক্ষরের message পাঠানো যাবে
MAX_CHAT_MESSAGE_LENGTH = 500


# ------------------------------------------------------------
# Student Request Configuration
# ------------------------------------------------------------

# Student/Teacher registration বা request form-এর
# প্রয়োজনীয় fieldগুলো ভবিষ্যতে এখান থেকে নিয়ন্ত্রণ করা যাবে।
REQUEST_FORM_ENABLED = True


# ------------------------------------------------------------
# Application Settings
# ------------------------------------------------------------

APP_VERSION = "1.0.0"

APP_LANGUAGE = "bn"

APP_TIMEZONE = "Asia/Dhaka"


# ------------------------------------------------------------
# Security Configuration
# ------------------------------------------------------------

# Login করার পর session কতক্ষণ মনে রাখা হবে।
# Flask session-এর জন্য ব্যবহার করা হবে।
SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = "Lax"

# HTTPS চালু করার পর এটি True করা যাবে।
# এখন Localhost development-এর জন্য False রাখা হয়েছে।
SESSION_COOKIE_SECURE = False


# ------------------------------------------------------------
# File Upload Configuration
# ------------------------------------------------------------
# ভবিষ্যতে Profile Photo / School Logo ইত্যাদি
# upload করার প্রয়োজন হলে এই folder ব্যবহার করা যাবে।
# ------------------------------------------------------------

UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


# ------------------------------------------------------------
# Folder তৈরি করার Function
# ------------------------------------------------------------
# Project চালু হলে প্রয়োজনীয় folder না থাকলে
# Python নিজে তৈরি করে নেবে।
# ------------------------------------------------------------

def create_required_folders():
    """
    Website-এর প্রয়োজনীয় folder তৈরি করে।
    """

    UPLOAD_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )


# ------------------------------------------------------------
# Configuration Check Function
# ------------------------------------------------------------
# Website চালু হওয়ার সময় configuration ঠিক আছে কিনা
# পরীক্ষা করার জন্য এই function ব্যবহার করা হবে।
# ------------------------------------------------------------

def check_configuration():
    """
    প্রয়োজনীয় configuration-এর basic status check করে।
    """

    create_required_folders()

    return {
        "school_name": SCHOOL_NAME,
        "database": str(DATABASE_FILE),
        "sms_api_configured": bool(
            SSL_WIRELESS_API_TOKEN
            and SSL_WIRELESS_SID
        ),
        "version": APP_VERSION
    }