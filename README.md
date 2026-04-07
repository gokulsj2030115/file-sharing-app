# 🌌 S3 Storage Hub

<div align="center">
  <img src="https://img.icons8.com/clouds/200/cloud-lighting.png" alt="S3 Storage Hub Logo" width="120" height="120" />
  <h3>Production-Style S3 File Manager Dashboard</h3>
  <p>A high-performance, prefix-based S3 explorer built with Flask, Boto3, and Vanilla SaaS-UI.</p>

  [![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
  [![AWS S3](https://img.shields.io/badge/AWS_S3-Storage-FF9900?style=for-the-badge&logo=amazons3&logoColor=white)](https://aws.amazon.com/s3/)
  [![Tailwind-Inspired](https://img.shields.io/badge/UI-Modern_SaaS-6366f1?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://github.com/gokulsj2030115/s3-storage-hub)
</div>

---

## 📖 Table of Contents
- [✨ Core Features](#-core-features)
- [🏗️ Technical Specs](#️-technical-specs)
- [🎨 Design System](#-design-system)
- [🚀 Rapid Deployment](#-rapid-deployment)
- [📂 Project Topology](#-project-topology)
- [🛡️ Security Architecture](#️-security-architecture)

---

## ✨ Core Features

| Feature | Detailed Specification |
| :--- | :--- |
| **📁 Prefix-Based Folders** | Virtual directory simulation using S3 object keys and delimiter logic. Full breadcrumb navigation support. |
| **🗑️ Trash Lifecycle** | "Soft Delete" mechanism moving items to `trash/` prefix. Enables restoration or permanent purging. |
| **🕒 Recent Activity** | Global view of the 7 most recently modified files across the entire bucket, regardless of depth. |
| **📊 Real-time Metrics** | Live calculation of bucket size, object count, and used percentage (relative to configurable 5GB limit). |
| **🔗 Presigned Sharing** | One-click 3600s access links with `inline` disposition for viewing PDFs/Images in browser. |
| **🔍 Search Index** | Client-side real-time filtering with `onkeyup` instant updates to the explorer view. |

---

## 🏗️ Technical Specs

### 🧠 Backend (Logic Layer)
- **S3Service Class**: Encapsulated Boto3 operations for `move`, `copy`, `list`, and `stats`.
- **Dynamic Routing**: Flask routes optimized for query parameters (`?prefix=`, `?view=`).
- **Error Handling**: Graceful `ClientError` catching with Flash messaging for user feedback.

### 🎨 Frontend (Presentation Layer)
- **CSS3 Variables**: Managed color palette (Indigo, Slate) for a premium dark/light mode feel.
- **Glassmorphism**: Subtle backdrops and micro-animations for a high-end SaaS experience.
- **Iconography**: Integrated FontAwesome 6 for visual file-type distinction (Folders vs Files).

---

## 🚀 Rapid Deployment

### Local Development
```bash
# Clone & Navigate
git clone https://github.com/gokulsj2030115/s3-storage-hub
cd s3-storage-hub

# Virtual Env
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate

# Install & Run
pip install -r requirements.txt
python app.py
```

### AWS EC2 Production
1. **IAM Role**: Attach a role with `AmazonS3FullAccess` to your EC2.
2. **Environment**: Set `S3_BUCKET` in your `.env`.
3. **Gunicorn**:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

---

## 🛡️ Security Architecture

> [!CAUTION]
> **Credential Safety**: This project is designed to run via **IAM Roles** in production. Never commit `.env` files with secret keys to version control.

- **Principle of Least Privilege**: Bucket access is scoped via instance profiles.
- **Public Access Block**: S3 bucket remains private; only the backend interacts with objects.
- **Time-Bound Access**: Temporary URLs ensure that shared links expire automatically.

---

## 📂 Project Topology

```text
s3-storage-hub/
├── app.py              # Main Flask Controller
├── s3_service.py       # S3 Interaction Engine
├── config.py           # Environment Variables
├── SETUP.md            # Detailed Infrastructure Guide
├── static/             # Assets (SaaS-UI & JS)
│   ├── css/style.css   # Custom CSS3 Design System
│   └── js/script.js    # Client Logic & Modals
└── templates/          # Jinja2 Layouts
    └── index.html      # Main Storage Dashboard
```

---

<div align="center">
  <p>Built for cloud-native storage management</p>
  <b>S3 Storage Hub &copy; 2026</b>
</div>