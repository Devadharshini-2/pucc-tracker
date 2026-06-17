# PUCC Tracker 🚗💨

A lightweight automation system for PUCC (Pollution Under Control Certificate) centers that automatically captures certificate data from the government portal and maintains digital records.

## Problem Statement

PUCC centers often maintain daily records manually, making it difficult to track certificates, calculate collections, and access historical data.

This project automates certificate tracking and reporting for a real-world PUCC center.

## Features

- Automatic certificate data capture
- Smart pricing engine
- Duplicate certificate prevention
- Historical date-wise reports
- Fuel sorting
- Time sorting
- Edit charge functionality
- Delete entry functionality
- Auto-refresh dashboard
- Lightweight SQLite database

## Tech Stack

- Python
- Flask
- SQLite
- JavaScript
- Chrome Extension (Manifest V3)
- HTML/CSS

## System Flow

PUCC Website → Chrome Extension → Flask API → SQLite Database → Report Dashboard

## Smart Pricing Logic

| Certificate Fee | Actual Charge |
|----------------|--------------|
| ₹60 | ₹100 |
| ₹100 | ₹200 |
| ₹110 | ₹200 |
| ₹150 (6 months) | ₹200 |
| ₹150 (1 year) | ₹250 |

## Dashboard

_Add screenshots here later._

## Future Improvements

- Monthly analytics
- Vehicle search
- Certificate preview
- Database backup

## Real World Impact

Developed for an actual PUCC center to digitize certificate management and reduce manual work.

---

**Developer:** Devadharshini S
