/* ============================================================
   SHSD LINK
   PART 8 : MAIN JAVASCRIPT
   ============================================================ */


/* ============================================================
   DOM READY
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {

    /*
     * Website পুরোপুরি load হওয়ার পর
     * এই JavaScript কাজ শুরু করবে।
     */

    initializeTooltips();

    initializeChat();

    initializeForms();

    initializeMobileNavigation();

});


/* ============================================================
   BOOTSTRAP TOOLTIPS
   ============================================================ */

function initializeTooltips() {

    /*
     * যেসব element-এ Bootstrap tooltip আছে
     * সেগুলো চালু করা হচ্ছে।
     */

    const tooltipElements =
        document.querySelectorAll(
            '[data-bs-toggle="tooltip"]'
        );


    tooltipElements.forEach(function (element) {

        new bootstrap.Tooltip(element);

    });

}


/* ============================================================
   PUBLIC CHAT
   ============================================================ */

function initializeChat() {

    /*
     * Chat page-এ #chatMessages থাকলে
     * বুঝব আমরা Public Chat page-এ আছি।
     */

    const chatMessages =
        document.getElementById(
            "chatMessages"
        );


    if (!chatMessages) {

        /*
         * Chat page নয়।
         * তাই আর কিছু করার প্রয়োজন নেই।
         */

        return;

    }


    /*
     * Socket.IO connection তৈরি করা হচ্ছে।
     *
     * Backend-এর Flask-SocketIO server
     * এই connection ব্যবহার করবে।
     */

    let socket;


    try {

        socket = io();

    } catch (error) {

        console.error(
            "Socket.IO connection তৈরি করা যায়নি:",
            error
        );

        return;

    }


    /* ========================================================
       CHAT FORM
       ======================================================== */

    const chatForm =
        document.getElementById(
            "chatForm"
        );


    const chatInput =
        document.getElementById(
            "chatInput"
        );


    const chatSendButton =
        document.getElementById(
            "chatSendButton"
        );


    /* ========================================================
       SOCKET CONNECT
       ======================================================== */

    socket.on("connect", function () {

        console.log(
            "Public Chat server-এর সাথে connected."
        );


        updateChatConnectionStatus(
            true
        );

    });


    /* ========================================================
       SOCKET DISCONNECT
       ======================================================== */

    socket.on("disconnect", function () {

        console.log(
            "Public Chat server থেকে disconnected."
        );


        updateChatConnectionStatus(
            false
        );

    });


    /* ========================================================
       CHAT MESSAGE RECEIVE
       ======================================================== */

    socket.on(
        "new_message",
        function (message) {

            /*
             * Backend থেকে নতুন message এলে
             * এই function message screen-এ দেখাবে।
             */

            addChatMessage(
                message
            );

        }
    );


    /* ========================================================
       OLD CHAT HISTORY
       ======================================================== */

    socket.on(
        "chat_history",
        function (messages) {

            /*
             * Server পুরনো message পাঠালে
             * প্রথমে chat পরিষ্কার করে
             * তারপর সব message দেখানো হবে।
             */

            chatMessages.innerHTML = "";


            if (
                !messages ||
                messages.length === 0
            ) {

                showChatEmptyState();

                return;

            }


            messages.forEach(
                function (message) {

                    addChatMessage(
                        message,
                        false
                    );

                }
            );


            scrollChatToBottom();

        }
    );


    /* ========================================================
       SEND CHAT MESSAGE
       ======================================================== */

    if (chatForm) {

        chatForm.addEventListener(
            "submit",
            function (event) {

                /*
                 * Browser-এর normal form submit বন্ধ করছি।
                 */

                event.preventDefault();


                if (!chatInput) {

                    return;

                }


                const message =
                    chatInput.value.trim();


                /*
                 * খালি message পাঠানো যাবে না।
                 */

                if (!message) {

                    showLocalNotification(
                        "মেসেজ লিখুন।",
                        "warning"
                    );

                    chatInput.focus();

                    return;

                }


                /*
                 * অতিরিক্ত বড় message আটকানো হচ্ছে।
                 */

                if (message.length > 1000) {

                    showLocalNotification(
                        "মেসেজ সর্বোচ্চ ১০০০ অক্ষরের হতে পারবে।",
                        "warning"
                    );

                    return;

                }


                /*
                 * Server-এ message পাঠানো হচ্ছে।
                 */

                socket.emit(
                    "send_message",
                    {
                        message: message
                    }
                );


                /*
                 * Input পরিষ্কার করা হচ্ছে।
                 */

                chatInput.value = "";

                chatInput.focus();

            }
        );

    }


    /* ========================================================
       ENTER KEY
       ======================================================== */

    if (chatInput) {

        chatInput.addEventListener(
            "keydown",
            function (event) {

                /*
                 * Enter চাপলে message send হবে।
                 *
                 * Shift + Enter দিলে নতুন line হবে।
                 */

                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();


                    if (chatForm) {

                        chatForm.requestSubmit();

                    }

                }

            }
        );

    }


    /* ========================================================
       SEND BUTTON LOADING
       ======================================================== */

    if (chatSendButton) {

        chatForm?.addEventListener(
            "submit",
            function () {

                /*
                 * Message পাঠানোর সময়
                 * button সামান্য visual feedback দেবে।
                 */

                chatSendButton.classList.add(
                    "sending"
                );


                setTimeout(
                    function () {

                        chatSendButton.classList.remove(
                            "sending"
                        );

                    },
                    300
                );

            }
        );

    }

}


