# ============================================================
# SHSD Link - School Communication System
# PART 3 : Database System
# ============================================================

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


# ------------------------------------------------------------
# SQLAlchemy Database Object
# ------------------------------------------------------------
# এই object-টির মাধ্যমে আমাদের Flask Website-এর সাথে
# SQLite Database-এর connection তৈরি হবে।
#
# app.py থেকে পরে:
#
#     db.init_app(app)
#
# করা হবে।
# ------------------------------------------------------------

db = SQLAlchemy()


# ============================================================
# USER MODEL
# ============================================================
# এই Table-এ Admin, Teacher এবং Student — তিন ধরনের User
# সংরক্ষণ করা হবে।
# ============================================================

class User(db.Model):

    # Database Table-এর নাম
    __tablename__ = "users"

    # --------------------------------------------------------
    # Primary Key
    # --------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # --------------------------------------------------------
    # User-এর নাম
    # --------------------------------------------------------

    name = db.Column(
        db.String(120),
        nullable=False
    )

    # --------------------------------------------------------
    # Login Username
    # --------------------------------------------------------

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # Password সরাসরি Database-এ রাখা হবে না।
    # Password Hash করে রাখা হবে।
    # --------------------------------------------------------

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    # --------------------------------------------------------
    # User Role
    #
    # admin
    # teacher
    # student
    # --------------------------------------------------------

    role = db.Column(
        db.String(20),
        nullable=False,
        default="student"
    )

    # --------------------------------------------------------
    # Mobile Number
    # --------------------------------------------------------

    mobile = db.Column(
        db.String(30),
        nullable=True
    )

    # --------------------------------------------------------
    # Email
    # --------------------------------------------------------

    email = db.Column(
        db.String(120),
        nullable=True
    )

    # --------------------------------------------------------
    # Student-এর Class
    # Teacher/Admin-এর জন্য এটি খালি থাকতে পারে।
    # --------------------------------------------------------

    student_class = db.Column(
        db.String(50),
        nullable=True
    )

    # --------------------------------------------------------
    # Student Roll
    # --------------------------------------------------------

    roll = db.Column(
        db.String(50),
        nullable=True
    )

    # --------------------------------------------------------
    # Account Active কিনা
    # --------------------------------------------------------

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # --------------------------------------------------------
    # Account তৈরি হওয়ার সময়
    # --------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # --------------------------------------------------------
    # User-এর সর্বশেষ update time
    # --------------------------------------------------------

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # --------------------------------------------------------
    # Password Set করার Function
    # --------------------------------------------------------

    def set_password(self, password):
        """
        Password-কে নিরাপদ Hash-এ পরিবর্তন করে Database-এ রাখে।
        """

        self.password_hash = generate_password_hash(
            password
        )

    # --------------------------------------------------------
    # Password Check করার Function
    # --------------------------------------------------------

    def check_password(self, password):
        """
        Login করার সময় দেওয়া password সঠিক কিনা পরীক্ষা করে।
        """

        return check_password_hash(
            self.password_hash,
            password
        )

    # --------------------------------------------------------
    # Flask-Login-এর জন্য User ID
    # --------------------------------------------------------

    def get_id(self):
        """
        Flask-Login এই ID ব্যবহার করে User-এর session
        চিনতে পারবে।
        """

        return str(self.id)

    # --------------------------------------------------------
    # Admin কিনা
    # --------------------------------------------------------

    def is_admin(self):
        return self.role == "admin"

    # --------------------------------------------------------
    # Teacher কিনা
    # --------------------------------------------------------

    def is_teacher(self):
        return self.role == "teacher"

    # --------------------------------------------------------
    # Student কিনা
    # --------------------------------------------------------

    def is_student(self):
        return self.role == "student"

    # --------------------------------------------------------
    # সহজে User-এর নাম দেখানোর জন্য
    # --------------------------------------------------------

    def __repr__(self):
        return f"<User {self.username} - {self.role}>"


