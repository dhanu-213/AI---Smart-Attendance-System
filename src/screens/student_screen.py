import streamlit as st 
from src.ui.base_layout import style_background_dashboard,style_base_layout
from src .components.header import header_dashboard
from src .components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendence,get_face_embeddings,train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students,create_student,get_student_subjects,get_student_attendance,unenroll_student_to_subjects
import time
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card

def student_dashboard():   
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    c1 , c2 = st.columns(2,vertical_alignment = 'center',gap='xxlarge')
    with c1:
        header_dashboard()
    with c2 : 
        st.subheader(f"""Welcome,{student_data['name']}""") 
        if st.button("Logout",type ='secondary',key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in']=False
            del st.session_state.student_data
            st.rerun()

    st.space()

    c1,c2 = st.columns(2)
    with c1 :
        st.header('Your Enrolled Subjects')

    with c2:
        if st.button('Enroll in subject',type='primary',width='stretch'):
            enroll_dialog()   

    st.divider()         


    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map={}  

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0,"attended":0}  

        stats_map[sid]['total']+=1

        if log.get('is_present'):
            stats_map[sid]['attended']+=1

    cols = st.columns(2) 
    for i ,sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']


        stats = stats_map.get(sid,{"total":0,"attended":0})
        def unenroll_button():
            if st.button("Unenroll from this course",type = 'tertiary',width='stretch',icon = ':material/delete_forever:'):
                unenroll_student_to_subjects(student_id,sid)
                st.toast(f'Unenrolled from {sub['name']}successfully!')
                st.rerun()
        
        with cols[i % 2]:     
            subject_card(
                name = sub['name'],
                code=sub['subject_code'],
                section = sub['section'],
                stats = [
                    ('','Total',stats['total']),
                    ('','Attended',stats['attended']),
                ],
                footer_callback=unenroll_button
            )     

    footer_dashboard()


def student_screen():

    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    # Header
    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )

    with c1:
        header_dashboard()

    with c2:
        if st.button(
            "GO back to Home",
            type="secondary",
            key="student_home_btn",
            shortcut="control+backspace"
        ):
            st.session_state["login_type"] = None
            st.rerun()

    st.header(
        "Login using Face_id",
        text_alignment="center"
    )

    st.space()
    st.space()

    # ==============================
    # FACE CAPTURE
    # ==============================

    photo_source = st.camera_input(
        "Position your face in the center"
    )

    if photo_source:

        img = np.array(
            Image.open(photo_source).convert("RGB")
        )

        # ==============================
        # AI SCREENING
        # ==============================

        with st.spinner("AI is screening..."):

            detected, all_ids, num_faces = predict_attendence(img)

        # ==============================
        # NO FACE
        # ==============================

        if num_faces == 0:

            st.warning("Face not found!")

        # ==============================
        # MULTIPLE FACES
        # ==============================

        elif num_faces > 1:

            st.warning("Multiple faces found!")

        # ==============================
        # ONE FACE
        # ==============================

        else:

            # ==============================
            # EXISTING STUDENT
            # ==============================

            if detected:

                student_id = list(
                    detected.keys()
                )[0]

                all_students = get_all_students()

                student = next(
                    (
                        s for s in all_students
                        if s["student_id"] == student_id
                    ),
                    None
                )

                if student:

                    st.session_state["is_logged_in"] = True
                    st.session_state["user_role"] = "student"
                    st.session_state["student_data"] = student

                    st.success(
                        f"Welcome back, {student['name']}!"
                    )

                    time.sleep(1)
                    st.rerun()

            # ==============================
            # NEW STUDENT
            # ==============================

            else:

                st.info(
                    "Face not recognized. "
                    "Please register as a new student."
                )

                st.divider()

                with st.container(border=True):

                    st.header("Register new profile")

                    new_name = st.text_input(
                        "Enter your name",
                        placeholder="E.g. Dhanashri Vani",
                        key="new_student_name"
                    )

                    st.subheader(
                        "Optional: Voice Enrollment"
                    )

                    st.info(
                        "Enroll your voice for voice-only attendance."
                    )

                    audio_data = None

                    try:

                        audio_data = st.audio_input(
                            "Record a short phrase like "
                            "'I am present, My name is Dhanashri.'",
                            key="voice_capture"
                        )

                    except Exception as e:

                        st.error(
                            f"Audio capture failed: {e}"
                        )

                    # ==============================
                    # CREATE ACCOUNT
                    # ==============================

                    if st.button(
                        "Create Account",
                        type="primary",
                        key="create_student_btn"
                    ):

                        if not new_name.strip():

                            st.warning(
                                "Please enter your name!"
                            )

                        else:

                            with st.spinner(
                                "Creating profile..."
                            ):

                                encodings = get_face_embeddings(img)

                                if not encodings:

                                    st.error(
                                        "Couldn't capture "
                                        "your facial features."
                                    )

                                else:

                                    face_emb = encodings[0].tolist()

                                    voice_emb = None

                                    if audio_data:

                                        try:

                                            voice_emb = get_voice_embedding(
                                                audio_data.read()
                                            )

                                        except Exception as e:

                                            st.warning(
                                                f"Voice enrollment skipped: {e}"
                                            )

                                    response_data = create_student(
                                        new_name.strip(),
                                        face_embedding=face_emb,
                                        voice_embedding=voice_emb
                                    )

                                    if response_data:

                                        train_classifier()

                                        st.success(
                                            f"Profile created successfully! "
                                            f"Hi {new_name.strip()}!"
                                        )

                                        st.session_state[
                                            "is_logged_in"
                                        ] = True

                                        st.session_state[
                                            "user_role"
                                        ] = "student"

                                        st.session_state[
                                            "student_data"
                                        ] = response_data[0]

                                        time.sleep(1)

                                        st.rerun()

                                    else:

                                        st.error(
                                            "Student profile could not "
                                            "be created in database."
                                        )

    footer_dashboard()



