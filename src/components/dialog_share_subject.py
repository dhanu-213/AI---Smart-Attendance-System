import streamlit as st

import segno
import io

@st.dialog("Share Class Link")
def share_subject_dialog(subject_name,subject_code):
    app_domain="snapclass-main.streamlit.app"
    join_url=f"{app_domain}/join-code={subject_code}"

    st.header("scan to join")

    qr = segno.make(join_url)

    out = io.BytesIO()

    qr.save(out,kind='png',scale=10,border=1)

    col1,col2=st.columns(2)

    with col1:
        st.markdown('### copy Link')
        st.code(join_url,language="text")
        st.code(subject_code,language="text")
        st.info('Copy this link to share on whatsapp or Email')

    with col2:
        st.markdown('### Scan to join')
        st.image(out.getvalue(),caption='QRCODE for class joining')    