/* ============================================================
   ADD CHAT MESSAGE
   ============================================================ */

function addChatMessage(
    message,
    scroll = true
) {

    const chatMessages =
        document.getElementById(
            "chatMessages"
        );


    if (!chatMessages) {

        return;

    }


    /*
     * Empty state থাকলে সেটা সরিয়ে দেওয়া হবে।
     */

    const emptyState =
        chatMessages.querySelector(
            ".shsd-empty"
        );


    if (emptyState) {

        emptyState.remove();

    }


    /*
     * Message data নিরাপদভাবে তৈরি করা হচ্ছে।
     */

    const senderName =
        escapeHtml(
            message.name ||
            "User"
        );


    const messageText =
        escapeHtml(
            message.message ||
            ""
        );


    const role =
        escapeHtml(
            message.role ||
            "student"
        );


    const time =
        escapeHtml(
            message.time ||
            ""
        );


    /* ========================================================
       ROLE ICON
       ======================================================== */

    let roleIcon =
        "bi-person-fill";


    if (role === "admin") {

        roleIcon =
            "bi-shield-fill-check";

    } else if (role === "teacher") {

        roleIcon =
            "bi-person-workspace";

    } else {

        roleIcon =
            "bi-mortarboard-fill";

    }


    /* ========================================================
       MESSAGE ELEMENT
       ======================================================== */

    const messageElement =
        document.createElement(
            "div"
        );


    messageElement.className =
        "chat-message fade-up";


    messageElement.innerHTML = `

        <div class="chat-avatar">

            <i class="bi ${roleIcon}"></i>

        </div>


        <div class="chat-bubble">

            <div class="chat-sender">

                ${senderName}

            </div>


            <div class="chat-text">

                ${messageText}

            </div>


            <div class="chat-time">

                ${time}

            </div>

        </div>

    `;


    chatMessages.appendChild(
        messageElement
    );


    /*
     * নতুন message এলে নিচে scroll করা হবে।
     */

    if (scroll) {

        scrollChatToBottom();

    }

}


/* ============================================================
   CHAT EMPTY STATE
   ============================================================ */

function showChatEmptyState() {

    const chatMessages =
        document.getElementById(
            "chatMessages"
        );


    if (!chatMessages) {

        return;

    }


    chatMessages.innerHTML = `

        <div class="shsd-empty">

            <div class="shsd-empty-icon">

                <i class="bi bi-chat-dots"></i>

            </div>


            <h4>
                এখনো কোনো মেসেজ নেই
            </h4>


            <p>
                প্রথম মেসেজটি আপনিই পাঠান।
            </p>

        </div>

    `;

}


