 # 📸 AI Smart Attendance System

An AI-powered attendance system that marks attendance **from a classroom photo or a voice recording** instead of manual roll call. Teachers create subjects and take attendance in seconds; students log in with **Face ID** and track their own attendance.

Built with **Streamlit**, **dlib** (face recognition), **Resemblyzer** (voice recognition) and **Supabase** (database).

---

## ✨ Features

### 👩‍🏫 Teacher
- Register / log in with username and password (passwords are hashed with **bcrypt**)
- Create subjects (subject code, name, section)
- Share a subject through a **join link and QR code**
- **Face attendance** – capture or upload one or more classroom photos; every face is detected and matched with enrolled students
- **Voice attendance** – record the class saying "I am present"; each speaker is identified from their voice
- Review the result table and confirm before saving (Discard / Confirm and save)
- View attendance records session by session (present / total students)

### 🎓 Student
- **Face ID login** – no password needed
- Automatic **new-profile registration** if the face is not recognised (name + face, optional voice enrollment)
- Enroll in a subject using a subject code, or instantly via the QR / join link
- Dashboard showing every enrolled subject with **total classes vs. classes attended**
- Unenroll from a subject

---

## 🧠 How It Works

### Face recognition pipeline
1. **Detect** faces with dlib's HOG-based frontal face detector
2. **Align** using the 68-point shape predictor
3. **Embed** each face into a **128-dimensional vector** with dlib's ResNet face recognition model
4. **Classify** the embedding with a **Support Vector Classifier** (linear kernel) trained on all registered students
5. **Verify** the prediction with a Euclidean-distance threshold (`0.6`) so unknown faces are rejected

### Voice recognition pipeline
1. Load audio at 16 kHz with **librosa**
2. Split the recording into speech segments on silence (`librosa.effects.split`) and ignore very short segments
3. Create a speaker embedding for each segment with **Resemblyzer**
4. Compare with the voice embeddings of students enrolled in that subject using **similarity score** (threshold `0.65`)

### Attendance flow
```
Teacher selects subject  ──►  adds photos / records audio
        │
        ▼
 AI detects & identifies students
        │
        ▼
 Teacher reviews results  ──►  Confirm  ──►  saved to Supabase
```

---

## 🛠️ Tech Stack

| Area | Technology |
|------|------------|
| Frontend / App framework | Streamlit |
| Face recognition | dlib, face_recognition_models, scikit-learn (SVC) |
| Voice recognition | Resemblyzer, librosa |
| Database | Supabase (PostgreSQL) |
| Security | bcrypt |
| Data handling | NumPy, Pandas, Pillow |
| QR code | segno |
| Language | Python |

---

## 📁 Project Structure

```
AI---Smart-Attendance-System/
├── app.py                          # Entry point – routes to home / student / teacher screens
├── requirements.txt
├── .gitignore
└── src/
    ├── components/                 # Reusable UI pieces and dialogs
    │   ├── dialog_add_photo.py
    │   ├── dialog_attendance_results.py
    │   ├── dialog_auto_enroll.py
    │   ├── dialog_create_subject.py
    │   ├── dialog_enroll.py
    │   ├── dialog_share_subject.py
    │   ├── dialog_voice_attendance.py
    │   ├── header.py / footer.py
    │   └── subject_card.py
    ├── database/
    │   ├── config.py               # Supabase client (reads Streamlit secrets)
    │   └── db.py                   # All database queries + password hashing
    ├── pipelines/
    │   ├── face_pipeline.py        # Face detection, embeddings, SVM training, prediction
    │   └── voice_pipeline.py       # Voice embeddings and speaker identification
    ├── screens/
    │   ├── home_screen.py
    │   ├── student_screen.py
    │   └── teacher_screen.py
    └── ui/
        └── base_layout.py          # Custom CSS styling
```

---

## 🗄️ Database (Supabase)

Create these tables in your Supabase project:

| Table | Columns used by the app |
|-------|-------------------------|
| `teachers` | `teacher_id`, `username`, `password` (bcrypt hash), `name` |
| `students` | `student_id`, `name`, `face_embedding`, `voice_embedding` |
| `subjects` | `subject_id`, `subject_code`, `name`, `section`, `teacher_id` |
| `subject_students` | `student_id`, `subject_id` |
| `attendence_logs` | `student_id`, `subject_id`, `timestamp`, `is_present` |

> The table name `attendence_logs` is spelled exactly as it is used in the code.

---

## 🚀 Getting Started

### Prerequisites
- Python **3.12 or newer**
- A free [Supabase](https://supabase.com) project
- A webcam / microphone (or image and audio files) for testing

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/AI---Smart-Attendance-System.git
cd AI---Smart-Attendance-System
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

`dlib-bin` is used so that dlib installs without compiling it from source.

### 4. Add your Supabase credentials
Create the file `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-supabase-key"
```

> `.streamlit/` and `.env` are already listed in `.gitignore`, so your keys will not be pushed to GitHub.

### 5. Run the app
```bash
streamlit run app.py
```

---

## 📖 Usage

1. **Teacher:** open the Teacher portal → register → log in → *Manage Subjects* → create a subject → share the code or QR with students.
2. **Student:** open the Student portal → look at the camera → register on first visit (name, optional voice sample) → enroll in the subject.
3. **Take attendance:** Teacher → *Take Attendance* → choose the subject → *Add Photos* → *Run face Analysis* (or *use voice attendance*) → review → *Confirm and save*.
4. **Check records:** Teacher → *attendance_records*; Student dashboard shows attended vs. total classes.

---

## ⚠️ Limitations

- Face login has no liveness detection, so a printed photo could be used to fool it
- Accuracy depends on lighting, camera angle and image quality
- Voice attendance works best in a quiet room with students speaking one at a time
- Each student is currently registered with a single face sample

## 🔮 Future Improvements

- Liveness / anti-spoofing check for Face ID
- Multiple face samples per student for better accuracy
- Export attendance reports to Excel / CSV
- Attendance percentage alerts for students
- Row Level Security policies on Supabase tables
- Live video attendance

---

## 👩‍💻 Author

**Dhanashri Vani**
B.Tech in Artificial Intelligence & Data Science

⭐ If you found this project useful, consider giving it a star!
