# 📔 Smart Diary & Reminder Telegram Bot

## 📌 About the Project

Smart Diary & Reminder Bot is a Telegram bot written in Python that helps users organize their daily life.
The bot works as a **personal diary**, **reminder assistant**, and **weekly planner**.

Users can save thoughts, tasks, and plans in natural language without complicated commands.

---

## 🚀 Features

### 📝 Smart Diary

* Save any text message as a diary entry
* Automatic category detection:

  * Study 📚
  * Health 🏥
  * Work 💼
  * Tasks 📌
  * Personal 💬
  * Thoughts 💭

---

### ⏰ Smart Reminders

* Create reminders **with or without commands**
* Supported formats:

  ```
  20:30
  Do homework
  ```

  or

  ```
  /remind 2026-01-02 20:30 Doctor appointment
  ```
* Automatic reminder notifications
* View all reminders using `/reminder`

---

### 📅 Weekly Planner

* Add plans manually:

  ```
  /weekadd Monday workout
  ```
* Add plans using natural language:

  ```
  Do physics homework until Friday
  ```
* Duplicate tasks are automatically filtered
* View weekly plan with `/week`
* Clear weekly plan with `/weekclear`

---

## 🛠 Technologies Used

* Python 3.11
* aiogram (Telegram Bot API)
* SQLite (local database)
* asyncio
* FSM (Finite State Machine) for smart input handling

---

## 💡 Why This Project?

This project demonstrates:

* Working with Telegram bots
* Asynchronous programming
* Databases (SQLite)
* Natural language parsing
* Clean project structure

It is suitable as a **final school project** or a **beginner-to-intermediate Python project**.

---

## 📈 Future Improvements

* Advanced natural language date parsing
* Notifications statistics
* Cloud database support
* Multi-language support

---

## 👤 Author

Project created by Dior Achilov

---
