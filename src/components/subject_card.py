
import streamlit as st


def subject_card(name, code, section, stats=None, footer_callback=None):

    if stats is None:
        stats = []

    # =========================================================
    # STATS HTML
    # =========================================================

    stats_html = ""

    for icon, label, value in stats:
        stats_html += f"""
        <div class="stat-box">
            <span class="stat-icon">{icon}</span>
            <span class="stat-value">{value}</span>
            <span class="stat-label">{label}</span>
        </div>
        """

    # =========================================================
    # SUBJECT CARD HTML
    # =========================================================

    html = f"""
    <div class="subject-card">

        <h3 class="subject-title">
            {name}
        </h3>

        <p class="subject-info">
            Code:
            <span class="subject-code">
                {code}
            </span>

            <span class="separator">|</span>

            Section:
            <b>{section}</b>
        </p>

        <div class="stats-container">
            {stats_html}
        </div>

        <div class="share-section">

            <div class="share-content">

                <div class="share-icon">
                    🔗
                </div>

                <div>
                    <div class="share-title">
                        Share to Join
                    </div>

                    <div class="share-description">
                        Share this subject with students
                    </div>
                </div>

            </div>

        </div>

    </div>

    <style>

        /* ==============================================
           SUBJECT CARD
        ============================================== */

        .subject-card {{
            background-color: white;
            border: 1px solid #dddddd;
            border-left: 8px solid #EB459E;
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }}


        /* ==============================================
           SUBJECT TITLE
        ============================================== */

        .subject-title {{
            margin: 0;
            padding: 0;
            color: #1e293b;
            font-size: 24px;
            font-weight: 600;
        }}


        /* ==============================================
           SUBJECT INFORMATION
        ============================================== */

        .subject-info {{
            color: #64748b;
            margin-top: 10px;
            margin-bottom: 15px;
            font-size: 15px;
        }}


        .subject-code {{
            background-color: #E0E3FF;
            color: #5865F2;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 600;
            margin-left: 5px;
        }}


        .separator {{
            margin-left: 10px;
            margin-right: 10px;
        }}


        /* ==============================================
           STATS
        ============================================== */

        .stats-container {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 15px;
        }}


        .stat-box {{
            background-color: #fce7f3;
            padding: 8px 14px;
            border-radius: 12px;
            font-size: 14px;
            color: #1e293b;
        }}


        .stat-icon {{
            margin-right: 5px;
        }}


        .stat-value {{
            font-weight: bold;
            margin-right: 4px;
        }}


        .stat-label {{
            margin-right: 3px;
        }}


        /* ==============================================
           SHARE TO JOIN SECTION
        ============================================== */

        .share-section {{
            margin-top: 20px;
            padding-top: 18px;
            border-top: 1px solid #e5e7eb;
        }}


        .share-content {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}


        .share-icon {{
            width: 42px;
            height: 42px;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #fce7f3;
            border-radius: 12px;
            font-size: 20px;
        }}


        .share-title {{
            color: #1e293b;
            font-size: 16px;
            font-weight: 600;
        }}


        .share-description {{
            color: #64748b;
            font-size: 13px;
            margin-top: 2px;
        }}

    </style>
    """

    # =========================================================
    # RENDER SUBJECT CARD
    # =========================================================

    st.html(html)

    # =========================================================
    # SHARE BUTTON
    # =========================================================

    if footer_callback:

        share_col1, share_col2 = st.columns(
            [3, 1],
            vertical_alignment="center"
        )

        with share_col1:
            st.empty()

        with share_col2:

            footer_callback()

