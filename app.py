import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import difflib
import time
import os
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Students Solution - Assessment", layout="centered")

# --- GLOBAL PREMIUM MODERN CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    * { font-family: 'Poppins', sans-serif !important; }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
    }
    
    /* ======== INVISIBLE TEXT FIX ======== */
    .block-container p, 
    .block-container span, 
    .block-container label, 
    div[data-testid="stMarkdownContainer"] p {
        color: #2c3e50 !important;
    }
    
    /* ======== STRICT HIDE "PRESS ENTER" ======== */
    [data-testid="InputInstructions"], 
    div[data-testid="InputInstructions"],
    .stTextArea [data-testid="InputInstructions"],
    .stTextInput [data-testid="InputInstructions"] {
        display: none !important; visibility: hidden !important; opacity: 0 !important;
    }
    .stTextArea small, .stTextInput small { display: none !important; }
    
    /* ======== ANTI-CHEAT: UNSELECTABLE REFERENCE TEXT ======== */
    .typing-reference {
        font-size: 1.15rem !important;
        line-height: 1.8 !important;
        font-weight: 500 !important;
        color: #2c3e50 !important;
        background-color: #e8f4f8 !important;
        padding: 20px 25px !important;
        border-radius: 12px !important;
        border-left: 6px solid #ff2828 !important;
        margin-bottom: 15px !important;
        user-select: none !important; 
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
    }
    /* ==================================================================== */

    h3 { color: #2c3e50 !important; font-weight: 600 !important; letter-spacing: -0.5px !important; margin-top: 0 !important; padding-top: 0 !important;}
    h4 { font-weight: 500 !important; }
    
    .stTextInput > div > div > input {
        border-radius: 12px !important; border: 2px solid #e1e8ed !important; padding: 16px 20px !important;
        font-size: 15px !important; background-color: #f8f9fa !important; transition: all 0.3s ease !important;
        text-align: center !important; 
        color: #2c3e50 !important;
        caret-color: #ff2828 !important;
    }
    .stTextInput > div > div > input:focus { border-color: #ff2828 !important; background-color: #ffffff !important; box-shadow: 0 0 0 4px rgba(255, 40, 40, 0.1) !important; }
    
    /* ======== PRIMARY BUTTON STYLING ======== */
    button[kind="primary"], button[data-testid="baseButton-primary"] {
        background: linear-gradient(45deg, #ff2828, #ff4d4d) !important; color: white !important; border-radius: 12px !important;
        font-weight: 600 !important; letter-spacing: 0.5px !important; font-size: 16px !important; padding: 14px !important;
        border: none !important; box-shadow: 0 4px 15px rgba(255, 40, 40, 0.25) !important; transition: all 0.3s ease !important;
    }
    button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover { transform: translateY(-3px) !important; box-shadow: 0 8px 25px rgba(255, 40, 40, 0.35) !important; }
    button[kind="primary"] p, button[data-testid="baseButton-primary"] p { color: white !important; }
    
    /* ======== SECONDARY BUTTON STYLING (PERMANENT GREY) ======== */
    button[kind="secondary"], button[data-testid="baseButton-secondary"] {
        background: transparent !important; color: #7f8c8d !important; border-radius: 12px !important;
        font-weight: 600 !important; font-size: 16px !important; padding: 14px !important;
        border: 2px solid #dcdde1 !important; box-shadow: none !important; opacity: 0.6 !important; transition: all 0.3s ease !important;
    }
    button[kind="secondary"]:hover, button[data-testid="baseButton-secondary"]:hover { opacity: 1 !important; background: #f1f3f5 !important; border-color: #95a5a6 !important; }
    button[kind="secondary"] p, button[data-testid="baseButton-secondary"] p { color: #7f8c8d !important; }

    .stTabs [data-baseweb="tab-list"] { gap: 8px; padding-bottom: 5px; }
    .stTabs [data-baseweb="tab"] { background-color: #f1f3f5; border-radius: 8px; padding: 10px 18px; color: #495057 !important; font-weight: 500; border: none; }
    .stTabs [aria-selected="true"] { background-color: #ff2828 !important; color: white !important; box-shadow: 0 4px 10px rgba(255, 40, 40, 0.2) !important; }

    .stTextArea textarea { 
        border-radius: 12px !important; border: 2px solid #e1e8ed !important; padding: 15px !important; 
        background-color: #fbfbfc !important; 
        color: #2c3e50 !important; 
        caret-color: #ff2828 !important;
    }
    .stTextArea textarea:focus { border-color: #ff2828 !important; box-shadow: 0 0 0 4px rgba(255, 40, 40, 0.1) !important; }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURATION & CREDENTIALS ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
    SENDER_APP_PASSWORD = st.secrets["SENDER_APP_PASSWORD"]
except KeyError as e:
    st.error(f"System Configuration Error: Missing {e} in the secrets file.")
    st.stop()

RECEIVER_EMAIL = "muhammadshamikh724@gmail.com"

# --- AI API SETUP ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- PARAGRAPH BANK ---
typing_paragraphs = [
    "Welcome to the typing test. As an office assistant, your main tasks will include answering phone calls, organizing files, and responding to emails. Good typing speed helps you finish your work faster and with fewer mistakes. Please type carefully and pay attention to spelling and punctuation. We are glad to have you take this test today. Take a deep breath, focus on the screen, and do your best. Good luck with your assessment!",
    "Effective communication is a vital skill in any professional environment. Writing clear and concise emails ensures that your message is understood by clients and colleagues alike. When drafting corporate documents, formatting is just as important as the content. Attention to detail can save the company time and prevent unnecessary misunderstandings. Always proofread your work before hitting the send button.",
    "Time management and organizational skills are essential for success in this role. You will be expected to handle multiple tasks efficiently, such as scheduling meetings, maintaining digital records, and managing daily correspondence. Prioritizing your workload will help you stay focused during busy office hours. A reliable assistant keeps the entire team running smoothly and effectively without missing any deadlines.",
    "Customer service is the heart of our business. Whenever you interact with clients, it is important to maintain a polite and professional tone. Listening carefully to their requests allows you to provide the best possible solutions. Remember that you represent the company's image with every email you send and every call you receive. Consistency and empathy are the keys to building long-lasting client relationships."
]

# --- MCQ DATA (YAHAN MISSING THA, AB WAPAS AAGAYA) ---
mcq_data = [
    {"q": "1. What is the default font used in MS Word (2007 and later)?", "options": ["Times New Roman", "Arial", "Calibri", "Comic Sans"], "answer": "Calibri"},
    {"q": "2. In MS Word, which feature allows you to create a list with dots or symbols?", "options": ["Numbering", "Bullets", "Indentation", "Margins"], "answer": "Bullets"},
    {"q": "3. What is the keyboard shortcut for 'Undo' in MS Office applications?", "options": ["Ctrl + U", "Ctrl + Z", "Ctrl + Y", "Ctrl + X"], "answer": "Ctrl + Z"},
    {"q": "4. In MS Word, what is the shortcut key to 'Copy' selected text?", "options": ["Ctrl + C", "Ctrl + X", "Ctrl + P", "Ctrl + V"], "answer": "Ctrl + C"},
    {"q": "5. Which feature is used in MS Word to send the same letter to multiple people automatically?", "options": ["Macros", "Template", "Mail Merge", "AutoCorrect"], "answer": "Mail Merge"},
    {"q": "6. What is the shortcut key for 'Center Alignment' in MS Word?", "options": ["Ctrl + C", "Ctrl + E", "Ctrl + A", "Ctrl + J"], "answer": "Ctrl + E"},
    {"q": "7. Which key is used to check spelling and grammar in MS Word?", "options": ["F5", "F7", "F12", "F2"], "answer": "F7"},
    {"q": "8. In MS Word, what is the shortcut for inserting a Page Break?", "options": ["Ctrl + Enter", "Shift + Enter", "Alt + Enter", "Space + Enter"], "answer": "Ctrl + Enter"},
    {"q": "9. Which tab in MS Word contains the 'Watermark' option?", "options": ["Home", "Insert", "Design", "View"], "answer": "Design"},
    {"q": "10. What is the keyboard shortcut to make text Bold in MS Word?", "options": ["Ctrl + B", "Shift + B", "Alt + B", "Tab + B"], "answer": "Ctrl + B"},
    {"q": "11. In MS Excel, all formulas must begin with which symbol?", "options": ["+", "@", "=", "#"], "answer": "="},
    {"q": "12. What is the intersection of a row and a column in MS Excel called?", "options": ["Box", "Cell", "Grid", "Table"], "answer": "Cell"},
    {"q": "13. In MS Excel, which function is used to add all numbers in a selected range?", "options": ["TOTAL()", "COUNT()", "SUM()", "ADD()"], "answer": "SUM()"},
    {"q": "14. What is the primary purpose of the VLOOKUP function in Excel?", "options": ["To find related data in a table", "To change text to uppercase", "To create a chart", "To sum vertical cells only"], "answer": "To find related data in a table"},
    {"q": "15. What is the shortcut to select an entire column in MS Excel?", "options": ["Ctrl + Space", "Shift + Space", "Ctrl + A", "Alt + Space"], "answer": "Ctrl + Space"},
    {"q": "16. What is the standard file extension for a modern MS Excel workbook?", "options": [".doc", ".xls", ".xlsx", ".pdf"], "answer": ".xlsx"},
    {"q": "17. In MS Excel, how can you freeze the top row of a spreadsheet so it stays visible while scrolling?", "options": ["Home Tab -> Freeze", "View Tab -> Freeze Panes", "Insert Tab -> Lock Row", "Data Tab -> Freeze"], "answer": "View Tab -> Freeze Panes"},
    {"q": "18. Which feature in MS Excel automatically fills a series of data (like days of the week or months)?", "options": ["AutoSum", "AutoFill", "AutoFormat", "AutoComplete"], "answer": "AutoFill"},
    {"q": "19. What is the shortcut key to insert a new worksheet in MS Excel?", "options": ["Shift + F11", "Ctrl + N", "Alt + W", "F12"], "answer": "Shift + F11"},
    {"q": "20. How do you wrap text within a single cell in MS Excel so it fits nicely?", "options": ["Format Cells -> Wrap Text", "View -> Wrap", "Insert -> Text Wrap", "Data -> Wrap"], "answer": "Format Cells -> Wrap Text"}
]

# --- SESSION STATE INITIALIZATION ---
if "test_started" not in st.session_state: st.session_state.test_started = False
if "candidate_name" not in st.session_state: st.session_state.candidate_name = ""
if "typing_started" not in st.session_state: st.session_state.typing_started = False
if "start_time" not in st.session_state: st.session_state.start_time = 0
if "show_confirm" not in st.session_state: st.session_state.show_confirm = False
if "assigned_paragraph" not in st.session_state: st.session_state.assigned_paragraph = ""
if "final_typing_time" not in st.session_state: st.session_state.final_typing_time = 0 

# --- HELPER FUNCTIONS ---
def calculate_typing_accuracy(original, typed):
    if not typed: return 0.0
    matcher = difflib.SequenceMatcher(None, original.strip(), typed.strip())
    return round(matcher.ratio() * 100, 2)

def calculate_wpm(typed_text, elapsed_seconds):
    if elapsed_seconds <= 0: elapsed_seconds = 1 
    words = len(typed_text.split())
    minutes = elapsed_seconds / 60.0
    return round(words / minutes)

def check_answers_with_ai(email_ans, forward_ans):
    prompt = f"""
    You are an expert, empathetic HR Manager evaluating an office assistant candidate. 
    IMPORTANT EVALUATION RULES:
    1. The candidate may answer in English or Roman Urdu (e.g., "setting me ja kar email forward karden"). Accept both.
    2. Focus ONLY on the core concept and whether they understand the task.
    3. Be lenient. Completely IGNORE grammar, spelling mistakes, or unprofessional formatting. Do not deduct marks for poor grammar if the intended meaning is clear.
    
    Evaluate the two answers below but DO NOT repeat the candidate's text in your response. 
    Only provide a score out of 10 and a strictly 1-line short feedback for each.
    
    Candidate's Answers:
    1. Client Email Draft: {email_ans}
    2. Gmail Forwarding Process: {forward_ans}
    
    Format output strictly as:
    - Email Drafting: [Score]/10 - [1-line feedback]
    - Mail Forwarding: [Score]/10 - [1-line feedback]
    - Overall Written Score: [Score]/10
    """
    return model.generate_content(prompt).text

def send_email_to_boss(candidate_name, typing_score, wpm, time_taken_sec, mcq_score, ai_report):
    subject = f"Assessment Report: {candidate_name} - Students Solution"
    clean_report = ai_report.replace('**', '')
    minutes_taken, seconds_taken = int(time_taken_sec // 60), int(time_taken_sec % 60)
    
    body = f"""Candidate Name: {candidate_name}\n\nObjective Test Results:\n- Basic Software MCQs: {mcq_score} / 20\n\nTyping Test Results (Out of 3 Minutes limit):\n- Accuracy: {typing_score}%\n- Speed: {wpm} WPM\n- Time Taken: {minutes_taken} minutes and {seconds_taken} seconds\n\nAI Evaluation (Practical Tasks):\n{clean_report}"""
    msg = MIMEMultipart()
    msg['From'], msg['To'], msg['Subject'] = SENDER_EMAIL, RECEIVER_EMAIL, subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        return "Success"
    except Exception as e: 
        return str(e) 

# --- MAIN APP LOGIC ---
if not st.session_state.test_started:
    st.markdown("""
        <style>
        .block-container {
            background: rgba(255, 255, 255, 0.95); border-radius: 20px;
            padding: 3rem !important; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
            margin: 0 auto !important; margin-top: 8vh !important; margin-bottom: 8vh !important;
            max-width: 750px !important;
        }
        [data-testid="stImage"] { display: flex; justify-content: center; }
        </style>
    """, unsafe_allow_html=True)
    
    logo_col1, logo_col2, logo_col3 = st.columns([1, 1, 1]) 
    with logo_col2:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
            
    st.markdown("<h3 style='text-align: center; color: #7f8c8d !important;'>Candidate Assessment Portal</h3>", unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)
    
    input_col1, input_col2, input_col3 = st.columns([1, 2, 1])
    with input_col2:
        st.markdown("<div style='text-align: center; font-weight: 500; margin-bottom: 5px; color: #495057;'>Enter Your Full Name to Begin:</div>", unsafe_allow_html=True)
        name_input = st.text_input("Name", placeholder="E.g., Muhammad Shamikh", label_visibility="collapsed")
        st.write("<br>", unsafe_allow_html=True) 
        if st.button("Start Assessment", type="primary", use_container_width=True):
            if name_input.strip() == "": st.error("Please enter your name first.")
            else:
                st.session_state.candidate_name = name_input
                st.session_state.test_started = True
                st.session_state.assigned_paragraph = random.choice(typing_paragraphs)
                st.session_state.final_typing_time = 0 
                st.rerun()

else:
    st.markdown("""
        <style>
        .block-container {
            background: rgba(255, 255, 255, 0.95); border-radius: 20px;
            padding: 2rem 2.5rem 2.5rem 2.5rem !important;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
            margin: 0 auto !important; 
            margin-top: 2vh !important; 
            max-width: 850px !important; 
        }
        [data-testid="stImage"] img {
            object-fit: fill !important;   
            width: 100% !important;        
            height: 120px !important; 
        }
        [data-testid="stImage"] {
            display: flex; justify-content: flex-end; align-items: center; 
        }
        </style>
    """, unsafe_allow_html=True)

    header_col1, header_col2 = st.columns([5.5, 1.5], gap="small")
    
    with header_col1:
        st.markdown(f"""
            <div style='display: flex; align-items: center; height: 120px;'>
                <h3 style='margin: 0 !important; padding: 0 !important;'>Welcome, {st.session_state.candidate_name}</h3>
            </div>
        """, unsafe_allow_html=True)
    
    with header_col2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            st.markdown("<h4 style='color:#ff2828; text-align:right;'>Students Solution</h4>", unsafe_allow_html=True)
        
    st.markdown("<hr style='margin: 10px 0px 15px 0px; border: none; border-bottom: 3px solid #ff2828;'>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Typing Test", "MCQs", "Email Drafting", "Mail Forwarding"])

    with tab1:
        st.write("#### Typing Assessment (3 Minutes)")
        st.write("*Note: Type the text, then click anywhere outside the box to update your progress.*")
        if not st.session_state.typing_started:
            st.info("Click the button below to start the timer. The text will appear, and you will have 3 minutes to type it accurately.")
            if st.button("Start Typing Test", type="primary"):
                st.session_state.typing_started = True
                st.session_state.start_time = time.time()
                st.rerun()
        
        typing_input = ""
        if st.session_state.typing_started:
            col_a, col_b = st.columns([3, 1])
            with col_a: st.write("**Type the text below exactly as it appears:**")
            with col_b:
                target_length = len(st.session_state.assigned_paragraph) - 50 
                
                if st.session_state.final_typing_time > 0:
                    time_left_sec = int(180 - st.session_state.final_typing_time)
                    is_already_done = "true"
                else:
                    time_left_sec = int(180 - (time.time() - st.session_state.start_time))
                    is_already_done = "false"
                if time_left_sec < 0: time_left_sec = 0

                timer_html = f"""
                <div style="text-align: center; font-size: 20px; font-weight: bold; color: white; background: #ff2828; padding: 5px; border-radius: 8px;">
                    Time: <span id="timer">...</span>
                </div>
                <script>
                    var timeLeft = {time_left_sec};
                    var isAlreadyDone = {is_already_done};
                    var targetLen = {target_length};

                    function formatTime(t) {{
                        var m = Math.floor(t / 60); var s = t % 60;
                        return (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
                    }}

                    // --- ANTI CHEAT SYSTEM ---
                    try {{
                        var textAreas = window.parent.document.querySelectorAll('textarea');
                        if (textAreas.length > 
