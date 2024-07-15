# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth, messages
from .code.code import RandomFourierFeatures
from django.http import JsonResponse, HttpResponseNotAllowed
from django.http import JsonResponse

# Third-party imports
import os
import numpy as np
from joblib import load
import librosa
import matplotlib.pyplot as plt
import base64
import pickle

# Django imports (continued)
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import tensorflow as tf

print(tf.__version__)


from tensorflow.python.keras.models import load_model
from tensorflow.python.keras.utils.generic_utils import register_keras_serializable

model = tf.keras.models.load_model(
    "emosense/code/emocode.keras",
    custom_objects={"RandomFourierFeatures": RandomFourierFeatures},
)

try:
    model = tf.keras.models.load_model(
        "emosense/code/emocode.keras",
        custom_objects={"RandomFourierFeatures": RandomFourierFeatures},
    )
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")


# Function to create spectrogram from audio file
def create_spectrogram(audio_file):
    y, sr = librosa.load(audio_file, sr=None)
    ms = librosa.feature.melspectrogram(y=y, sr=sr)
    log_ms = librosa.power_to_db(ms, ref=np.max)
    return log_ms


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username and password:  
            user = auth.authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect("home")  
            else:
                messages.error(request, "Invalid username or password")
                return redirect(
                    "login"
                )  
        else:
            messages.error(request, "Please provide both username and password")
            return redirect(
                "login"
            )  
    else:
        return render(request, "login.html")


def signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if not username:
            messages.error(request, "Please provide a username")
            return redirect("signup")

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email Taken")
                return redirect("signup")
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username Taken")
                return redirect("signup")
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password
                )
                user.save()

                # log user in
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                return redirect("home")
        else:
            messages.info(request, "Password Not Matching")
            return redirect("signup")
    else:
        return render(request, "signup.html")


def home(request):
    return render(request, "home.html")


def forgot(request):
    return render(request, "forgot.html")


def result(request):
    print(request)
    print(request.method)
    print(request.FILES)
    if request.method == "POST" and "audio" in request.FILES:
        audio_file = request.FILES["audio"]
        audio_path = default_storage.save(
            "temp_audio.wav", ContentFile(audio_file.read())
        )

        print("audio saved")

        try:
            # Process the audio file
            spectrogram = create_spectrogram(audio_path)

            # Convert spectrogram to image-like array for prediction
            spectrogram_image = np.expand_dims(spectrogram, axis=-1)
            spectrogram_image = np.expand_dims(spectrogram_image, axis=0)

            prediction = model.predict(spectrogram_image)
            class_labels = ["belly pain", "burping", "discomfort", "hungry", "tired"]
            predicted_label = class_labels[np.argmax(prediction)]
            print(predicted_label)

        finally:
            # Clean up the saved audio file
            os.remove(audio_path)

        print("Prediction result:", prediction)


        return JsonResponse({"predicted_label": predicted_label})
    else:
        return render(request, "home.html")


def upload_audio(request):
    print(request)
    print(request.method)
    print(request.FILES)
    if request.method == "POST":
        audio_file = request.FILES["audio"]
        audio_path = default_storage.save(
            "recorded_audio.wav", ContentFile(audio_file.read(), "recorded_audio.wav")
        )

        print("audio saved", audio_path)
        print(audio_file, type(audio_file))

        try:
            # Process the audio file
            spectrogram = create_spectrogram(audio_path)

            # Convert spectrogram to image-like array for prediction
            spectrogram_image = np.expand_dims(spectrogram, axis=-1)
            spectrogram_image = np.expand_dims(spectrogram_image, axis=0)

            prediction = model.predict(spectrogram_image)
            class_labels = ["belly pain", "burping", "discomfort", "hungry", "tired"]
            predicted_label = class_labels[np.argmax(prediction)]
            print(predicted_label)

        finally:
            # Clean up the saved audio file
            os.remove(audio_path)

        print("Prediction result:", prediction)

        # # Render the result template with prediction
        # return render(request, 'result.html', {'prediction': predicted_label})
        # Render the result template with prediction
        print("result.html")
        return JsonResponse({"predicted_label": predicted_label})
    else:
        print("home.html")
        return render(request, "home.html")