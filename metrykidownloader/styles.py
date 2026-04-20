from __future__ import annotations


def light_stylesheet() -> str:
    return """
    QMainWindow, QWidget {
        background: #f5f7fb;
        color: #1f2937;
    }
    QGroupBox {
        background: #ffffff;
        border: 1px solid #dbe2ea;
        border-radius: 14px;
        margin-top: 8px;
        font-weight: 600;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
    }
    QLabel {
        color: #334155;
        background: transparent;
    }
    QLabel#hintLabel {
        color: #64748b;
        font-style: italic;
    }
    QLineEdit, QTextEdit, QTableWidget {
        background: #ffffff;
        color: #1f2937;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 8px;
    }
    QTableWidget {
        gridline-color: #e2e8f0;
        alternate-background-color: #f8fafc;
    }
    QHeaderView::section {
        background: #eef2f7;
        color: #334155;
        border: none;
        border-bottom: 1px solid #dbe2ea;
        padding: 10px;
        font-weight: 600;
    }
    QPushButton {
        background: #e9eef6;
        color: #1f2937;
        border: 1px solid #d4dce7;
        border-radius: 12px;
        padding: 10px 14px;
        font-weight: 600;
        text-align: center;
    }
    QPushButton:hover {
        background: #dde6f3;
    }
    QPushButton:pressed {
        background: #d5dfef;
    }
    QPushButton:disabled {
        color: #94a3b8;
        background: #eef2f7;
    }
    QPushButton#addBookButton {
        background: #facc15;
        color: #1f2937;
        border: 1px solid #eab308;
    }
    QPushButton#addBookButton:hover {
        background: #eab308;
    }
    QPushButton#deleteBookButton {
        background: #f97316;
        color: white;
        border: 1px solid #ea580c;
    }
    QPushButton#changePagesButton {
        background: #a855f7;
        color: white;
        border: 1px solid #9333ea;
    }
    QPushButton#downloadButton {
        background: #22c55e;
        color: white;
        border: 1px solid #16a34a;
    }
    QPushButton#stopButton {
        background: #ef4444;
        color: white;
        border: 1px solid #dc2626;
    }
    QPushButton#resetButton {
        background: #3b82f6;
        color: white;
        border: 1px solid #2563eb;
    }
    QProgressBar {
        border: 1px solid #d4dce7;
        border-radius: 10px;
        background: #ffffff;
        text-align: center;
        min-height: 24px;
    }
    QProgressBar::chunk {
        background: #3b82f6;
        border-radius: 9px;
    }
    QStatusBar {
        background: #ffffff;
        color: #475569;
        border-top: 1px solid #dbe2ea;
    }
    """


def dark_stylesheet() -> str:
    return """
    QMainWindow, QWidget {
        background: #111827;
        color: #e5e7eb;
    }
    QGroupBox {
        background: #1f2937;
        border: 1px solid #374151;
        border-radius: 14px;
        margin-top: 8px;
        font-weight: 600;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
    }
    QLabel {
        color: #d1d5db;
        background: transparent;
    }
    QLabel#hintLabel {
        color: #9ca3af;
        font-style: italic;
    }
    QLineEdit, QTextEdit, QTableWidget {
        background: #0f172a;
        color: #e5e7eb;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 8px;
    }
    QTableWidget {
        gridline-color: #253041;
        alternate-background-color: #111827;
    }
    QHeaderView::section {
        background: #243041;
        color: #e5e7eb;
        border: none;
        border-bottom: 1px solid #374151;
        padding: 10px;
        font-weight: 600;
    }
    QPushButton {
        background: #273549;
        color: #f8fafc;
        border: 1px solid #3c4b60;
        border-radius: 12px;
        padding: 10px 14px;
        font-weight: 600;
        text-align: center;
    }
    QPushButton:hover {
        background: #32445d;
    }
    QPushButton:pressed {
        background: #40526b;
    }
    QPushButton:disabled {
        color: #94a3b8;
        background: #1f2937;
    }
    QPushButton#addBookButton {
        background: #eab308;
        color: #111827;
        border: 1px solid #ca8a04;
    }
    QPushButton#deleteBookButton {
        background: #f97316;
        color: white;
        border: 1px solid #ea580c;
    }
    QPushButton#changePagesButton {
        background: #a855f7;
        color: white;
        border: 1px solid #9333ea;
    }
    QPushButton#downloadButton {
        background: #22c55e;
        color: white;
        border: 1px solid #16a34a;
    }
    QPushButton#stopButton {
        background: #ef4444;
        color: white;
        border: 1px solid #dc2626;
    }
    QPushButton#resetButton {
        background: #3b82f6;
        color: white;
        border: 1px solid #2563eb;
    }
    QProgressBar {
        border: 1px solid #374151;
        border-radius: 10px;
        background: #0f172a;
        text-align: center;
        min-height: 24px;
    }
    QProgressBar::chunk {
        background: #60a5fa;
        border-radius: 9px;
    }
    QStatusBar {
        background: #0f172a;
        color: #cbd5e1;
        border-top: 1px solid #374151;
    }
    """
