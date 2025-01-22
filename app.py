import streamlit as st
import os
import onnx
import onnxruntime as ort
import numpy as np
import cv2
from PIL import Image

# Konfigurasi direktori unggahan
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Muat model ONNX
MODEL_PATH = 'my_model.onnx'  # Ganti dengan path model ONNX Anda
onnx_model = onnx.load(MODEL_PATH)
onnx.checker.check_model(onnx_model)
session = ort.InferenceSession(MODEL_PATH)

# Daftar kelas sesuai dengan model Anda
class_names = {0: 'Bukan Daun', 1: 'Healty', 2: 'Penyakit Cescospora', 3: 'Penyakit Kuning', 4: 'Penyakit Mozaik', 5: 'Penyakit Tungau'}

def preprocess_image(image_path):
    """
    Preproses gambar untuk dimasukkan ke model menggunakan OpenCV.
    """
    # Memuat gambar menggunakan OpenCV (BGR format)
    img = cv2.imread(image_path)
    
    # Mengubah ukuran gambar
    img = cv2.resize(img, (128, 128))  # Ubah ukuran gambar
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Konversi ke RGB
    
    # Normalisasi piksel
    img_array = img / 255.0
    
    # Tambahkan dimensi batch
    img_array = np.expand_dims(img_array, axis=0)  
    
    return img_array

def predict_image(image_path):
    """
    Fungsi untuk memprediksi kelas gambar.
    """
    # Preproses gambar
    img_array = preprocess_image(image_path)

    # Prediksi dengan model ONNX
    inputs = {session.get_inputs()[0].name: img_array.astype(np.float32)}
    predictions = session.run(None, inputs)
    predicted_class = np.argmax(predictions[0])

    # Dapatkan nama kelas
    predicted_class_name = class_names.get(predicted_class, 'Unknown')

    # Hasil prediksi
    return predicted_class_name, predictions[0].tolist()

# Streamlit UI
st.title("Klasifikasi Gambar Daun dengan Model ONNX")
st.write("Unggah gambar untuk diklasifikasikan.")

uploaded_file = st.file_uploader("Pilih file gambar", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Simpan file gambar sementara
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Tampilkan gambar yang diunggah
    st.image(file_path, caption="Gambar yang diunggah", use_column_width=True)

    # Prediksi gambar
    try:
        predicted_class_name, prediction_probabilities = predict_image(file_path)
        st.success(f"Kelas Prediksi: {predicted_class_name}")
        # st.write("Probabilitas Prediksi:")
        # for i, prob in enumerate(prediction_probabilities):
        #     st.write(f"{class_names.get(i, 'Unknown')}: {prob:.4f}")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

    # Hapus file setelah diproses
    os.remove(file_path)