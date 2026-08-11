# ============================================================
# SHSD Link - School Communication System
# PART 5 : Main Flask Application
# ============================================================

from datetime import datetime
import json

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from flask_socketio import (
    SocketIO,
    emit
)

from config import (
    BASE_DIR,
    DATABASE_URL,
    SECRET_KEY,
    SCHOOL_NAME,
    SCHOOL_TAGLINE,
    DEBUG_MODE,
    SOCKETIO_ASYNC_MODE,
    DEFAULT_ADMIN_NAME,
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_ROLE,
    ROLE_ADMIN,
    ROLE_TEACHER,
    ROLE_STUDENT,
    MAX_CHAT_MESSAGE_LENGTH,
    create_required_folders
)

from database import (
    db,
    User,
    ChatMessage,
    BroadcastMessage,
    SMSLog,
    FormRequest,
    DirectMessage,
    CallMessage,
    initialize_database,
    create_default_admin,
    create_default_teacher,
    save_chat_message,
    get_recent_chat_messages,
    get_students_with_mobile
)

from sms_service import (
    send_sms,
    send_bulk_sms,
    get_sms_service_status,
    is_valid_mobile_number
)


# ============================================================
# FLASK APP CREATE
# ============================================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)


# ============================================================
# FLASK CONFIGURATION
# ============================================================

app.config["SECRET_KEY"] = SECRET_KEY

app.config["DATABASE_URL"] = DATABASE_URL

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SCHOOL_NAME"] = SCHOOL_NAME

app.config["SCHOOL_TAGLINE"] = SCHOOL_TAGLINE

app.config["MAX_CHAT_MESSAGE_LENGTH"] = (
    MAX_CHAT_MESSAGE_LENGTH
)


# ============================================================
# REQUIRED FOLDER CREATE
# ============================================================

create_required_folders()


# ============================================================
# DATABASE INITIALIZE
# ============================================================

initialize_database(app)


# ============================================================
# FLASK LOGIN CONFIGURATION
# ============================================================

login_manager = LoginManager()

login_manager.init_app(app)

# Login না করা অবস্থায় protected page-এ গেলে
# এই route-এ পাঠানো হবে।

login_manager.login_view = "login"

login_manager.login_message = (
    "এই পেজটি দেখতে আগে Login করতে হবে।"
)

login_manager.login_message_category = "warning"


# ============================================================
# SOCKETIO INITIALIZE
# ============================================================
# Public Text Chat-এর Real-Time System-এর জন্য।
# ============================================================

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode=SOCKETIO_ASYNC_MODE
)


# ============================================================
# FLASK-LOGIN USER LOADER
# ============================================================
# Session-এর User ID থেকে Database-এর User খুঁজে বের করে।
# ============================================================

@login_manager.user_loader
def load_user(user_id):

    try:

        return db.session.get(
            User,
            int(user_id)
        )

    except (
        ValueError,
        TypeError
    ):

        return None


# ============================================================
# TEMPLATE GLOBAL DATA
# ============================================================
# সব HTML Page-এ এই তথ্যগুলো সরাসরি ব্যবহার করা যাবে।
# ============================================================

@app.context_processor
def inject_global_data():

    return {
        "school_name": SCHOOL_NAME,
        "school_tagline": SCHOOL_TAGLINE,
        "current_year": datetime.now().year
    }


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def index():

    # --------------------------------------------------------
    # User Login করা থাকলে তার Dashboard-এ পাঠানো হবে।
    # --------------------------------------------------------

    if current_user.is_authenticated:

        if current_user.role == ROLE_ADMIN:

            return redirect(
                url_for("admin_dashboard")
            )

        if current_user.role == ROLE_TEACHER:

            return redirect(
                url_for("teacher_dashboard")
            )

        if current_user.role == ROLE_STUDENT:

            return redirect(
                url_for("student_dashboard")
            )

    # --------------------------------------------------------
    # Login না করা থাকলে Login Page
    # --------------------------------------------------------

    return redirect(
        url_for("login")
    )