/* ============================================================
   CHAT SCROLL
   ============================================================ */

function scrollChatToBottom() {

    const chatMessages =
        document.getElementById(
            "chatMessages"
        );


    if (!chatMessages) {

        return;

    }


    /*
     * Smooth scroll করে সর্বশেষ message-এ যাওয়া।
     */

    chatMessages.scrollTo({

        top:
            chatMessages.scrollHeight,

        behavior:
            "smooth"

    });

}


/* ============================================================
   CHAT CONNECTION STATUS
   ============================================================ */

function updateChatConnectionStatus(
    connected
) {

    const statusText =
        document.getElementById(
            "chatStatusText"
        );


    const statusDot =
        document.querySelector(
            ".chat-status-dot"
        );


    if (!statusText) {

        return;

    }


    if (connected) {

        statusText.textContent =
            "লাইভ • সবাই দেখতে পাচ্ছে";


        if (statusDot) {

            statusDot.style.background =
                "#2ee6a6";

        }

    } else {

        statusText.textContent =
            "সংযোগ বিচ্ছিন্ন";


        if (statusDot) {

            statusDot.style.background =
                "#ff5f70";

        }

    }

}


/* ============================================================
   FORM INITIALIZATION
   ============================================================ */

function initializeForms() {

    /*
     * যেসব form-এ data-confirm আছে
     * সেগুলো submit করার আগে confirmation চাইবে।
     */

    const confirmForms =
        document.querySelectorAll(
            "form[data-confirm]"
        );


    confirmForms.forEach(
        function (form) {

            form.addEventListener(
                "submit",
                function (event) {

                    const message =
                        form.dataset.confirm ||
                        "আপনি কি নিশ্চিত?";


                    const confirmed =
                        window.confirm(
                            message
                        );


                    if (!confirmed) {

                        event.preventDefault();

                    }

                }
            );

        }
    );


    /*
     * SMS textarea-এর character counter।
     */

    const smsTextarea =
        document.getElementById(
            "smsMessage"
        );


    const smsCounter =
        document.getElementById(
            "smsCounter"
        );


    if (
        smsTextarea &&
        smsCounter
    ) {

        updateCharacterCounter(
            smsTextarea,
            smsCounter
        );


        smsTextarea.addEventListener(
            "input",
            function () {

                updateCharacterCounter(
                    smsTextarea,
                    smsCounter
                );

            }
        );

    }

}


/* ============================================================
   CHARACTER COUNTER
   ============================================================ */

function updateCharacterCounter(
    textarea,
    counter
) {

    const currentLength =
        textarea.value.length;


    const maxLength =
        textarea.maxLength > 0
            ? textarea.maxLength
            : 1000;


    counter.textContent =
        `${currentLength}/${maxLength}`;


    /*
     * সীমার কাছে গেলে warning দেখানো হবে।
     */

    if (
        currentLength >
        maxLength * 0.9
    ) {

        counter.style.color =
            "#ffc857";

    } else {

        counter.style.color =
            "";

    }


    /*
     * Limit অতিক্রম করলে danger color।
     */

    if (
        currentLength >= maxLength
    ) {

        counter.style.color =
            "#ff5f70";

    }

}


/* ============================================================
   MOBILE NAVIGATION
   ============================================================ */

function initializeMobileNavigation() {

    const navbarLinks =
        document.querySelectorAll(
            ".navbar-collapse .nav-link"
        );


    navbarLinks.forEach(
        function (link) {

            link.addEventListener(
                "click",
                function () {

                    /*
                     * Mobile menu open থাকলে
                     * link click করার পরে menu বন্ধ হবে।
                     */

                    const navbar =
                        document.querySelector(
                            ".navbar-collapse.show"
                        );


                    if (!navbar) {

                        return;

                    }


                    const collapse =
                        bootstrap.Collapse
                        .getInstance(navbar);


                    if (collapse) {

                        collapse.hide();

                    }

                }
            );

        }
    );

}


