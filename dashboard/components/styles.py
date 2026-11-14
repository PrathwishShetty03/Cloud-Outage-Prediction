import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* Base Reset & Palette */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: #0B1220 !important;
            color: #F1F5F9 !important;
        }

        .stApp {
            background-color: #0B1220 !important;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #111A2B !important;
            border-right: 1px solid #29364A !important;
            width: 260px !important;
        }

        section[data-testid="stSidebar"] .stMarkdown {
            color: #94A3B8 !important;
        }

        /* Active Navigation Item Styling */
        div[data-testid="stSidebarNav"] li a[aria-current="page"] {
            background-color: rgba(79, 124, 255, 0.12) !important;
            color: #F1F5F9 !important;
            border-left: 3px solid #4F7CFF !important;
            border-radius: 0 4px 4px 0 !important;
            font-weight: 600 !important;
        }

        /* Section Anchors & Headers */
        h1 {
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            color: #F1F5F9 !important;
            margin-bottom: 4px !important;
            padding-top: 0 !important;
            letter-spacing: -0.02em !important;
        }
        h2 {
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            color: #F1F5F9 !important;
            margin-top: 16px !important;
            margin-bottom: 8px !important;
            letter-spacing: -0.01em !important;
        }
        h3 {
            font-size: 1.0rem !important;
            font-weight: 600 !important;
            color: #CBD5E1 !important;
            margin-top: 12px !important;
            margin-bottom: 6px !important;
        }

        /* SRE Card Containers */
        .sre-card {
            background: #151F32;
            border: 1px solid #29364A;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }

        .sre-card-elevated {
            background: #1B263A;
            border: 1px solid #29364A;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }

        /* Metric Typography */
        div[data-testid="stMetricValue"] {
            font-family: 'Inter', sans-serif !important;
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            color: #F1F5F9 !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            color: #94A3B8 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }

        /* Status Dot Badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .badge-healthy {
            background: rgba(34, 197, 94, 0.12);
            color: #22C55E;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        .badge-warning {
            background: rgba(245, 158, 11, 0.12);
            color: #F59E0B;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .badge-critical {
            background: rgba(239, 68, 68, 0.12);
            color: #EF4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        .badge-active {
            background: rgba(79, 124, 255, 0.12);
            color: #4F7CFF;
            border: 1px solid rgba(79, 124, 255, 0.3);
        }
        .badge-standby {
            background: rgba(100, 116, 139, 0.12);
            color: #94A3B8;
            border: 1px solid rgba(100, 116, 139, 0.3);
        }

        /* Table Styling */
        div[data-testid="stTable"], table {
            width: 100% !important;
            background-color: #151F32 !important;
            border-collapse: collapse !important;
            border: 1px solid #29364A !important;
            border-radius: 6px !important;
            font-size: 0.85rem !important;
        }
        th {
            background-color: #111A2B !important;
            color: #94A3B8 !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            font-size: 0.75rem !important;
            letter-spacing: 0.05em !important;
            padding: 10px 12px !important;
            border-bottom: 1px solid #29364A !important;
        }
        td {
            padding: 10px 12px !important;
            border-bottom: 1px solid #29364A !important;
            color: #F1F5F9 !important;
        }
        tr:hover td {
            background-color: #1B263A !important;
        }

        /* Buttons Reset */
        .stButton>button {
            background: #4F7CFF !important;
            color: #FFFFFF !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            border-radius: 6px !important;
            border: 1px solid #4F7CFF !important;
            padding: 6px 14px !important;
            transition: background 0.15s ease-in-out !important;
        }
        .stButton>button:hover {
            background: #668EFF !important;
            border-color: #668EFF !important;
        }

        /* Custom Monospace Utility */
        .tech-id {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.82rem !important;
        }

        /* Custom Scrollbars */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #0B1220;
        }
        ::-webkit-scrollbar-thumb {
            background: #29364A;
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #3B4D68;
        }
    </style>
    """, unsafe_allow_html=True)