# ============================================================
# LOGIN PAGE
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # --------------------------------------------------------
    # যদি আগে থেকেই Login করা থাকে
    # --------------------------------------------------------

    if current_user.is_authenticated:

        return redirect(
            url_for("index")
        )

    # --------------------------------------------------------
    # POST হলে Login করার চেষ্টা
    # --------------------------------------------------------

    if request.method == "POST":

        username = (
            request.form.get(
                "username",
                ""
            )
            .strip()
        )

        password = request.form.get(
            "password",
            ""
        )

        selected_role = (
            request.form.get(
                "role",
                ""
            )
            .strip()
            .lower()
        )

        # ----------------------------------------------------
        # Basic Validation
        # ----------------------------------------------------

        if not username:

            flash(
                "Username দিন।",
                "danger"
            )

            return redirect(
                url_for("login")
            )

        if not password:

            flash(
                "Password দিন।",
                "danger"
            )

            return redirect(
                url_for("login")
            )

        if selected_role not in (
            ROLE_ADMIN,
            ROLE_TEACHER,
            ROLE_STUDENT
        ):

            flash(
                "সঠিক User Type নির্বাচন করুন।",
                "danger"
            )

            return redirect(
                url_for("login")
            )

        # ----------------------------------------------------
        # Username দিয়ে User খোঁজা
        # ----------------------------------------------------

        user = User.query.filter_by(
            username=username
        ).first()

        # ----------------------------------------------------
        # User না থাকলে
        # ----------------------------------------------------

        if not user:

            flash(
                "Username অথবা Password সঠিক নয়।",
                "danger"
            )

            return redirect(
                url_for("login")
            )

        # ----------------------------------------------------
        # Account Active কিনা
        # ----------------------------------------------------

        if not user.is_active:

            flash(
                "এই Account বর্তমানে বন্ধ আছে।",
                "danger"
            )

            return redirect(
                url_for("login")
            )

        # ----------------------------------------------------
        # Selected Role এবং Database Role মিলছে কিনা
        # ----------------------------------------------------

        if user.role != selected_role:

            flash(
                "আপনার Account-এর User Type সঠিক নয়।",
                "danger"
            )

            return redirect(
                url_for("login")
            )

        # ----------------------------------------------------
        # Password Check
        # ----------------------------------------------------

        if not user.check_password(password):

            flash(
                "Username অথবা Password সঠিক নয়।",
                "danger"
            )

            return redirect(
                url_for("login")
            )

        # ----------------------------------------------------
        # Successful Login
        # ----------------------------------------------------

        login_user(user)

        flash(
            f"স্বাগতম, {user.name}!",
            "success"
        )

        # ----------------------------------------------------
        # Role অনুযায়ী Dashboard
        # ----------------------------------------------------

        if user.role == ROLE_ADMIN:

            return redirect(
                url_for("admin_dashboard")
            )

        if user.role == ROLE_TEACHER:

            return redirect(
                url_for("teacher_dashboard")
            )

        return redirect(
            url_for("student_dashboard")
        )

    # --------------------------------------------------------
    # Login Page দেখানো
    # --------------------------------------------------------

    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "আপনি সফলভাবে Logout করেছেন।",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# ADMIN ACCESS DECORATOR
# ============================================================
# শুধু Admin Role-এর User-এর জন্য।
# ============================================================

def admin_required(function):

    from functools import wraps

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not current_user.is_authenticated:

            return redirect(
                url_for("login")
            )

        if current_user.role != ROLE_ADMIN:

            flash(
                "এই পেজটি শুধুমাত্র Admin-এর জন্য।",
                "danger"
            )

            return redirect(
                url_for("index")
            )

        return function(
            *args,
            **kwargs
        )

    return decorated_function


# ============================================================
# TEACHER ACCESS DECORATOR
# ============================================================
# Teacher এবং Admin দুজনই Teacher Dashboard ব্যবহার করতে পারবে।
# ============================================================

