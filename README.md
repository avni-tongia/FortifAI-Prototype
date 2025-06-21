
# 🛡️ Self-Learning Multimodal Fraud Detection System (Text + Image)

---

## ✅ What's Included

- `app.py` → Fully self-learning Streamlit app (Text + Image fraud detection)
- `generate_full_combined_initializer.py` → Full automatic pool generator (text & image)
- `Dockerfile` → Full Docker deployment file
- `requirements.txt` → Clean dependency list for pip installation
- `.gitignore` → To avoid tracking unnecessary files in Git

---

## 🔧 Correct GitHub Structure

When pushing this repo to GitHub, ensure:

- DO NOT commit your `venv/` folder.
- DO NOT commit `.pkl` generated pool files.
- DO NOT commit generated image augmentation folders.

Your `.gitignore` file should contain:

```
venv/
__pycache__/
*.pkl
generated_legit_images/
generated_fraud_images/
```

---

# 🚀 Full Local Development Setup

## 1️⃣ Clone your repo (or pull latest version)

```bash
git clone <your-repo-url>
cd <repo-folder>
```

## 2️⃣ Create a new virtual environment (venv)

```bash
python -m venv venv
```

### Activate virtual environment:

- **On Windows**:

```bash
venv\Scripts\activate
```

- **On Mac/Linux**:

```bash
source venv/bin/activate
```

✅ You’ll see `(venv)` appear in your terminal.

---

## 3️⃣ Install all dependencies:

Using `requirements.txt`:

```bash
pip install -r requirements.txt
```

✅ This installs:

- streamlit
- torch
- torchvision
- sentence-transformers
- scikit-learn
- pillow
- numpy

You only need to install ONCE per virtual environment.

---

## 4️⃣ Prepare initial images

In your project folder, place:

- `legit_sample1.jpg`
- `legit_sample2.jpg`
- `fraud_sample1.jpg`
- `fraud_sample2.jpg`

These seed images are used by the initializer to create starting embedding pools.

---

## 5️⃣ Generate your initial embedding pools:

Run the combined initializer:

```bash
python generate_full_combined_initializer.py
```

✅ This creates:

- `legit_text_pool.pkl`
- `fraud_text_pool.pkl`
- `legit_image_pool.pkl`
- `fraud_image_pool.pkl`

These will be used by your Streamlit app for inference.

---

## 6️⃣ Launch the Streamlit App:

```bash
streamlit run app.py
```

Go to your browser → `http://localhost:8501` → App will open fully.

✅ The app is now fully functional and self-learning.

---

# 🔁 Daily Workflow Summary

| Action | Required? |
|--------|-----------|
| Reinstall dependencies? | ❌ No (only once per venv) |
| Re-initialize pools? | ❌ No (unless you want fresh pools) |
| Activate venv? | ✅ Yes |
| Run Streamlit? | ✅ Yes |

---

# 🔨 Optional Docker Deployment

## Build Docker Image:

```bash
docker build -t multimodal-fraud-detector .
```

## Run Docker Container:

```bash
docker run -p 8501:8501 multimodal-fraud-detector
```

## Open browser:

```
http://localhost:8501
```

✅ With Docker, you don’t need to manage virtual environments anymore.

---

# ✅ After this setup:
- Your repo remains clean.
- Your virtual environment stays isolated (ignored by git).
- Anyone can reproduce your full environment easily using `requirements.txt`.

---
