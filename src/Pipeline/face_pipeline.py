import dlib 
import numpy as np
import face_recognition_models
# from sklearn.svm import SVC
import streamlit as st
from src.Database.db import get_all_students, create_student


@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    face_recognition = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, face_recognition


def get_face_embedding(image_np):
    detector, sp, face_recognition = load_dlib_models()

    faces = detector(image_np, 1)
    encodings = []

    for face in faces:
        shape = sp(image_np, face)

        face_descriptor = face_recognition.compute_face_descriptor(
            image_np,
            shape,
            1
        )

        encodings.append(np.array(face_descriptor))

    return encodings


@st.cache_resource
def get_trained_model():
    from sklearn.svm import SVC
    X = []
    y = []

    students_db = get_all_students()

    if not students_db:
        return None

    for student in students_db:

        embeddings = student.get('face_embedding')

        if embeddings:

            embedding = np.array(
                embeddings,
                dtype=np.float64
            ).flatten()

            if len(embedding) == 128:
                X.append(embedding)
                y.append(student.get('student_id'))

    if len(X) == 0:
        return None

    if len(set(y)) < 2:
        return {
            'clf': None,
            'X': X,
            'y': y
        }

    clf = SVC(
        kernel='linear',
        probability=True,
        class_weight='balanced'
    )

    try:
        clf.fit(X, y)
    except ValueError:
        return None

    return {
        'clf': clf,
        'X': X,
        'y': y
    }


def train_classifier():
    st.cache_resource.clear()

    model_data = get_trained_model()

    return bool(model_data)


def predict_attendance(image_np):
    encodings = get_face_embedding(image_np)

    detected_students = {}

    model_data = get_trained_model()

    if not model_data:
        return {}, [], len(encodings)

    clf = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']

    all_students = sorted(list(set(y_train)))

    for encoding in encodings:

        encoding = np.array(
            encoding,
            dtype=np.float64
        ).flatten()

        if len(all_students) == 1:

            predicted_id = all_students[0]

        else:

            predicted_id = clf.predict([encoding])[0]

        predicted_id = int(predicted_id)

        student_indexes = [
            i
            for i, sid in enumerate(y_train)
            if sid == predicted_id
        ]

        best_match_score = float('inf')

        for index in student_indexes:

            student_embedding = np.array(
                X_train[index],
                dtype=np.float64
            ).flatten()

            distance = np.linalg.norm(
                student_embedding - encoding
            )

            if distance < best_match_score:
                best_match_score = distance

        resemblance_threshold = 0.6

        if best_match_score < resemblance_threshold:
            detected_students[predicted_id] = True

    return detected_students, all_students, len(encodings)