def teacher_required(function):

    from functools import wraps

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not current_user.is_authenticated:

            return redirect(
                url_for("login")
            )

        if current_user.role not in (
            ROLE_ADMIN,
            ROLE_TEACHER
        ):

            flash(
                "এই পেজটি Teacher/Admin-এর জন্য।",
                "danger"
            )

            return redirect(
                url_for("index")
            )

        return function(
            *args,
            **kwargs
        )

    return decorated_function


# ============================================================
# STUDENT ACCESS DECORATOR
# ============================================================

def student_required(function):

    from functools import wraps

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not current_user.is_authenticated:

            return redirect(
                url_for("login")
            )

        if current_user.role != ROLE_STUDENT:

            flash(
                "এই পেজটি Student-এর জন্য।",
                "danger"
            )

            return redirect(
                url_for("index")
            )

        return function(
            *args,
            **kwargs
        )

    return decorated_function


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    # --------------------------------------------------------
    # সব Student
    # --------------------------------------------------------

    students = (
        User.query
        .filter_by(
            role=ROLE_STUDENT
        )
        .order_by(
            User.id.desc()
        )
        .all()
    )

    # --------------------------------------------------------
    # মোট Student সংখ্যা
    # --------------------------------------------------------

    total_students = User.query.filter_by(
        role=ROLE_STUDENT
    ).count()

    # --------------------------------------------------------
    # মোট Teacher সংখ্যা
    # --------------------------------------------------------

    total_teachers = User.query.filter_by(
        role=ROLE_TEACHER
    ).count()

    # --------------------------------------------------------
    # মোট Chat Message
    # --------------------------------------------------------

    total_chat_messages = ChatMessage.query.count()

    # --------------------------------------------------------
    # Pending Request
    # --------------------------------------------------------

    pending_requests = FormRequest.query.filter_by(
        status="pending"
    ).count()

    # --------------------------------------------------------
    # Recent Broadcast
    # --------------------------------------------------------

    recent_broadcasts = (
        BroadcastMessage.query
        .order_by(
            BroadcastMessage.created_at.desc()
        )
        .limit(10)
        .all()
    )

    return render_template(
        "admin_dashboard.html",
        students=students,
        total_students=total_students,
        total_teachers=total_teachers,
        total_chat_messages=total_chat_messages,
        pending_requests=pending_requests,
        recent_broadcasts=recent_broadcasts
    )


# ============================================================
# TEACHER DASHBOARD
# ============================================================

@app.route("/teacher/dashboard")
@teacher_required
def teacher_dashboard():

    # --------------------------------------------------------
    # Student List
    # --------------------------------------------------------

    students = (
        User.query
        .filter_by(
            role=ROLE_STUDENT,
            is_active=True
        )
        .order_by(
            User.name.asc()
        )
        .all()
    )

    # --------------------------------------------------------
    # Pending Request
    # --------------------------------------------------------

    pending_requests = (
        FormRequest.query
        .filter_by(
            status="pending"
        )
        .order_by(
            FormRequest.created_at.desc()
        )
        .all()
    )

    # --------------------------------------------------------
    # Recent Chat
    # --------------------------------------------------------

    recent_messages = get_recent_chat_messages(
        limit=30
    )

    return render_template(
        "teacher_dashboard.html",
        students=students,
        pending_requests=pending_requests,
        recent_messages=recent_messages
    )


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@app.route("/student/dashboard")
@student_required
def student_dashboard():

    # --------------------------------------------------------
    # Student-এর নিজের Request
    # --------------------------------------------------------

    requests_list = (
        FormRequest.query
        .filter_by(
            student_id=current_user.id
        )
        .order_by(
            FormRequest.created_at.desc()
        )
        .all()
    )

    # --------------------------------------------------------
    # Student-এর Call Message
    # --------------------------------------------------------

    call_messages = (
        CallMessage.query
        .filter_by(
            student_id=current_user.id
        )
        .order_by(
            CallMessage.created_at.desc()
        )
        .limit(20)
        .all()
    )

    # --------------------------------------------------------
    # Recent Public Chat
    # --------------------------------------------------------

    recent_messages = get_recent_chat_messages(
        limit=30
    )

    return render_template(
        "student_dashboard.html",
        requests_list=requests_list,
        call_messages=call_messages,
        recent_messages=recent_messages
    )


