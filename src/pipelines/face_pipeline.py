import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students


@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec=dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector,sp,facerec


def get_face_embeddings(image_np):
    detector,sp,facerec = load_dlib_models()
    faces = detector(image_np,1)


    encodings = []

    for face in faces:
        shape = sp(image_np,face)
        face_descriptor = facerec.compute_face_descriptor(image_np,shape,1)

        encodings.append(np.array(face_descriptor))

    return encodings

@st.cache_resource
def get_trained_model():
    X= []
    y= [] 

    student_db = get_all_students()

    if not student_db:
        return None

    for student in student_db:
        embedding = student.get('face_embedding')
        if embedding:
            X.append(np.array(embedding))
            y.append(student.get('student_id'))

    if len(X) ==0:
        return 0

    clf = SVC(kernel='linear',probability=True,class_weight='balanced')


    try:
        clf.fit(X,y)
    except ValueError:
        pass 

    return{'clf':clf,'X':X,'y':y}   


def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)


def predict_attendence(class_image_np):
    encodings = get_face_embeddings(class_image_np)

    detected_student={}

    model_data=get_trained_model()

    if not model_data:
        return detected_student,[],len(encodings)


    clf = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']


    all_students=sorted(list(set(y_train)))

    for encoding in encodings:
        if len(all_students)>=2:
            predicted_id =int(clf.predict([encoding])[0])
        else:
            predicted_id = int(all_students[0])    
        
        

        student_embedding = X_train[y_train.index(predicted_id)] 

        best_match_score = np.linalg.norm(student_embedding-encoding)

        resembalence_threshold = 0.6

        if best_match_score <= resembalence_threshold:
            detected_student[predicted_id] = True

    return detected_student,all_students,len(encodings)



# import dlib
# import numpy as np
# import face_recognition_models
# from sklearn.svm import SVC
# import streamlit as st

# from src.database.db import get_all_students


# # =========================================================
# # LOAD DLIB FACE MODELS
# # =========================================================

# @st.cache_resource
# def load_dlib_models():

#     detector = dlib.get_frontal_face_detector()

#     sp = dlib.shape_predictor(
#         face_recognition_models.pose_predictor_model_location()
#     )

#     facerec = dlib.face_recognition_model_v1(
#         face_recognition_models.face_recognition_model_location()
#     )

#     return detector, sp, facerec


# # =========================================================
# # GET FACE EMBEDDINGS
# # =========================================================

# def get_face_embeddings(image_np):

#     detector, sp, facerec = load_dlib_models()

#     # Make sure image is uint8
#     image_np = np.asarray(image_np, dtype=np.uint8)

#     faces = detector(image_np, 1)

#     encodings = []

#     for face in faces:

#         try:
#             shape = sp(image_np, face)

#             face_descriptor = facerec.compute_face_descriptor(
#                 image_np,
#                 shape,
#                 1
#             )

#             encoding = np.array(face_descriptor, dtype=np.float64)

#             # dlib face embedding must contain 128 values
#             if encoding.shape == (128,):
#                 encodings.append(encoding)

#         except Exception as e:
#             print("Face embedding error:", e)

#     return encodings


# # =========================================================
# # TRAIN CLASSIFIER
# # =========================================================

# @st.cache_resource
# def get_trained_model():

#     X = []
#     y = []

#     student_db = get_all_students()

#     print("DEBUG - Students from DB:", student_db)

#     # No students registered yet
#     if not student_db:
#         print("DEBUG - No students found in database")
#         return None

#     for student in student_db:

#         embedding = student.get("face_embedding")

#         if embedding is None:
#             continue

#         if isinstance(embedding, list) and len(embedding) == 128:

#             X.append(
#                 np.array(embedding, dtype=np.float64)
#             )

#             y.append(
#                 int(student["student_id"])
#             )

#     print("DEBUG - Number of embeddings:", len(X))
#     print("DEBUG - Student IDs:", y)

