# ============================================================
# SHSD Link - School Communication System
# PART 4 : SSL Wireless SMS Service
# ============================================================

import uuid
import requests

from config import (
    SSL_WIRELESS_API_TOKEN,
    SSL_WIRELESS_SID,
    SSL_WIRELESS_SMS_URL,
    SMS_COUNTRY_CODE
)


# ============================================================
# MOBILE NUMBER CLEAN FUNCTION
# ============================================================

def clean_mobile_number(mobile):
    """
    Student-এর Mobile Number-কে SMS API-এর জন্য
    পরিষ্কার এবং standard format-এ নিয়ে আসে।

    উদাহরণ:

    01712345678
        ↓
    8801712345678

    +8801712345678
        ↓
    8801712345678
    """

    # --------------------------------------------------------
    # Mobile number না থাকলে
    # --------------------------------------------------------

    if not mobile:
        return None

    # --------------------------------------------------------
    # Space, dash, bracket ইত্যাদি সরানো
    # --------------------------------------------------------

    mobile = str(mobile).strip()

    mobile = (
        mobile
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    # --------------------------------------------------------
    # +880 দিয়ে শুরু হলে
    # --------------------------------------------------------

    if mobile.startswith("+880"):

        mobile = mobile[1:]

    # --------------------------------------------------------
    # 880 দিয়ে শুরু হলে
    # --------------------------------------------------------

    elif mobile.startswith("880"):

        pass

    # --------------------------------------------------------
    # 01 দিয়ে শুরু হলে
    # --------------------------------------------------------

    elif mobile.startswith("01"):

        mobile = (
            SMS_COUNTRY_CODE
            + mobile[1:]
        )

    # --------------------------------------------------------
    # শুধু 1 দিয়ে শুরু হলে
    # যেমন:
    #
    # 1712345678
    #
    # সেটাকে 8801712345678 করা হবে।
    # --------------------------------------------------------

    elif mobile.startswith("1"):

        mobile = (
            SMS_COUNTRY_CODE
            + mobile
        )

    # --------------------------------------------------------
    # অন্য কোনো format হলে
    # --------------------------------------------------------

    else:

        return None

    return mobile


# ============================================================
# MOBILE NUMBER VALIDATION
# ============================================================

def is_valid_mobile_number(mobile):
    """
    Mobile Number valid কিনা basic check করে।
    """

    cleaned = clean_mobile_number(mobile)

    if not cleaned:
        return False

    # Bangladesh-এর সাধারণ mobile number
    # 8801XXXXXXXXX format
    if len(cleaned) != 13:
        return False

    if not cleaned.startswith("8801"):
        return False

    return cleaned.isdigit()


# ============================================================
# API CONFIGURATION CHECK
# ============================================================

def is_sms_api_configured():
    """
    SSL Wireless API Token এবং SID দেওয়া আছে কিনা পরীক্ষা করে।

    API Key না থাকলে SMS পাঠানোর চেষ্টা করা হবে না।
    """

    return bool(
        SSL_WIRELESS_API_TOKEN
        and SSL_WIRELESS_SID
    )


# ============================================================
# CREATE CSMS ID
# ============================================================

def create_csms_id():
    """
    প্রত্যেক SMS request-এর জন্য একটি unique ID তৈরি করে।
    """

    return str(uuid.uuid4())


# ============================================================
# SEND SINGLE SMS
# ============================================================

def send_sms(
    mobile,
    message,
    csms_id=None
):
    """
    একজন Student-এর Mobile Number-এ SMS পাঠানোর Function।

    Parameters:

        mobile
            → Student-এর mobile number

        message
            → যে SMS পাঠানো হবে

        csms_id
            → SMS-এর unique ID

    Return:

        Dictionary আকারে result ফেরত দেবে।
    """

    # --------------------------------------------------------
    # Mobile Number পরিষ্কার করা
    # --------------------------------------------------------

    mobile = clean_mobile_number(mobile)

    # --------------------------------------------------------
    # Mobile Number valid কিনা
    # --------------------------------------------------------

    if not mobile:

        return {
            "success": False,
            "status": "failed",
            "message": "Invalid mobile number",
            "response": None
        }

    # --------------------------------------------------------
    # Message খালি কিনা
    # --------------------------------------------------------

    if not message:

        return {
            "success": False,
            "status": "failed",
            "message": "SMS message is empty",
            "response": None
        }

    # --------------------------------------------------------
    # SSL Wireless API configuration আছে কিনা
    # --------------------------------------------------------

    if not is_sms_api_configured():

        return {
            "success": False,
            "status": "failed",
            "message": (
                "SSL Wireless API is not configured yet."
            ),
            "response": None
        }

    # --------------------------------------------------------
    # CSMS ID না থাকলে নতুন তৈরি করা
    # --------------------------------------------------------

    if not csms_id:

        csms_id = create_csms_id()

    # --------------------------------------------------------
    # SSL Wireless API Request Data
    # --------------------------------------------------------
    #
    # API credential Python backend-এ থাকবে।
    # Browser / HTML / JavaScript-এ যাবে না।
    # --------------------------------------------------------

    payload = {
        "api_token": SSL_WIRELESS_API_TOKEN,
        "sid": SSL_WIRELESS_SID,
        "msisdn": mobile,
        "sms": message,
        "csms_id": csms_id
    }

    # --------------------------------------------------------
    # HTTP Headers
    # --------------------------------------------------------

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # --------------------------------------------------------
    # API Request
    # --------------------------------------------------------

    try:

        response = requests.post(
            SSL_WIRELESS_SMS_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        # ----------------------------------------------------
        # Response Text
        # ----------------------------------------------------

        response_text = response.text

        # ----------------------------------------------------
        # JSON Response হলে JSON হিসেবে নেওয়া
        # ----------------------------------------------------

        try:

            response_data = response.json()

        except ValueError:

            response_data = {
                "raw_response": response_text
            }

        # ----------------------------------------------------
        # HTTP Status Code check
        # ----------------------------------------------------

        if 200 <= response.status_code < 300:

            return {
                "success": True,
                "status": "success",
                "message": "SMS request sent successfully.",
                "response": response_data,
                "csms_id": csms_id
            }

        # ----------------------------------------------------
        # API Error
        # ----------------------------------------------------

        return {
            "success": False,
            "status": "failed",
            "message": (
                "SSL Wireless API returned an error."
            ),
            "response": response_data,
            "http_status": response.status_code,
            "csms_id": csms_id
        }

    # --------------------------------------------------------
    # Internet / Connection Error
    # --------------------------------------------------------

    except requests.exceptions.Timeout:

        return {
            "success": False,
            "status": "failed",
            "message": (
                "SMS API request timed out."
            ),
            "response": None,
            "csms_id": csms_id
        }

    except requests.exceptions.ConnectionError:

        return {
            "success": False,
            "status": "failed",
            "message": (
                "Could not connect to SSL Wireless."
            ),
            "response": None,
            "csms_id": csms_id
        }

    # --------------------------------------------------------
    # অন্য যেকোনো Error
    # --------------------------------------------------------

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "status": "failed",
            "message": (
                "SMS request failed."
            ),
            "response": str(error),
            "csms_id": csms_id
        }

    except Exception as error:

        return {
            "success": False,
            "status": "failed",
            "message": (
                "Unexpected SMS error."
            ),
            "response": str(error),
            "csms_id": csms_id
        }


# ============================================================
# SEND SMS TO MULTIPLE STUDENTS
# ============================================================

def send_bulk_sms(
    students,
    message
):
    """
    একাধিক Student-এর কাছে SMS পাঠানোর Function।

    students-এর মধ্যে প্রত্যেক Student-এর:

        student.mobile

    ব্যবহার করা হবে।

    Return:

        total
        success
        failed
        results

    """

    # --------------------------------------------------------
    # Message validation
    # --------------------------------------------------------

    if not message:

        return {
            "total": 0,
            "success": 0,
            "failed": 0,
            "results": [],
            "message": "SMS message is empty."
        }

    # --------------------------------------------------------
    # Student list খালি কিনা
    # --------------------------------------------------------

    if not students:

        return {
            "total": 0,
            "success": 0,
            "failed": 0,
            "results": [],
            "message": "No students found."
        }

    # --------------------------------------------------------
    # Result List
    # --------------------------------------------------------

    results = []

    successful_count = 0

    failed_count = 0

    # --------------------------------------------------------
    # প্রত্যেক Student-এর জন্য SMS পাঠানো
    # --------------------------------------------------------

    for student in students:

        result = send_sms(
            mobile=student.mobile,
            message=message
        )

        # ----------------------------------------------------
        # Result-এর সঙ্গে Student information যোগ করা
        # ----------------------------------------------------

        student_result = {
            "student_id": student.id,
            "student_name": student.name,
            "mobile": student.mobile,
            "success": result.get("success", False),
            "status": result.get(
                "status",
                "failed"
            ),
            "message": result.get(
                "message",
                ""
            ),
            "response": result.get(
                "response"
            )
        }

        results.append(student_result)

        # ----------------------------------------------------
        # Success / Failed count
        # ----------------------------------------------------

        if result.get("success"):

            successful_count += 1

        else:

            failed_count += 1

    # --------------------------------------------------------
    # Final Result
    # --------------------------------------------------------

    return {
        "total": len(students),
        "success": successful_count,
        "failed": failed_count,
        "results": results,
        "message": (
            f"{successful_count} SMS sent successfully, "
            f"{failed_count} failed."
        )
    }


# ============================================================
# TEST SMS FUNCTION
# ============================================================
# ভবিষ্যতে Admin Dashboard থেকে API Test করার জন্য
# এই Function ব্যবহার করা যাবে।
# ============================================================

def test_sms_configuration(
    mobile,
    message="SHSD Link SMS Test"
):
    """
    SSL Wireless configuration ঠিকমতো কাজ করছে কিনা
    পরীক্ষা করার জন্য একটি Test SMS পাঠায়।
    """

    return send_sms(
        mobile=mobile,
        message=message
    )


# ============================================================
# SMS SERVICE INFORMATION
# ============================================================

def get_sms_service_status():
    """
    Admin Dashboard-এ SMS Service-এর status দেখানোর জন্য।
    """

    configured = is_sms_api_configured()

    return {
        "configured": configured,
        "service": "SSL Wireless",
        "api_url": SSL_WIRELESS_SMS_URL
    }