# ============================================================
# PUBLIC CHAT PAGE
# ============================================================
# Login করা সবাই Public Chat ব্যবহার করতে পারবে।
# ============================================================

@app.route("/chat")
@login_required
def public_chat():

    recent_messages = get_recent_chat_messages(
        limit=50
    )

    return render_template(
        "chat.html",
        recent_messages=recent_messages
    )


# ============================================================
# CHAT HISTORY API
# ============================================================

@app.route("/api/chat/history")
@login_required
def chat_history():

    messages = get_recent_chat_messages(
        limit=50
    )

    data = []

    for message in messages:

        data.append({
            "id": message.id,
            "sender_name": message.sender_name,
            "sender_role": message.sender_role,
            "message": message.message,
            "created_at": message.created_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        })

    return jsonify({
        "success": True,
        "messages": data
    })


# ============================================================
# SOCKETIO - USER CONNECTED
# ============================================================

@socketio.on("connect")
def socket_connect():

    # --------------------------------------------------------
    # Socket connection করার সময় User Login করা আছে কিনা
    # --------------------------------------------------------

    if not current_user.is_authenticated:

        return False

    # --------------------------------------------------------
    # Connected User-এর তথ্য পাঠানো
    # --------------------------------------------------------

    emit(
        "connection_status",
        {
            "success": True,
            "message": (
                f"স্বাগতম {current_user.name}"
            )
        }
    )


# ============================================================
# SOCKETIO - PUBLIC CHAT MESSAGE
# ============================================================

@socketio.on("send_public_message")
def handle_public_message(data):

    # --------------------------------------------------------
    # Login ছাড়া Chat করা যাবে না।
    # --------------------------------------------------------

    if not current_user.is_authenticated:

        emit(
            "chat_error",
            {
                "message": (
                    "Chat করার জন্য আগে Login করুন।"
                )
            }
        )

        return

    # --------------------------------------------------------
    # Data না থাকলে
    # --------------------------------------------------------

    if not data:

        emit(
            "chat_error",
            {
                "message": "Message পাওয়া যায়নি।"
            }
        )

        return

    # --------------------------------------------------------
    # Message নেওয়া
    # --------------------------------------------------------

    message = str(
        data.get(
            "message",
            ""
        )
    ).strip()

    # --------------------------------------------------------
    # Empty Message
    # --------------------------------------------------------

    if not message:

        emit(
            "chat_error",
            {
                "message": "খালি message পাঠানো যাবে না।"
            }
        )

        return

    # --------------------------------------------------------
    # Maximum Length
    # --------------------------------------------------------

    if len(message) > MAX_CHAT_MESSAGE_LENGTH:

        emit(
            "chat_error",
            {
                "message": (
                    f"Message সর্বোচ্চ "
                    f"{MAX_CHAT_MESSAGE_LENGTH} "
                    f"অক্ষরের হতে পারবে।"
                )
            }
        )

        return

    # --------------------------------------------------------
    # Database-এ Save
    # --------------------------------------------------------

    try:

        chat_message = save_chat_message(
            current_user,
            message
        )

    except Exception:

        db.session.rollback()

        emit(
            "chat_error",
            {
                "message": (
                    "Message save করা যায়নি।"
                )
            }
        )

        return

    # --------------------------------------------------------
    # Message Data তৈরি
    # --------------------------------------------------------

    message_data = {
        "id": chat_message.id,
        "sender_name": chat_message.sender_name,
        "sender_role": chat_message.sender_role,
        "message": chat_message.message,
        "created_at": chat_message.created_at.strftime(
            "%H:%M"
        )
    }

    # --------------------------------------------------------
    # Room-এর সবাইকে Message পাঠানো
    # --------------------------------------------------------
    # এখানেই Real-Time Chat কাজ করবে।
    # Browser refresh করার দরকার হবে না।
    # --------------------------------------------------------

    emit(
        "new_public_message",
        message_data,
        broadcast=True
    )


