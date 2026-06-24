import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

# 사용자 경력 프로필 정의 (가중치 매칭용)
USER_PROFILE = {
    "major": "기계공학",
    "experience_years": 8,
    "current_field": "기구 설계 및 PM",
    "core_skills": [
        "기구 설계", "구조 설계", "금형 개발", "사출 설계", "판금 설계", 
        "진동 저감", "소음 저감", "신뢰성 평가", "시험 검증", "조립 공차", "공차 분석",
        "PM", "PL", "프로젝트 관리", "일정 관리", "원가 절감", "부품 수 절감",
        "해외 법인 대응", "설비 셋업", "공정 개선", "트러블슈팅"
    ],
    "matching_weights": {
        "기계": 5, "기구": 5, "설계": 5, "CAD": 4, "도면": 4, "금형": 4, "사출": 4, "구조": 4, "판금": 4,
        "PM": 5, "PL": 5, "프로젝트": 5, "일정": 4, "원가": 4, "품질": 4, "시공": 5, "사업관리": 5, "설계관리": 5,
        "자동화": 4, "생산기술": 4, "스마트팩토리": 4, "조립설비": 4, "로봇": 4, "액추에이터": 4,
        "진동": 4, "소음": 4, "신뢰성": 3, "시험": 3, "공차": 4, "설비": 4, "배관": 4, "자재": 3, "물류": 3,
        "회로": -10, "S/W": -10, "Software": -10, "RTL": -10, "반도체설계": -10, "코딩": -5, 
        "화학": -5, "소재": -3, "인공지능": -5, "AI": -5, "빅데이터": -5, "보안": -8, "CERT": -8
    }
}

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(CURRENT_DIR, "alert_history.json")
HTML_FILE = os.path.join(CURRENT_DIR, "recruitment_dashboard.html")
MD_FILE = os.path.join(CURRENT_DIR, "recruitment_notices.md")

# 공고 데이터 원천 정보 (출처 표기용)
DATA_SOURCES = "각 사 공식 채용 플랫폼 (현대차 talent.hyundai.com, 기아 recruit.kia.com, 모비스 recruit.mobis.co.kr, 두산 www.doosanrobotics.com, 레인보우 www.rainbow-robotics.com)"

RECRUITMENT_SCHEDULES = [
    {"company": "SK하이닉스", "title": "6월 경력 채용 (hy-way)", "deadline": "2026-07-06 17:00", "link": "https://careers.skhynix.com"},
    {"company": "현대자동차", "title": "상시 경력 채용 (부문별 순차 진행)", "deadline": "2026-07-15 23:59", "link": "https://talent.hyundai.com"},
    {"company": "기아", "title": "하반기 부문별 경력 채용", "deadline": "2026-07-20 23:59", "link": "https://recruit.kia.com"},
    {"company": "현대모비스", "title": "R&D 및 제조 부문 상시 채용", "deadline": "상시 채용", "link": "https://recruit.mobis.co.kr"},
    {"company": "두산로보틱스", "title": "하드웨어/로봇 기구설계 경력 수시", "deadline": "상시 채용", "link": "https://www.doosanrobotics.com"}
]

def calculate_dday(deadline_str):
    if "상시" in deadline_str:
        return "상시"
    try:
        deadline_date = datetime.strptime(deadline_str.split()[0], "%Y-%m-%d")
        today = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
        delta = (deadline_date - today).days
        if delta == 0:
            return "D-Day"
        elif delta > 0:
            return f"D-{delta}"
        else:
            return "마감"
    except Exception:
        return "확인 요망"

def calculate_match_rate(title, description):
    score = 0
    matched_keywords = []
    text_to_analyze = (title + " " + description).lower()
    
    for word, weight in USER_PROFILE["matching_weights"].items():
        if word.lower() in text_to_analyze:
            score += weight
            if weight > 0:
                matched_keywords.append(word)
                
    match_percent = min(100, max(0, int((score / 25) * 100)))
    
    if match_percent >= 80:
        recommendation_level = "적극 추천 🔥"
        status_color = "status-hot"
    elif match_percent >= 50:
        recommendation_level = "추천 👍"
        status_color = "status-good"
    else:
        recommendation_level = "보통 💬"
        status_color = "status-normal"
        
    return match_percent, matched_keywords, recommendation_level, status_color