/* ============================================================
   LOCAL NOTIFICATION
   ============================================================ */

function showLocalNotification(
    message,
    type = "info"
) {

    /*
     * JavaScript থেকে ছোট notification
     * দেখানোর জন্য এই function।
     */

    const container =
        document.querySelector(
            ".shsd-alert-container"
        );


    if (!container) {

        return;

    }


    let icon =
        "bi-info-circle-fill";


    if (type === "success") {

        icon =
            "bi-check-circle-fill";

    } else if (type === "warning") {

        icon =
            "bi-exclamation-circle-fill";

    } else if (type === "danger") {

        icon =
            "bi-exclamation-triangle-fill";

    }


    const alertElement =
        document.createElement(
            "div"
        );


    alertElement.className =
        `alert shsd-alert alert-${type} fade show`;


    alertElement.setAttribute(
        "role",
        "alert"
    );


    alertElement.innerHTML = `

        <i class="bi ${icon}"></i>

        <span>
            ${escapeHtml(message)}
        </span>

        <button
            type="button"
            class="btn-close"
            data-bs-dismiss="alert"
            aria-label="Close"
        ></button>

    `;


    container.appendChild(
        alertElement
    );


    /*
     * কয়েক সেকেন্ড পরে notification
     * নিজে থেকেই চলে যাবে।
     */

    setTimeout(
        function () {

            const alert =
                bootstrap.Alert
                .getOrCreateInstance(
                    alertElement
                );


            alert.close();

        },
        4500
    );

}


/* ============================================================
   SAFE HTML ESCAPE
   ============================================================ */

function escapeHtml(value) {

    /*
     * User-এর message সরাসরি innerHTML-এ দেওয়ার আগে
     * HTML special character escape করা হচ্ছে।
     *
     * এতে malicious HTML/Script inject করা কঠিন হবে।
     */

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        String(value);


    return div.innerHTML;

}


/* ============================================================
   GLOBAL COPY FUNCTION
   ============================================================ */

function copyText(text) {

    /*
     * কোনো প্রয়োজন হলে এই function
     * clipboard-এ text copy করবে।
     */

    if (
        !navigator.clipboard
    ) {

        showLocalNotification(
            "আপনার browser copy support করছে না।",
            "warning"
        );

        return;

    }


    navigator.clipboard
        .writeText(text)
        .then(
            function () {

                showLocalNotification(
                    "কপি করা হয়েছে।",
                    "success"
                );

            }
        )
        .catch(
            function () {

                showLocalNotification(
                    "কপি করা যায়নি।",
                    "danger"
                );

            }
        );

}


/* ============================================================
   PASSWORD SHOW / HIDE
   ============================================================ */

function togglePassword(
    inputId,
    button
) {

    const input =
        document.getElementById(
            inputId
        );


    if (!input) {

        return;

    }


    if (
        input.type === "password"
    ) {

        input.type =
            "text";


        if (button) {

            button.innerHTML =
                '<i class="bi bi-eye-slash"></i>';

        }

    } else {

        input.type =
            "password";


        if (button) {

            button.innerHTML =
                '<i class="bi bi-eye"></i>';

        }

    }

}


/* ============================================================
   PAGE LOADER
   ============================================================ */

window.addEventListener(
    "beforeunload",
    function () {

        /*
         * Page change করার সময়
         * ছোট visual feedback।
         *
         * Browser unload হলে সবসময় দেখাবে না,
         * তাই এটি optional রাখা হয়েছে।
         */

    }
);


/* ============================================================
   CONSOLE MESSAGE
   ============================================================ */

console.log(
    "%cSHSD Link",
    "color:#39d9ff;font-size:22px;font-weight:bold;"
);


console.log(
    "%cSchool Communication System",
    "color:#9aabc0;font-size:12px;"
);


/* ============================================================
   END OF PART 8
   ============================================================ */