# ============================================================
# ADMIN BROADCAST PAGE
# ============================================================

@app.route("/admin/broadcast")
@admin_required
def admin_broadcast():

    recent_broadcasts = (
        BroadcastMessage.query
        .order_by(
            BroadcastMessage.created_at.desc()
        )
        .limit(20)
        .all()
    )

    sms_status = get_sms_service_status()

    students = (
        User.query
        .filter_by(
            role=ROLE_STUDENT,
            is_active=True
        )
        .order_by(
            User.name.asc()
        )
        .all()
    )

    return render_template(
        "admin_broadcast.html",
        recent_broadcasts=recent_broadcasts,
        sms_status=sms_status,
        students=students
    )


# ============================================================
# ADMIN SEND BROADCAST SMS
# ============================================================

@app.route(
    "/admin/broadcast/send",
    methods=["POST"]
)
@admin_required
def admin_send_broadcast():

    # --------------------------------------------------------
    # Message নেওয়া
    # --------------------------------------------------------

    message = (
        request.form.get(
            "message",
            ""
        )
        .strip()
    )

    # --------------------------------------------------------
    # Message Validation
    # --------------------------------------------------------

    if not message:

        flash(
            "Broadcast message লিখুন।",
            "danger"
        )

        return redirect(
            url_for("admin_broadcast")
        )

    # --------------------------------------------------------
    # Student-এর Mobile Number সহ List
    # --------------------------------------------------------

    students = get_students_with_mobile()

    # --------------------------------------------------------
    # Student না থাকলে
    # --------------------------------------------------------

    if not students:

        flash(
            "Mobile Number সহ কোনো Active Student পাওয়া যায়নি।",
            "warning"
        )

        return redirect(
            url_for("admin_broadcast")
        )

    # --------------------------------------------------------
    # Broadcast Record আগে তৈরি করা
    # --------------------------------------------------------

    broadcast = BroadcastMessage(
        admin_id=current_user.id,
        admin_name=current_user.name,
        message=message,
        total_recipients=len(students),
        successful_count=0,
        failed_count=0
    )

    db.session.add(broadcast)

    db.session.commit()

    # --------------------------------------------------------
    # প্রত্যেক Student-এর কাছে SMS পাঠানো
    # --------------------------------------------------------

    success_count = 0

    failed_count = 0

    api_responses = []

    for student in students:

        # ----------------------------------------------------
        # Mobile Number basic validation
        # ----------------------------------------------------

        if not is_valid_mobile_number(
            student.mobile
        ):

            failed_count += 1

            sms_log = SMSLog(
                broadcast_id=broadcast.id,
                student_id=student.id,
                student_name=student.name,
                mobile=student.mobile or "",
                status="failed",
                response="Invalid mobile number"
            )

            db.session.add(
                sms_log
            )

            continue

        # ----------------------------------------------------
        # SMS Send
        # ----------------------------------------------------

        result = send_sms(
            mobile=student.mobile,
            message=message
        )

        # ----------------------------------------------------
        # Result Save
        # ----------------------------------------------------

        if result.get("success"):

            status = "success"

            success_count += 1

        else:

            status = "failed"

            failed_count += 1

        # ----------------------------------------------------
        # API Response Safe String
        # ----------------------------------------------------

        api_response = result.get(
            "response"
        )

        try:

            response_text = json.dumps(
                api_response,
                ensure_ascii=False
            )

        except Exception:

            response_text = str(
                api_response
            )

        # ----------------------------------------------------
        # SMS Log
        # ----------------------------------------------------

        sms_log = SMSLog(
            broadcast_id=broadcast.id,
            student_id=student.id,
            student_name=student.name,
            mobile=student.mobile or "",
            status=status,
            response=response_text
        )

        db.session.add(
            sms_log
        )

        api_responses.append({
            "student_id": student.id,
            "student_name": student.name,
            "status": status,
            "response": api_response
        })

    # --------------------------------------------------------
    # Broadcast Summary Update
    # --------------------------------------------------------

    broadcast.successful_count = success_count

    broadcast.failed_count = failed_count

    try:

        broadcast.api_response = json.dumps(
            api_responses,
            ensure_ascii=False
        )

    except Exception:

        broadcast.api_response = str(
            api_responses
        )

    db.session.commit()

    # --------------------------------------------------------
    # Admin-কে Result দেখানো
    # --------------------------------------------------------

    if success_count > 0 and failed_count == 0:

        flash(
            (
                f"সফলভাবে {success_count} জন "
                f"Student-এর Mobile-এ SMS পাঠানো হয়েছে।"
            ),
            "success"
        )

    elif success_count > 0:

        flash(
            (
                f"{success_count}টি SMS সফল এবং "
                f"{failed_count}টি SMS ব্যর্থ হয়েছে।"
            ),
            "warning"
        )

    else:

        flash(
            (
                "কোনো SMS সফলভাবে পাঠানো যায়নি। "
                "SSL Wireless configuration পরীক্ষা করুন।"
            ),
            "danger"
        )

    return redirect(
        url_for("admin_broadcast")
    )