# ============================================================
# PUBLIC CHAT MESSAGE MODEL
# ============================================================
# Public Text Chat-এর সকল Message এখানে সংরক্ষণ হবে।
# ============================================================

class ChatMessage(db.Model):

    __tablename__ = "chat_messages"

    # --------------------------------------------------------
    # Message ID
    # --------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # --------------------------------------------------------
    # যে User Message পাঠিয়েছে তার ID
    # --------------------------------------------------------

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # Sender-এর নাম
    # --------------------------------------------------------
    # User delete হলেও পুরোনো chat-এর sender name
    # যেন হারিয়ে না যায়, তাই এখানে নামও রাখা হচ্ছে।
    # --------------------------------------------------------

    sender_name = db.Column(
        db.String(120),
        nullable=False
    )

    # --------------------------------------------------------
    # Sender-এর Role
    # --------------------------------------------------------

    sender_role = db.Column(
        db.String(20),
        nullable=False
    )

    # --------------------------------------------------------
    # আসল Message
    # --------------------------------------------------------

    message = db.Column(
        db.Text,
        nullable=False
    )

    # --------------------------------------------------------
    # Message পাঠানোর সময়
    # --------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # User Relationship
    # --------------------------------------------------------

    user = db.relationship(
        "User",
        backref=db.backref(
            "chat_messages",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<ChatMessage {self.id}>"


# ============================================================
# ADMIN BROADCAST MODEL
# ============================================================
# Admin যখন সকল Student-এর Mobile Number-এ SMS পাঠাবে,
# সেই Broadcast-এর তথ্য এখানে সংরক্ষণ হবে।
# ============================================================

class BroadcastMessage(db.Model):

    __tablename__ = "broadcast_messages"

    # --------------------------------------------------------
    # Broadcast ID
    # --------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # --------------------------------------------------------
    # যে Admin Broadcast করেছে
    # --------------------------------------------------------

    admin_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # --------------------------------------------------------
    # Admin-এর নাম
    # --------------------------------------------------------

    admin_name = db.Column(
        db.String(120),
        nullable=False
    )

    # --------------------------------------------------------
    # Broadcast Message
    # --------------------------------------------------------

    message = db.Column(
        db.Text,
        nullable=False
    )

    # --------------------------------------------------------
    # মোট কতজন Student-কে SMS পাঠানোর চেষ্টা হয়েছে
    # --------------------------------------------------------

    total_recipients = db.Column(
        db.Integer,
        default=0
    )

    # --------------------------------------------------------
    # কতজনের SMS সফল হয়েছে
    # --------------------------------------------------------

    successful_count = db.Column(
        db.Integer,
        default=0
    )

    # --------------------------------------------------------
    # কতজনের SMS ব্যর্থ হয়েছে
    # --------------------------------------------------------

    failed_count = db.Column(
        db.Integer,
        default=0
    )

    # --------------------------------------------------------
    # API Response
    # --------------------------------------------------------
    # Debug / future report-এর জন্য রাখা হচ্ছে।
    # --------------------------------------------------------

    api_response = db.Column(
        db.Text,
        nullable=True
    )

    # --------------------------------------------------------
    # Broadcast-এর সময়
    # --------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # --------------------------------------------------------
    # Admin Relationship
    # --------------------------------------------------------

    admin = db.relationship(
        "User",
        backref=db.backref(
            "broadcast_messages",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<BroadcastMessage {self.id}>"


# ============================================================
# SMS LOG MODEL
# ============================================================
# প্রত্যেক Student-এর SMS পাঠানোর আলাদা record রাখা হবে।
#
# যেমন:
#
# Student A → SUCCESS
# Student B → SUCCESS
# Student C → FAILED
#
# এতে পরে Admin দেখতে পারবে কার কাছে SMS গেছে।
# ============================================================

class SMSLog(db.Model):

    __tablename__ = "sms_logs"

    # --------------------------------------------------------
    # SMS Log ID
    # --------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # --------------------------------------------------------
    # কোন Broadcast-এর অংশ ছিল
    # --------------------------------------------------------

    broadcast_id = db.Column(
        db.Integer,
        db.ForeignKey("broadcast_messages.id"),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # Student-এর User ID
    # --------------------------------------------------------

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # Student-এর নাম
    # --------------------------------------------------------

    student_name = db.Column(
        db.String(120),
        nullable=False
    )

    # --------------------------------------------------------
    # যে Mobile Number-এ SMS পাঠানো হয়েছে
    # --------------------------------------------------------

    mobile = db.Column(
        db.String(30),
        nullable=False
    )

    # --------------------------------------------------------
    # SMS Status
    #
    # pending
    # success
    # failed
    # --------------------------------------------------------

    status = db.Column(
        db.String(20),
        default="pending",
        nullable=False
    )

    # --------------------------------------------------------
    # SSL Wireless API Response
    # --------------------------------------------------------

    response = db.Column(
        db.Text,
        nullable=True
    )

    # --------------------------------------------------------
    # SMS পাঠানোর সময়
    # --------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # --------------------------------------------------------
    # Relationship
    # --------------------------------------------------------

    broadcast = db.relationship(
        "BroadcastMessage",
        backref=db.backref(
            "sms_logs",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    student = db.relationship(
        "User",
        backref=db.backref(
            "sms_logs",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<SMSLog {self.id} - {self.status}>"


# ============================================================
# FORM REQUEST MODEL
# ============================================================
# ছবিতে দেখানো Request Form-এর জন্য এই Table।
#
# Student ভবিষ্যতে Teacher-এর কাছে request পাঠাতে পারবে।
# Teacher/Admin সেটি Accept বা Cancel করতে পারবে।
# ============================================================

class FormRequest(db.Model):

    __tablename__ = "form_requests"

    # --------------------------------------------------------
    # Request ID
    # --------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # --------------------------------------------------------
    # যে Student Request পাঠিয়েছে
    # --------------------------------------------------------

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # Student-এর নাম
    # --------------------------------------------------------

    student_name = db.Column(
        db.String(120),
        nullable=False
    )

    # --------------------------------------------------------
    # Request-এর Subject
    # --------------------------------------------------------

    subject = db.Column(
        db.String(200),
        nullable=False
    )

    # --------------------------------------------------------
    # Request-এর বিস্তারিত
    # --------------------------------------------------------

    message = db.Column(
        db.Text,
        nullable=False
    )

    # --------------------------------------------------------
    # Request Status
    #
    # pending
    # accepted
    # cancelled
    # --------------------------------------------------------

    status = db.Column(
        db.String(20),
        default="pending",
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # কোন Teacher/Admin Request দেখেছে
    # --------------------------------------------------------

    reviewed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    # --------------------------------------------------------
    # Request তৈরি হওয়ার সময়
    # --------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # --------------------------------------------------------
    # Review হওয়ার সময়
    # --------------------------------------------------------

    reviewed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # --------------------------------------------------------
    # Student Relationship
    # --------------------------------------------------------

    student = db.relationship(
        "User",
        foreign_keys=[student_id],
        backref=db.backref(
            "submitted_requests",
            lazy=True
        )
    )

    # --------------------------------------------------------
    # Reviewer Relationship
    # --------------------------------------------------------

    reviewer = db.relationship(
        "User",
        foreign_keys=[reviewed_by]
    )

    def __repr__(self):
        return f"<FormRequest {self.id} - {self.status}>"


# ============================================================
# DIRECT MESSAGE MODEL
# ============================================================
# ভবিষ্যতে Student ↔ Teacher ব্যক্তিগত Text Message
# ব্যবহারের জন্য এই Table রাখা হচ্ছে।
# ============================================================

class DirectMessage(db.Model):

    __tablename__ = "direct_messages"

    # --------------------------------------------------------
    # Message ID
    # --------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # --------------------------------------------------------
    # Message Sender
    # --------------------------------------------------------

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # Message Receiver
    # --------------------------------------------------------

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # Message
    # --------------------------------------------------------

    message = db.Column(
        db.Text,
        nullable=False
    )

    # --------------------------------------------------------
    # Message Read হয়েছে কিনা
    # --------------------------------------------------------

    is_read = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # --------------------------------------------------------
    # Message তৈরি হওয়ার সময়
    # --------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # Sender Relationship
    # --------------------------------------------------------

    sender = db.relationship(
        "User",
        foreign_keys=[sender_id],
        backref=db.backref(
            "sent_messages",
            lazy=True
        )
    )

    # --------------------------------------------------------
    # Receiver Relationship
    # --------------------------------------------------------

    receiver = db.relationship(
        "User",
        foreign_keys=[receiver_id],
        backref=db.backref(
            "received_messages",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<DirectMessage {self.id}>"


# ============================================================
# CALL MESSAGE MODEL
# ============================================================
# ছবির ডিজাইনে থাকা "Call Message" feature-এর জন্য।
#
# এখানে Teacher/Admin একজন Student-এর জন্য
# Call সম্পর্কিত message/notice পাঠাতে পারবে।
# ============================================================

class CallMessage(db.Model):

    __tablename__ = "call_messages"

    # --------------------------------------------------------
    # Call Message ID
    # --------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # --------------------------------------------------------
    # যে Teacher/Admin message পাঠিয়েছে
    # --------------------------------------------------------

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # --------------------------------------------------------
    # যে Student-এর জন্য message
    # --------------------------------------------------------

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # --------------------------------------------------------
    # বিষয়
    # --------------------------------------------------------

    subject = db.Column(
        db.String(200),
        nullable=False
    )

    # --------------------------------------------------------
    # Message
    # --------------------------------------------------------

    message = db.Column(
        db.Text,
        nullable=False
    )

    # --------------------------------------------------------
    # Student message দেখেছে কিনা
    # --------------------------------------------------------

    is_read = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # --------------------------------------------------------
    # তৈরি হওয়ার সময়
    # --------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # --------------------------------------------------------
    # Sender Relationship
    # --------------------------------------------------------

    sender = db.relationship(
        "User",
        foreign_keys=[sender_id],
        backref=db.backref(
            "sent_call_messages",
            lazy=True
        )
    )

    # --------------------------------------------------------
    # Student Relationship
    # --------------------------------------------------------

    student = db.relationship(
        "User",
        foreign_keys=[student_id],
        backref=db.backref(
            "call_messages",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<CallMessage {self.id}>"


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database(app):
    """
    Flask App-এর সাথে Database connect করে এবং
    প্রয়োজনীয় সব Table তৈরি করে।
    """

    # --------------------------------------------------------
    # Flask-এর Database Configuration
    # --------------------------------------------------------

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        app.config.get(
            "DATABASE_URL"
        )
    )

    # --------------------------------------------------------
    # SQLAlchemy tracking বন্ধ রাখছি।
    # এতে অপ্রয়োজনীয় memory usage কমে।
    # --------------------------------------------------------

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --------------------------------------------------------
    # Database-এর সাথে Flask App connect করা
    # --------------------------------------------------------

    db.init_app(app)

    # --------------------------------------------------------
    # Application Context-এর ভিতরে Database Table তৈরি করা
    # --------------------------------------------------------

    with app.app_context():

        db.create_all()


# ============================================================
# DEFAULT ADMIN CREATE FUNCTION
# ============================================================

def create_default_admin(
    name,
    username,
    password
):
    """
    Database-এ Admin account না থাকলে
    একটি Default Admin account তৈরি করে।

    Admin আগে থেকেই থাকলে নতুন Admin তৈরি করবে না।
    """

    # --------------------------------------------------------
    # Username আগে থেকেই আছে কিনা পরীক্ষা
    # --------------------------------------------------------

    existing_admin = User.query.filter_by(
        username=username
    ).first()

    # --------------------------------------------------------
    # Admin আগে থেকেই থাকলে কিছু করার দরকার নেই
    # --------------------------------------------------------

    if existing_admin:

        return existing_admin

    # --------------------------------------------------------
    # নতুন Admin তৈরি
    # --------------------------------------------------------

    admin = User(
        name=name,
        username=username,
        role="admin",
        mobile=None,
        email=None,
        is_active=True
    )

    # --------------------------------------------------------
    # Password Hash করে সংরক্ষণ
    # --------------------------------------------------------

    admin.set_password(password)

    # --------------------------------------------------------
    # Database-এ Save
    # --------------------------------------------------------

    db.session.add(admin)

    db.session.commit()

    return admin


# ============================================================
# DEFAULT TEACHER CREATE FUNCTION
# ============================================================

def create_default_teacher(
    name,
    username,
    password,
    mobile=None
):
    """
    প্রয়োজন হলে Default Teacher account তৈরি করবে।
    """

    existing_teacher = User.query.filter_by(
        username=username
    ).first()

    if existing_teacher:

        return existing_teacher

    teacher = User(
        name=name,
        username=username,
        role="teacher",
        mobile=mobile,
        is_active=True
    )

    teacher.set_password(password)

    db.session.add(teacher)

    db.session.commit()

    return teacher


# ============================================================
# STUDENT CREATE FUNCTION
# ============================================================

def create_student(
    name,
    username,
    password,
    student_class,
    roll,
    mobile,
    email=None
):
    """
    নতুন Student Database-এ তৈরি করার Function।
    """

    # --------------------------------------------------------
    # একই Username আগে থেকেই আছে কিনা পরীক্ষা
    # --------------------------------------------------------

    existing_student = User.query.filter_by(
        username=username
    ).first()

    if existing_student:

        return existing_student

    # --------------------------------------------------------
    # Student Object তৈরি
    # --------------------------------------------------------

    student = User(
        name=name,
        username=username,
        role="student",
        mobile=mobile,
        email=email,
        student_class=student_class,
        roll=roll,
        is_active=True
    )

    # --------------------------------------------------------
    # Password Hash
    # --------------------------------------------------------

    student.set_password(password)

    # --------------------------------------------------------
    # Database-এ Save
    # --------------------------------------------------------

    db.session.add(student)

    db.session.commit()

    return student


# ============================================================
# PUBLIC CHAT SAVE FUNCTION
# ============================================================

def save_chat_message(
    user,
    message
):
    """
    Public Chat-এর Message Database-এ Save করে।
    """

    chat_message = ChatMessage(
        user_id=user.id,
        sender_name=user.name,
        sender_role=user.role,
        message=message
    )

    db.session.add(chat_message)

    db.session.commit()

    return chat_message


# ============================================================
# RECENT CHAT MESSAGE
# ============================================================

def get_recent_chat_messages(limit=50):
    """
    সর্বশেষ Chat Messageগুলো Database থেকে নিয়ে আসে।

    Default হিসেবে শেষ ৫০টি message দেখাবে।
    """

    messages = (
        ChatMessage.query
        .order_by(
            ChatMessage.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    # পুরোনো থেকে নতুন order-এ ফেরত দেওয়া হচ্ছে
    messages.reverse()

    return messages


# ============================================================
# ALL ACTIVE STUDENTS
# ============================================================

def get_all_active_students():
    """
    Database থেকে সব Active Student বের করে।

    Admin Broadcast SMS-এর সময় এই Function ব্যবহার হবে।
    """

    return (
        User.query
        .filter_by(
            role="student",
            is_active=True
        )
        .all()
    )


# ============================================================
# STUDENTS WITH MOBILE NUMBER
# ============================================================

def get_students_with_mobile():
    """
    যেসব Active Student-এর Mobile Number আছে,
    শুধুমাত্র তাদের বের করে।

    Broadcast SMS-এর সময় এটি ব্যবহার করা হবে।
    """

    return (
        User.query
        .filter(
            User.role == "student",
            User.is_active.is_(True),
            User.mobile.isnot(None),
            User.mobile != ""
        )
        .all()
    )