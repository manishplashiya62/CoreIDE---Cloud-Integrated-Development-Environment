# Online Code Compiler (Web IDE)

## 🚀 Project Overview

The **Online Code Compiler (Web IDE)** is a web-based integrated development environment that enables users to write, edit, compile, execute, and manage source code directly from a web browser without installing any software. The platform provides a modern coding experience similar to VS Code while supporting multiple programming languages and secure code execution using isolated Docker containers.

This project is designed for students, developers, and coding enthusiasts who need a lightweight cloud-based coding environment for learning, practicing, and developing programs from any device.

---

# ✨ Features

## 👤 User Authentication

- User Registration
- Login & Logout
- Password Hashing
- Forgot Password
- User Profile
- Session Management

---

## 💻 Online Code Editor

- Monaco Editor (VS Code Editor)
- Syntax Highlighting
- Auto Completion
- Line Numbers
- Code Folding
- Multiple Tabs
- Auto Save
- Dark / Light Theme
- Font Size Adjustment

---

## 🌐 Multi-Language Support

- Python
- C
- C++
- Java
- JavaScript

Future Support

- Go
- Rust
- PHP
- Kotlin

---

## ▶️ Compiler & Execution

- Compile Code
- Run Code
- Stop Execution
- Standard Input Support
- Console Output
- Error Display
- Execution Time
- Memory Usage
- Clear Console

---

## 📁 Project Management

- Create Project
- Open Project
- Rename Project
- Delete Project
- Duplicate Project
- Download Project
- Upload Existing Project

---

## 📂 File Manager

- Create Files
- Create Folders
- Rename Files
- Delete Files
- Upload Files
- Download Files
- Tree View Navigation

---

## 📜 Execution History

- Previous Executions
- Output History
- Error Logs
- Execution Time
- Language Used
- Timestamp

---

## 🤖 AI Coding Assistant *(Optional)*

- Explain Code
- Debug Errors
- Generate Code
- Optimize Code
- Convert Programming Languages
- Code Documentation

---

## 📊 Dashboard

- Recent Projects
- Total Projects
- Total Executions
- Favorite Projects
- Storage Usage

---

## 🛠 Admin Panel

- User Management
- Project Monitoring
- System Logs
- Analytics Dashboard
- User Activity
- Delete Users

---

# 🏗 System Architecture

```
                User
                  │
                  ▼
           React / HTML UI
                  │
                  ▼
          Flask REST API
                  │
     ┌────────────┼────────────┐
     ▼            ▼            ▼
 Authentication  Compiler   Database
     │            │            │
     ▼            ▼            ▼
 Flask Login   Docker     SQLite/MySQL
                  │
                  ▼
          Code Execution Engine
```

---

# 🗂 Folder Structure

```
Online-Code-Compiler/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── database/
│   └── database.db
│
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── editor/
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── editor.html
│   ├── projects.html
│   ├── profile.html
│   └── admin.html
│
├── routes/
│   ├── auth.py
│   ├── compiler.py
│   ├── editor.py
│   ├── project.py
│   └── admin.py
│
├── models/
│   ├── user.py
│   ├── project.py
│   ├── file.py
│   └── history.py
│
├── compiler/
│   ├── python_runner.py
│   ├── c_runner.py
│   ├── cpp_runner.py
│   ├── java_runner.py
│   └── javascript_runner.py
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── uploads/
│
├── user_projects/
│
└── logs/
```

---

# 🗄 Database Design

## Users

| Field | Type |
|-------|------|
| id | Integer |
| username | Text |
| email | Text |
| password | Text |
| created_at | DateTime |

---

## Projects

| Field | Type |
|-------|------|
| id | Integer |
| user_id | Integer |
| project_name | Text |
| created_at | DateTime |
| updated_at | DateTime |

---

## Files

| Field | Type |
|-------|------|
| id | Integer |
| project_id | Integer |
| filename | Text |
| language | Text |
| content | LongText |

---

## Execution History

| Field | Type |
|-------|------|
| id | Integer |
| user_id | Integer |
| language | Text |
| source_code | LongText |
| output | LongText |
| execution_time | Float |
| memory_usage | Float |
| created_at | DateTime |

---

# 🔄 Project Workflow

```
User Login
      │
      ▼
Dashboard
      │
      ▼
Create/Open Project
      │
      ▼
Write Code
      │
      ▼
Choose Language
      │
      ▼
Compile
      │
      ▼
Run
      │
      ▼
Output Console
      │
      ▼
Save Project
      │
      ▼
Execution History
```

---

# 🛡 Security

- Password Hashing
- Secure Sessions
- CSRF Protection
- Input Validation
- SQL Injection Protection
- XSS Protection
- Docker Sandbox
- CPU & Memory Limits
- Execution Timeout
- Read-only Containers

---

# ⚙️ Technology Stack

## Frontend

- HTML5
- CSS3
- Bootstrap
- JavaScript
- React (Optional)
- Monaco Editor

## Backend

- Python
- Flask
- Flask Login
- Flask SQLAlchemy

## Database

- SQLite
- MySQL (Optional)

## Compiler

- Docker
- GCC
- G++
- Python
- OpenJDK
- Node.js

---

# 📈 Future Enhancements

- Real-time Collaboration
- Video Calling
- GitHub Integration
- Git Version Control
- Cloud Storage
- AI Pair Programmer
- Mobile Application
- Plugin Marketplace
- Code Sharing
- Online Competitive Programming Mode

---

# 🎯 Learning Outcomes

By completing this project, students will gain practical knowledge of:

- Full Stack Web Development
- REST API Development
- Authentication & Authorization
- Database Design
- Docker Containerization
- Secure Code Execution
- File Management
- Compiler Integration
- Software Architecture
- Cloud-Based IDE Development

---

# 📌 Conclusion

The **Online Code Compiler (Web IDE)** provides a complete browser-based programming environment with modern development tools, secure execution, project management, and multi-language support. It is an excellent final-year project because it combines frontend development, backend engineering, databases, DevOps, security, and scalable software architecture into a single real-world application.

---

## 👨‍💻 Developed Using

- Python
- Flask
- HTML5
- CSS3
- JavaScript
- React (Optional)
- SQLite / MySQL
- Docker
- Monaco Editor
- Bootstrap

---