# ============================================================
# ADMIN STUDENT LIST
# ============================================================

@app.route("/admin/students")
@admin_required
def admin_students():

    students = (
        User.query
        .filter_by(
            role=ROLE_STUDENT
        )
        .order_by(
            User.name.asc()
        )
        .all()
    )

    return render_template(
        "student_list.html",
        students=students
    )


# ============================================================
# TEACHER STUDENT LIST
# ============================================================

@app.route("/teacher/students")
@teacher_required
def teacher_students():

    students = (
        User.query
        .filter_by(
            role=ROLE_STUDENT,
            is_active=True
        )
        .order_by(
            User.name.asc()
        )
        .all()
    )

    return render_template(
        "student_list.html",
        students=students
    )


# ============================================================
# REQUEST FORM PAGE
# ============================================================

@app.route("/request-form")
@login_required
def request_form():

    # --------------------------------------------------------
    # Student এবং Teacher উভয়েই Request Form দেখতে পারবে।
    # --------------------------------------------------------

    requests_list = []

    if current_user.role == ROLE_STUDENT:

        requests_list = (
            FormRequest.query
            .filter_by(
                student_id=current_user.id
            )
            .order_by(
                FormRequest.created_at.desc()
            )
            .all()
        )

    else:

        requests_list = (
            FormRequest.query
            .order_by(
                FormRequest.created_at.desc()
            )
            .limit(50)
            .all()
        )

    return render_template(
        "request_form.html",
        requests_list=requests_list
    )


# ============================================================
# STUDENT SUBMIT REQUEST
# ============================================================