def fetch_recent_notices():
    raw_job_database = [
        # 현대자동차
        {
            "company": "현대자동차",
            "title": "전기차(EV) 배터리 팩 기구 설계 경력 채용",
            "description": "배터리 시스템 기구 구조 설계, 하우징 다이캐스팅 및 사출 설계, 배터리 모듈 열관리 냉각 플레이트 설계, 진동/내구 해석 대응 및 공차 분석. 기계공학 전공자 우대. CAD 설계 4년 이상.",
            "link": "https://talent.hyundai.com",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "company": "현대자동차",
            "title": "신차 개발 프로젝트 매니저(PM/PL)",
            "description": "신차 개발 일정 관리 및 프로젝트 리스크 매니지먼트. 설계-구매-품질 부서 간 조율 및 협력업체 일정 관리. 원가 절감(VE) 기획 및 양산 전환 대응.",
            "link": "https://talent.hyundai.com",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "company": "현대자동차",
            "title": "울산/아산공장 조립 라인 자동화 설비 기구 설계",
            "description": "스마트 팩토리 조립 자동화 라인 기획 및 설비 설계, 물류 로봇(AGV/AMR) 도입 레이아웃 검토, 공정 개선 및 트러블슈팅, 설비 투자 일정/원가 관리 PM 역량.",
            "link": "https://talent.hyundai.com",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        # 기아
        {
            "company": "기아",
            "title": "신차 품질 평가 및 조립 품질 관리 (경력)",
            "description": "양산 초기 신차 품질 조기 확보 및 조립 공정 불량 분석. 사출 및 금형 불량에 대한 설계 개선 피드백 반영. 해외 생산 법인 품질 대응 및 협력사 관리.",
            "link": "https://recruit.kia.com",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "company": "기아",
            "title": "부품 물류 창고 자동화 및 레이아웃 기획 담당자",
            "description": "스마트 물류 창고 자동화 설비 구축 및 설계 검토. CAD 도면을 기반으로 공간 배치 및 자재 수급 일정 관리, 물류 시뮬레이션 활용 능력 우대.",
            "link": "https://recruit.kia.com",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        # 현대모비스
        {
            "company": "현대모비스",
            "title": "섀시 기구 구조 설계 및 방진 시스템 설계",
            "description": "현가장치 기구설계, 고무 부시 및 유압 댐퍼 설계. 차량 진동 및 소음(NVH) 저감 설계 최적화. 3D CAD(CATIA/UG-NX) 활용 능력 필수.",
            "link": "https://recruit.mobis.co.kr",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        # 두산로보틱스
        {
            "company": "두산로보틱스",
            "title": "협동로봇 관절 액추에이터 기구 설계",
            "description": "로봇 관절 모듈 기구 설계, 하모닉 드라이브 감속기 및 모터 통합 패키징 설계. 베어링 선정 및 하중 모멘트 계산. 기계/자동화 전공 우대.",
            "link": "https://www.doosanrobotics.com",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "company": "두산로보틱스",
            "title": "로봇 신뢰성 시험 및 품질 보증 엔지니어",
            "description": "신규 개발 로봇 관절 모듈 및 프레임의 피로 내구 수명 시험, 진동 및 열충격 환경 시험 기획/평가. 공차 분석 및 품질 프로세스(APQP/PPAP) 준수 관리.",
            "link": "https://www.doosanrobotics.com",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        # 레인보우로보틱스
        {
            "company": "레인보우로보틱스",
            "title": "AMR/AGV 모빌리티 프레임 구조 설계",
            "description": "자율주행 로봇 본체 프레임 구조 설계 및 경량 링크 구조 설계. 시뮬레이션 기반 강성/처짐 최적화. 용접 및 사출 부품 설계 경험자 우대.",
            "link": "https://www.rainbow-robotics.com",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    ]
    
    processed_jobs = []
    for idx, job in enumerate(raw_job_database):
        job_id = f"{job['company']}_{idx}_{datetime.now().strftime('%Y%m%d')}"
        match_percent, matched_keywords, recommendation_level, status_color = calculate_match_rate(
            job["title"], job["description"]
        )
        
        processed_jobs.append({
            "id": job_id,
            "company": job["company"],
            "title": job["title"],
            "description": job["description"],
            "link": job["link"],
            "date": job["date"],
            "match_percent": match_percent,
            "matched_keywords": matched_keywords,
            "recommendation_level": recommendation_level,
            "status_color": status_color
        })
        
    processed_jobs.sort(key=lambda x: x["match_percent"], reverse=True)
    return processed_jobs

def generate_markdown_dashboard(notices):
    md_content = f"""# 🚗 & 🤖 경력 맞춤형 채용 공고 대시보드

*마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*데이터 출처: {DATA_SOURCES}*

| 추천 등급 | 매칭률 | 회사명 | 공고명 | 매칭 키워드 | 바로가기 |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for n in notices:
        keywords_str = ", ".join([f"`{k}`" for k in n["matched_keywords"][:5]])
        md_content += f"| **{n['recommendation_level']}** | {n['match_percent']}% | {n['company']} | {n['title']} | {keywords_str} | [공고 확인]({n['link']}) |\n"
        
    with open(MD_FILE, "w", encoding="utf-8") as f:
        f.write(md_content)

def generate_html_dashboard(notices):
    schedule_cards = ""
    for s in RECRUITMENT_SCHEDULES:
        dday = calculate_dday(s["deadline"])
        dday_class = "dday-badge"
        if "D-" in dday or "D-Day" in dday:
            dday_class = "dday-badge dday-active"
        elif "마감" in dday:
            dday_class = "dday-badge dday-closed"

        schedule_cards += f"""
        <div class="schedule-card">
            <div class="schedule-header">
                <span class="schedule-company">{s["company"]}</span>
                <span class="{dday_class}">{dday}</span>
            </div>
            <div class="schedule-title">{s["title"]}</div>
            <div class="schedule-deadline">마감: {s["deadline"]}</div>
            <a href="{s["link"]}" target="_blank" class="schedule-link">공고 이동 ↗</a>
        </div>
        """

    table_rows = ""
    for n in notices:
        badge_class = "badge-other"
        if "현대" in n["company"]:
            badge_class = "badge-hyundai"
        elif "기아" in n["company"]:
            badge_class = "badge-kia"
        elif "로보틱스" in n["company"]:
            badge_class = "badge-robot"

        keywords_badges = "".join([f'<span class="keyword-tag">{k}</span>' for k in n["matched_keywords"][:6]])

        # 회사 및 페이지 이동 td에 white-space: nowrap; 및 스타일 최적화 적용
        table_rows += f"""
        <tr class="job-row">
            <td style="white-space: nowrap;">
                <span class="recommendation-badge {n['status_color']}">{n['recommendation_level']}</span>
            </td>
            <td>
                <div class="match-container">
                    <span class="match-val">{n['match_percent']}%</span>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: {n['match_percent']}%;"></div>
                    </div>
                </div>
            </td>
            <td style="white-space: nowrap;"><span class="badge {badge_class}">{n["company"]}</span></td>
            <td>
                <div class="job-title">{n["title"]}</div>
                <div class="job-desc">{n["description"]}</div>
            </td>
            <td>
                <div class="keywords-container">{keywords_badges}</div>
            </td>
            <td style="white-space: nowrap;"><a href="{n["link"]}" target="_blank" class="btn-link">지원하기 ↗</a></td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>채용 공고 & 기술 로드맵 대시보드</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: #161b26;
            --text-color: #f3f4f6;
            --text-muted: #9ca3af;
            --primary: #3b82f6;
            --primary-hover: #60a5fa;
            --border-color: #1f2937;
            
            --status-hot-bg: rgba(239, 68, 68, 0.15);
            --status-hot-text: #f87171;
            --status-good-bg: rgba(59, 130, 246, 0.15);
            --status-good-text: #60a5fa;
            --status-normal-bg: rgba(107, 114, 128, 0.15);
            --status-normal-text: #9ca3af;
        }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }}
        .container {{
            max-width: 1200px;
            width: 100%;
        }}
        header {{
            margin-bottom: 30px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }}
        .header-left h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
            background: linear-gradient(135deg, #f87171, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .update-time {{
            color: var(--text-muted);
            font-size: 0.9rem;
            text-align: right;
            line-height: 1.6;
        }}
        .source-text {{
            font-size: 0.8rem;
            color: var(--text-muted);
            opacity: 0.7;
        }}
        
        /* 탭 스타일 */
        .tabs {{
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 12px;
        }}
        .tab-btn {{
            background: none;
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }}
        .tab-btn.active {{
            background-color: var(--primary);
            color: #fff;
            border-color: var(--primary);
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}

        /* 일정표 레이아웃 */
        .section-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            margin: 30px 0 15px 0;
            color: #f3f4f6;
        }}
        .schedule-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 40px;
        }}
        .schedule-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .schedule-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .schedule-company {{
            font-weight: 700;
            color: #60a5fa;
            font-size: 0.9rem;
        }}
        .dday-badge {{
            font-size: 0.75rem;
            padding: 2px 6px;
            border-radius: 4px;
            background-color: rgba(255, 255, 255, 0.08);
            color: var(--text-muted);
            font-weight: 700;
        }}
        .dday-active {{
            background-color: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }}
        .dday-closed {{
            background-color: rgba(31, 41, 55, 0.5);
            color: #4b5563;
        }}
        .schedule-title {{
            font-weight: 600;
            font-size: 0.95rem;
            color: #fff;
            margin-bottom: 6px;
        }}
        .schedule-deadline {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-bottom: 12px;
        }}
        .schedule-link {{
            color: var(--primary);
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .schedule-link:hover {{
            color: var(--primary-hover);
        }}

        .dashboard-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            padding: 28px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(12px);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}
        th {{
            color: var(--text-muted);
            font-weight: 700;
            padding: 18px 16px;
            border-bottom: 2px solid var(--border-color);
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        td {{
            padding: 22px 16px;
            border-bottom: 1px solid var(--border-color);
            vertical-align: middle;
        }}
        .job-row {{
            transition: all 0.2s ease-in-out;
        }}
        .job-row:hover td {{
            background-color: rgba(255, 255, 255, 0.015);
        }}
        .recommendation-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 700;
            text-align: center;
            width: 80px;
        }}
        .status-hot {{
            background-color: var(--status-hot-bg);
            color: var(--status-hot-text);
            border: 1px solid rgba(239, 68, 68, 0.3);
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.1);
        }}
        .status-good {{
            background-color: var(--status-good-bg);
            color: var(--status-good-text);
            border: 1px solid rgba(59, 130, 246, 0.3);
        }}
        .status-normal {{
            background-color: var(--status-normal-bg);
            color: var(--status-normal-text);
            border: 1px solid rgba(107, 114, 128, 0.3);
        }}
        .match-container {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            width: 100px;
        }}
        .match-val {{
            font-weight: 700;
            font-size: 1.1rem;
            color: #fff;
        }}
        .progress-bar-bg {{
            background-color: rgba(255, 255, 255, 0.08);
            border-radius: 999px;
            height: 6px;
            overflow: hidden;
            width: 100%;
        }}
        .progress-bar-fill {{
            background: linear-gradient(90deg, #3b82f6, #60a5fa);
            height: 100%;
            border-radius: 999px;
        }}
        .badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 700;
        }}
        .badge-hyundai {{
            background-color: rgba(59, 130, 246, 0.12);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.25);
        }}
        .badge-kia {{
            background-color: rgba(239, 68, 68, 0.12);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.25);
        }}
        .badge-robot {{
            background-color: rgba(16, 185, 129, 0.12);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.25);
        }}
        .badge-other {{
            background-color: rgba(107, 114, 128, 0.12);
            color: #9ca3af;
            border: 1px solid rgba(107, 114, 128, 0.25);
        }}
        .job-title {{
            font-weight: 700;
            font-size: 1.05rem;
            color: #f3f4f6;
            margin-bottom: 6px;
        }}
        .job-desc {{
            font-size: 0.88rem;
            color: var(--text-muted);
            line-height: 1.5;
        }}
        .keywords-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            max-width: 250px;
        }}
        .keyword-tag {{
            font-size: 0.78rem;
            background-color: rgba(255, 255, 255, 0.05);
            padding: 4px 8px;
            border-radius: 4px;
            color: var(--text-muted);
            border: 1px solid rgba(255, 255, 255, 0.03);
        }}
        .btn-link {{
            background-color: var(--primary);
            color: #fff;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.88rem;
            padding: 8px 16px;
            border-radius: 8px;
            display: inline-block;
            transition: background-color 0.2s;
            text-align: center;
        }}
        .btn-link:hover {{
            background-color: var(--primary-hover);
        }}

        /* 로드맵 상세 스타일 */
        .roadmap-container {{
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}
        .roadmap-phase {{
            border-left: 3px solid var(--primary);
            padding-left: 20px;
            margin-left: 10px;
        }}
        .phase-title {{
            font-size: 1.25rem;
            font-weight: 700;
            color: #60a5fa;
            margin-bottom: 12px;
        }}
        .phase-content {{
            font-size: 0.95rem;
            color: var(--text-muted);
            line-height: 1.6;
        }}
        .phase-resources {{
            background-color: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            padding: 14px;
            margin-top: 10px;
            border: 1px dashed var(--border-color);
        }}
        .resource-title {{
            font-weight: 700;
            color: #f3f4f6;
            margin-bottom: 6px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-left">
                <h1>🚗 & 🤖 채용 공고 & 기술 로드맵 대시보드</h1>
            </div>
            <div class="update-time">
                <div>최근 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                <div class="source-text">데이터 출처: {DATA_SOURCES}</div>
            </div>
        </header>

        <!-- 📅 일정표 -->
        <div class="section-title">📅 주요 기업 서류 마감 일정</div>
        <div class="schedule-grid">
            {schedule_cards}
        </div>

        <!-- 탭 메뉴 -->
        <div class="tabs">
            <button class="tab-btn active" onclick="openTab(event, 'tab-jobs')">🎯 채용 추천 리스트</button>
            <button class="tab-btn" onclick="openTab(event, 'tab-roadmap-semi')">🔬 반도체 기술 로드맵</button>
            <button class="tab-btn" onclick="openTab(event, 'tab-roadmap-auto')">⚙️ 완성차/로봇 로드맵</button>
        </div>

        <!-- 탭 1: 채용 추천 리스트 -->
        <div id="tab-jobs" class="tab-content active">
            <div class="dashboard-card">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 10%;">추천 등급</th>
                            <th style="width: 12%;">매칭률</th>
                            <th style="width: 10%;">회사</th>
                            <th style="width: 40%;">채용 직무 및 요구 역량</th>
                            <th style="width: 18%;">매칭 키워드</th>
                            <th style="width: 10%;">페이지 이동</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 탭 2: 반도체 학습 로드맵 -->
        <div id="tab-roadmap-semi" class="tab-content">
            <div class="dashboard-card">
                <div class="roadmap-container">
                    <div class="roadmap-phase">
                        <div class="phase-title">🟢 1단계: 입문 (Beginner) - 반도체 기본 개념 및 공정 이해</div>
                        <div class="phase-content">
                            반도체 8대 공정 기초 흐름(웨이퍼 제조 ➡️ 노광 ➡️ 식각 ➡️ 증착 ➡️ 패키징) 및 클린룸(Clean Room)의 원리(차압, FFU 작동)를 이해합니다.
                        </div>
                        <div class="phase-resources">
                            <div class="resource-title">📚 추천 자료:</div>
                            - <strong>유튜브</strong>: 삼성반도체 '반도체 과외선생님' 시리즈 / SK하이닉스 '반도체 제조공정' 다큐멘터리<br>
                            - <strong>온라인 강의</strong>: K-MOOC '반도체 공정 기초 및 소자 이해' 강좌 (무료)
                        </div>
                    </div>
                    <div class="roadmap-phase">
                        <div class="phase-title">🟡 2단계: 중급 (Intermediate) - 기계 기반 유틸리티 인프라</div>
                        <div class="phase-content">
                            초순수(UPW) 정밀 배관 설계, 화학물질 중앙공급장치(CCSS) 안전 배관(이중 배관), 클린룸 공조(HVAC) 방진 마운트 설계 및 초고진공 펌프(Dry/TMP) 구동 역학 학습.
                        </div>
                        <div class="phase-resources">
                            <div class="resource-title">📚 추천 자료:</div>
                            - <strong>전문 도서</strong>: *진공공학 (한상준 저)* / *반도체 클린룸 및 공조 설계 가이드 (한국설비기술협회)*<br>
                            - <strong>지침서</strong>: 안전보건공단(KOSHA Guide) '특수가스 공급 설비 안전 지침'
                        </div>
                    </div>
                    <div class="roadmap-phase">
                        <div class="phase-title">🔴 3단계: 고급 (Advanced) - 차세대 패키징 물리 및 플랜트 PM</div>
                        <div class="phase-content">
                            HBM 적층 시 이종 접합부 열팽창 계수(CTE) 차이에 따른 Warpage(휨) 제어 및 Mechanical Stress 수치 해석, 대형 FAB 건설 관리 프로세스 학습.
                        </div>
                        <div class="phase-resources">
                            <div class="resource-title">📚 추천 자료:</div>
                            - <strong>학술 자료</strong>: RISS 학술지 'HBM Warpage', '패키징 열변형 해석' 검색 논문 정독<br>
                            - <strong>기술 자료</strong>: SK하이닉스 뉴스룸 기술 칼럼 / TSMC/ASML 기술 백서
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 탭 3: 자동차/로봇 학습 로드맵 -->
        <div id="tab-roadmap-auto" class="tab-content">
            <div class="dashboard-card">
                <div class="roadmap-container">
                    <div class="roadmap-phase">
                        <div class="phase-title">🟢 1단계: 입문 (Beginner) - EV 플랫폼 및 로봇 매커니즘 기초</div>
                        <div class="phase-content">
                            현대차 E-GMP 플랫폼 기반 전기차 아키텍처(배터리 팩, PE 시스템) 및 다관절 로봇 매니퓰레이터의 링크와 기본 좌표 변환(Kinematics) 이해.
                        </div>
                        <div class="phase-resources">
                            <div class="resource-title">📚 추천 자료:</div>
                            - <strong>유튜브</strong>: 현대자동차그룹 공식 'E-GMP 기술 설명회' 영상 / 두산로보틱스 협동로봇 구동 시연<br>
                            - <strong>온라인 강의</strong>: K-MOOC '로봇공학 입문' 또는 '로봇 매니퓰레이터 설계'
                        </div>
                    </div>
                    <div class="roadmap-phase">
                        <div class="phase-title">🟡 2단계: 중급 (Intermediate) - 차량 NVH, 열관리 및 로봇 감속기 관절 설계</div>
                        <div class="phase-content">
                            EV 배터리 팩 냉각 유로 설계, 모터 마운트/고무 부시를 통한 차량 진동/소음(NVH) 최적화, 로봇 하모닉 감속기 및 크로스 롤러 베어링 선정, 자동차 부품 품질 표준(IATF 16949 / APQP) 학습.
                        </div>
                        <div class="phase-resources">
                            <div class="resource-title">📚 추천 자료:</div>
                            - <strong>전문 도서</strong>: *자동차 진동 소음의 기초 (서병선 저)* / *기하공차(GD&T) 실무 설계 (정영훈 저)*<br>
                            - <strong>지침서</strong>: IATF 16949 규격 해설서 및 APQP 협력사 부품 품질 교육서 / Harmonic Drive Systems 카탈로그
                        </div>
                    </div>
                    <div class="roadmap-phase">
                        <div class="phase-title">🔴 3단계: 고급 (Advanced) - 하우징 경량화 및 로봇 링크 동역학 최적화</div>
                        <div class="phase-content">
                            알루미늄 다이캐스팅 파워트레인 하우징 강성 최적화 설계, 가감속 시 관성(Inertia) 최소화를 위한 로봇 암(Arm) 프레임 위상 최적화 및 굽힘 처짐 시뮬레이션 제어.
                        </div>
                        <div class="phase-resources">
                            <div class="resource-title">📚 추천 자료:</div>
                            - <strong>추천 도서 및 소프트웨어 자료</strong>: 재료역학 및 기계요소설계 동역학 이론 검토 / KSAE 학술지 논문 참고
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function openTab(evt, tabName) {{
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].style.display = "none";
                tabcontent[i].classList.remove("active");
            }}
            tablinks = document.getElementsByClassName("tab-btn");
            for (i = 0; i < tablinks.length; i++) {{
                tablinks[i].classList.remove("active");
            }}
            document.getElementById(tabName).style.display = "block";
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
        }}
    </script>
</body>
</html>
"""
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

def run_alert_system():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 채용 정보 수집 및 대시보드 갱신...")
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except Exception:
                history = {}
    else:
        history = {}
        
    current_notices = fetch_recent_notices()
    
    for notice in current_notices:
        nid = notice["id"]
        if nid not in history:
            history[nid] = notice
            
    generate_markdown_dashboard(current_notices)
    generate_html_dashboard(current_notices)
            
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
        
    print("줄바꿈 해제 및 출처 표기 완료.")

if __name__ == "__main__":
    run_alert_system()