#     # No valid face embeddings
#     if len(X) == 0:
#         print("DEBUG - No valid face embeddings")
#         return None

#     # =====================================================
#     # IMPORTANT:
#     # SVM requires at least 2 different classes.
#     # If only one student exists, don't train SVM.
#     # =====================================================

#     unique_ids = list(set(y))

#     if len(unique_ids) < 2:

#         print(
#             "DEBUG - Only one student registered. "
#             "Using direct face distance matching."
#         )

#         return {
#             "clf": None,
#             "X": X,
#             "y": y
#         }

#     # =====================================================
#     # TRAIN SVM
#     # =====================================================

#     clf = SVC(
#         kernel="linear",
#         probability=True,
#         class_weight="balanced"
#     )

#     try:

#         clf.fit(X, y)

#     except Exception as e:

#         print("SVM training error:", e)
#         return None

#     return {
#         "clf": clf,
#         "X": X,
#         "y": y
#     }


# # =========================================================
# # CLEAR / RETRAIN MODEL
# # =========================================================

# def train_classifier():

#     st.cache_resource.clear()

#     model_data = get_trained_model()

#     return model_data is not None


# # =========================================================
# # FACE PREDICTION
# # =========================================================

# def predict_attendence(class_image_np):

#     detected_student = {}

#     # -----------------------------------------------------
#     # Step 1: Get face embeddings from camera image
#     # -----------------------------------------------------

#     encodings = get_face_embeddings(class_image_np)

#     print("DEBUG - Number of faces:", len(encodings))

#     # No face
#     if len(encodings) == 0:

#         return detected_student, [], 0

#     # -----------------------------------------------------
#     # Step 2: Load registered students
#     # -----------------------------------------------------

#     model_data = get_trained_model()

#     # No students registered
#     if model_data is None:

#         print("DEBUG - No trained face model")

#         return detected_student, [], len(encodings)

#     X_train = model_data["X"]
#     y_train = model_data["y"]
#     clf = model_data["clf"]

#     all_students = sorted(
#         list(set(y_train))
#     )

#     print("DEBUG - All IDs:", all_students)

#     # -----------------------------------------------------
#     # Step 3: Match each detected face
#     # -----------------------------------------------------

#     for encoding in encodings:

#         # =================================================
#         # CASE 1:
#         # Only one student exists
#         # =================================================

#         if len(all_students) == 1:

#             student_id = all_students[0]

#             index = y_train.index(student_id)

#             stored_embedding = X_train[index]

#             distance = np.linalg.norm(
#                 stored_embedding - encoding
#             )

#             print(
#                 f"DEBUG - Student {student_id} "
#                 f"face distance: {distance}"
#             )

#             # Face recognition threshold
#             threshold = 0.45

#             if distance <= threshold:

#                 detected_student[
#                     int(student_id)
#                 ] = True

#         # =================================================
#         # CASE 2:
#         # Multiple students exist
#         # =================================================

#         else:

#             predicted_id = int(
#                 clf.predict([encoding])[0]
#             )

#             # Find predicted student's embedding
#             indexes = [
#                 i for i, value in enumerate(y_train)
#                 if value == predicted_id
#             ]

#             if indexes:

#                 # Use first stored embedding
#                 stored_embedding = X_train[indexes[0]]

#                 distance = np.linalg.norm(
#                     stored_embedding - encoding
#                 )

#                 print(
#                     f"DEBUG - Predicted student: "
#                     f"{predicted_id}"
#                 )

#                 print(
#                     f"DEBUG - Face distance: "
#                     f"{distance}"
#                 )

#                 threshold = 0.45

#                 if distance <= threshold:

#                     detected_student[
#                         predicted_id
#                     ] = True

#     print(
#         "DEBUG - Detected:",
#         detected_student
#     )

#     return (
#         detected_student,
#         all_students,
#         len(encodings)
#     )