@app.route(
    "/request-form/submit",
    methods=["POST"]
)
@student_required
def submit_request():

    subject = (
        request.form.get(
            "subject",
            ""
        )
        .strip()
    )

    message = (
        request.form.get(
            "message",
            ""
        )
        .strip()
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if not subject:

        flash(
            "Request-এর Subject লিখুন।",
            "danger"
        )

        return redirect(
            url_for("request_form")
        )

    if not message:

        flash(
            "Request-এর বিস্তারিত লিখুন।",
            "danger"
        )

        return redirect(
            url_for("request_form")
        )

    # --------------------------------------------------------
    # Request Create
    # --------------------------------------------------------

    new_request = FormRequest(
        student_id=current_user.id,
        student_name=current_user.name,
        subject=subject,
        message=message,
        status="pending"
    )

    db.session.add(
        new_request
    )

    db.session.commit()

    flash(
        "আপনার Request সফলভাবে পাঠানো হয়েছে।",
        "success"
    )

    return redirect(
        url_for("request_form")
    )


# ============================================================
# ADMIN / TEACHER REQUEST REVIEW
# ============================================================

@app.route(
    "/request/<int:request_id>/<action>",
    methods=["POST"]
)
@teacher_required
def review_request(
    request_id,
    action
):

    # --------------------------------------------------------
    # Request খোঁজা
    # --------------------------------------------------------

    form_request = db.session.get(
        FormRequest,
        request_id
    )

    if not form_request:

        flash(
            "Request পাওয়া যায়নি।",
            "danger"
        )

        return redirect(
            url_for("teacher_dashboard")
        )

    # --------------------------------------------------------
    # Action Check
    # --------------------------------------------------------

    if action not in (
        "accept",
        "cancel"
    ):

        flash(
            "Invalid action.",
            "danger"
        )

        return redirect(
            url_for("teacher_dashboard")
        )

    # --------------------------------------------------------
    # Status Update
    # --------------------------------------------------------

    if action == "accept":

        form_request.status = "accepted"

    else:

        form_request.status = "cancelled"

    form_request.reviewed_by = current_user.id

    form_request.reviewed_at = datetime.utcnow()

    db.session.commit()

    flash(
        "Request-এর status update করা হয়েছে।",
        "success"
    )

    return redirect(
        url_for("teacher_dashboard")
    )


# ============================================================
# CALL MESSAGE PAGE
# ============================================================

@app.route("/call-message")
@teacher_required
def call_message():

    students = (
        User.query
        .filter_by(
            role=ROLE_STUDENT,
            is_active=True
        )
        .order_by(
            User.name.asc()
        )
        .all()
    )

    return render_template(
        "call_message.html",
        students=students
    )


# ============================================================
# SEND CALL MESSAGE
# ============================================================

@app.route(
    "/call-message/send",
    methods=["POST"]
)
@teacher_required
def send_call_message():

    student_id = request.form.get(
        "student_id",
        ""
    )

    subject = (
        request.form.get(
            "subject",
            ""
        )
        .strip()
    )

    message = (
        request.form.get(
            "message",
            ""
        )
        .strip()
    )

    # --------------------------------------------------------
    # Student ID validation
    # --------------------------------------------------------

    try:

        student_id = int(
            student_id
        )

    except (
        ValueError,
        TypeError
    ):

        flash(
            "সঠিক Student নির্বাচন করুন।",
            "danger"
        )

        return redirect(
            url_for("call_message")
        )

    # --------------------------------------------------------
    # Student খোঁজা
    # --------------------------------------------------------

    student = db.session.get(
        User,
        student_id
    )

    if not student or student.role != ROLE_STUDENT:

        flash(
            "Student পাওয়া যায়নি।",
            "danger"
        )

        return redirect(
            url_for("call_message")
        )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if not subject:

        flash(
            "Subject লিখুন।",
            "danger"
        )

        return redirect(
            url_for("call_message")
        )

    if not message:

        flash(
            "Message লিখুন।",
            "danger"
        )

        return redirect(
            url_for("call_message")
        )

    # --------------------------------------------------------
    # Call Message Save
    # --------------------------------------------------------

    new_call_message = CallMessage(
        sender_id=current_user.id,
        student_id=student.id,
        subject=subject,
        message=message
    )

    db.session.add(
        new_call_message
    )

    db.session.commit()

    flash(
        f"{student.name}-এর কাছে Call Message পাঠানো হয়েছে।",
        "success"
    )

    return redirect(
        url_for("call_message")
    )


# ============================================================
# STUDENT READ CALL MESSAGE
# ============================================================

@app.route(
    "/call-message/read/<int:message_id>",
    methods=["POST"]
)
@student_required
def read_call_message(message_id):

    call_message = db.session.get(
        CallMessage,
        message_id
    )

    if not call_message:

        return jsonify({
            "success": False,
            "message": "Message পাওয়া যায়নি।"
        }), 404

    # --------------------------------------------------------
    # শুধুমাত্র নিজের Message read করতে পারবে
    # --------------------------------------------------------

    if call_message.student_id != current_user.id:

        return jsonify({
            "success": False,
            "message": "Permission denied."
        }), 403

    call_message.is_read = True

    db.session.commit()

    return jsonify({
        "success": True
    })


# ============================================================
# DIRECT TEXT MESSAGE
# ============================================================
# ভবিষ্যতের Student ↔ Teacher ব্যক্তিগত Messaging-এর
# Backend route।
# ============================================================

@app.route(
    "/message/send",
    methods=["POST"]
)
@login_required
def send_direct_message():

    receiver_id = request.form.get(
        "receiver_id",
        ""
    )

    message = (
        request.form.get(
            "message",
            ""
        )
        .strip()
    )

    # --------------------------------------------------------
    # Receiver ID
    # --------------------------------------------------------

    try:

        receiver_id = int(
            receiver_id
        )

    except (
        ValueError,
        TypeError
    ):

        return jsonify({
            "success": False,
            "message": "Invalid receiver."
        }), 400

    # --------------------------------------------------------
    # Receiver
    # --------------------------------------------------------

    receiver = db.session.get(
        User,
        receiver_id
    )

    if not receiver:

        return jsonify({
            "success": False,
            "message": "Receiver পাওয়া যায়নি।"
        }), 404

    # --------------------------------------------------------
    # Message Validation
    # --------------------------------------------------------

    if not message:

        return jsonify({
            "success": False,
            "message": "Message খালি হতে পারবে না।"
        }), 400

    if len(message) > MAX_CHAT_MESSAGE_LENGTH:

        return jsonify({
            "success": False,
            "message": "Message অনেক বড়।"
        }), 400

    # --------------------------------------------------------
    # Direct Message Save
    # --------------------------------------------------------

    direct_message = DirectMessage(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        message=message
    )

    db.session.add(
        direct_message
    )

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Message পাঠানো হয়েছে।",
        "data": {
            "id": direct_message.id,
            "sender": current_user.name,
            "receiver": receiver.name,
            "message": direct_message.message,
            "created_at": direct_message.created_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }
    })


# ============================================================
# HEALTH CHECK
# ============================================================
# Website ঠিকমতো চলছে কিনা পরীক্ষা করার ছোট API।
# ============================================================

@app.route("/health")
def health_check():

    return jsonify({
        "success": True,
        "application": SCHOOL_NAME,
        "status": "running"
    })


# ============================================================
# ERROR HANDLER - 404
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


# ============================================================
# ERROR HANDLER - 500
# ============================================================

@app.errorhandler(500)
def internal_server_error(error):

    db.session.rollback()

    return render_template(
        "500.html"
    ), 500


# ============================================================
# FIRST RUN SETUP
# ============================================================

def setup_default_accounts():

    """
    Website প্রথমবার চালু হলে প্রয়োজনীয় default account তৈরি করে।

    Default Admin:
        Username: admin
        Password: admin12345

    Default Teacher:
        Username: teacher
        Password: teacher12345

    পরবর্তীতে Admin Dashboard থেকে User Management
    যোগ করা হবে।
    """

    # --------------------------------------------------------
    # Default Admin
    # --------------------------------------------------------

    create_default_admin(
        name=DEFAULT_ADMIN_NAME,
        username=DEFAULT_ADMIN_USERNAME,
        password=DEFAULT_ADMIN_PASSWORD
    )

    # --------------------------------------------------------
    # Default Teacher
    # --------------------------------------------------------

    create_default_teacher(
        name="Demo Teacher",
        username="teacher",
        password="teacher12345",
        mobile=None
    )


# ============================================================
# RUN INITIAL SETUP
# ============================================================

with app.app_context():

    setup_default_accounts()


# ============================================================
# DEVELOPMENT SERVER
# ============================================================

if __name__ == "__main__":

    print("")
    print(
        "================================================"
    )

    print(
        f"  {SCHOOL_NAME}"
    )

    print(
        "  School Communication System"
    )

    print(
        "================================================"
    )

    print(
        "  Website: http://127.0.0.1:5000"
    )

    print(
        "  Default Admin:"
    )

    print(
        "      Username : admin"
    )

    print(
        "      Password : admin12345"
    )

    print(
        ""
    )

    print(
        "  Default Teacher:"
    )

    print(
        "      Username : teacher"
    )

    print(
        "      Password : teacher12345"
    )

    print(
        "================================================"
    )

    print("")

    # --------------------------------------------------------
    # Flask-SocketIO Server চালু করা
    # --------------------------------------------------------

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=DEBUG_MODE
    )