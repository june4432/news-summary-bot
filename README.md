# 🤖 AI 뉴스 요약 봇

뉴스 요약 봇은 AI를 활용하여 최신 뉴스를 요약하고, 사용자가 설정한 시간에 맞춰 관심 카테고리의 뉴스를 제공하는 서비스입니다. Flask 기반의 백엔드와 React/Vite 기반의 프론트엔드로 구성되어 있으며, PM2를 통해 안정적으로 운영됩니다.

---

## 📚 프로젝트 개요

* **뉴스 요약**: AI가 다양한 뉴스 소스에서 기사를 수집하고 핵심 내용을 요약합니다.
* **개인 맞춤형 뉴스레터**: 사용자는 웹 인터페이스를 통해 닉네임, 관심 카테고리, 수신 시간대를 설정할 수 있습니다.
* **정기 알림**: 설정된 시간에 맞춰 요약된 뉴스레터를 받아볼 수 있습니다.
* **기술 스택**: Python (Flask, Gunicorn), JavaScript (React, Vite), Nginx, PM2, Docker (Nginx).

---

## 📁 디렉토리 구조

프로젝트는 모듈화된 백엔드와 프론트엔드로 구성되어 있습니다.
```
news-summary-bot/
├── .github/                             # GitHub Actions (CI/CD 등) 설정
├── backend/                             # Flask 백엔드 애플리케이션
│   ├── batch/                           # 배치 처리 스크립트 (뉴스 수집, 요약 등)
│   │   ├── util/                        # 유틸리티 모듈 (RSS 파싱 등)
│   │   └── .env                         # 배치 및 백엔드 환경 변수 (예: API 키, rss_batch_count)
│   ├── venv/                            # Python 가상 환경 (Git 추적 제외)
│   ├── server.py                        # Flask 메인 애플리케이션 파일
│   ├── ecosystem.config.cjs             # PM2 백엔드 프로세스 설정 파일
│   ├── requirements.txt                 # Python 의존성 목록
│   └── tests/                           # 백엔드 테스트 코드
├── data/                                # 데이터 파일 (예: rss_sources.json - RSS 피드 정보)
│   ├── recipients_email.json            # 실제 이메일 구독자 명단
│   ├── recipients_email_sample.json     # 이메일 구독자 명단 샘플
│   ├── recipients_telegram.json         # 실제 텔레그램 구독자 명단
│   ├── recipients_telegram_sample.json  # 텔레그램 구독자 명단 샘플
├── frontend/                            # React/Vite 프론트엔드 애플리케이션
│   ├── public/                          # 정적 파일 (index.html, favicon.ico 등)
│   ├── src/                             # React 소스 코드
│   │   ├── assets/                      # 이미지, 폰트 등 정적 자산
│   │   ├── components/                  # 재사용 가능한 UI 컴포넌트
│   │   ├── pages/                       # 개별 웹 페이지 컴포넌트
│   │   ├── styles/                      # CSS 스타일 파일
│   │   ├── App.jsx                      # React 메인 애플리케이션 (JavaScript 버전)
│   │   └── App.tsx                      # React 메인 애플리케이션 (TypeScript 버전)
│   ├── vite.config.js                   # Vite 설정 파일
│   ├── ecosystem.config.cjs             # PM2 프론트엔드 프로세스 설정 파일
│   ├── package.json                     # Node.js 의존성 및 스크립트
│   └── tsconfig.json                    # TypeScript 설정
├── frontend/                            # React/Vite 프론트엔드 애플리케이션
├── .gitignore                           # Git 추적에서 제외할 파일/디렉토리 목록
├── LICENSE                              # 라이선스 정보
└── README.md                            # 프로젝트 설명 (현재 파일)
```

---

## 🚀 시작하기

### 📋 사전 준비

* **Python 3.9+**: 백엔드 실행을 위해 필요합니다.
* **Node.js (LTS 버전) 및 npm**: 프론트엔드 실행을 위해 필요합니다. [`nvm`](https://github.com/nvm-sh/nvm) 사용을 권장합니다.
* **PM2**: 프로세스 관리를 위해 필요합니다 (`npm install pm2 -g`).
* **Docker**: Nginx 프록시 서버 운영을 위해 필요합니다.
* **Gunicorn**: Flask 앱을 위한 WSGI 서버입니다.

### ⚙️ 설정 및 실행

#### 1. 프로젝트 클론

```bash
git clone [https://github.com/june4432/news-summary-bot.git](https://github.com/june4432/news-summary-bot.git)
cd news-summary-bot
```

#### 2. 백엔드 설정
```
cd backend/
python3 -m venv venv           # 가상 환경 생성
source venv/bin/activate       # 가상 환경 활성화
pip install -r requirements.txt # 의존성 설치 (requirements.txt가 없다면 수동 설치)
pip install python-dotenv      # .env 파일 로드를 위해 설치

# .env 파일 생성 및 설정 (backend/batch/.env 경로에)
# RSS_BATCH_COUNT, SECRET_TOKEN_FOR_LOGIN 등 필요한 환경 변수를 설정합니다.
# 예: RSS_BATCH_COUNT=10
# 예: SECRET_TOKEN_FOR_LOGIN="your_super_secret_jwt_key"
# 예: NEWSLETTER_URL="[https://leeyoungjun.duckdns.org/news-bot](https://leeyoungjun.duckdns.org/news-bot)" # 프론트엔드 URL
# .env 파일의 경로가 backend/batch/.env 이므로, ecosystem.config.cjs에서 해당 경로를 정확히 지정해야 합니다.

# PM2 설정 파일(ecosystem.config.cjs) 업데이트
# cwd 및 interpreter 경로가 현재 시스템에 맞는지 확인합니다.
# env_file: "../batch/.env" 가 .env 파일 경로를 정확히 가리키는지 확인합니다.
# server.py 내에서 load_dotenv() 코드는 제거합니다 (PM2가 로드하므로).
# 예시: interpreter: "/home/pi/project/news-summary-bot/backend/venv/bin/python3"

# PM2로 백엔드 앱 실행
pm2 start ecosystem.config.cjs
pm2 logs newsbot-backend-app # 로그 확인
```

#### 3. 프론트엔드 설정
```
cd ../newsletter-frontend/   # 프론트엔드 디렉토리로 이동
npm install                  # Node.js 의존성 설치

# Vite 설정 파일(vite.config.js) 업데이트
# base: '/news-bot/' 설정이 정확한지 확인합니다.
# server.host: '0.0.0.0' 또는 true로 설정하여 외부 접근을 허용합니다.

# React Router (src/App.jsx 또는 App.tsx) 설정
# <BrowserRouter basename="/news-bot"> 로 설정하여 서브 경로를 인지시킵니다.

# PM2 설정 파일(ecosystem.config.cjs) 업데이트
# cwd 및 interpreter 경로가 현재 시스템에 맞는지 확인합니다.
# 예시: interpreter: "/home/pi/.nvm/versions/node/v20.19.4/bin/node"

# PM2로 프론트엔드 앱 실행
pm2 start ecosystem.config.cjs
pm2 logs newsbot-frontend-app # 로그 확인
```

#### 4. Nginx 설정 (Docker)
Nginx를 Docker로 운영하는 경우, nginx.conf 파일을 업데이트해야 합니다.
- http 블록 내에 upstream 서버들을 정의합니다 (newsbotgateway, newsbotfrontend 등).
- server 블록 내에 다음 location 규칙들을 추가/수정합니다.
```
# ... (http 블록 내부) ...
    upstream newsbotfrontend {
        server 192.168.0.65:5173; # 프론트엔드 개발 서버 IP:포트
    }
    upstream newsbotgateway {
        server 192.168.0.65:3200; # Flask 백엔드 서버 IP:포트
    }
# ...

server {
    listen 80;
    server_name leeyoungjun.duckdns.org;
    return 301 https://$host$request_uri; # HTTP -> HTTPS 리다이렉트
}

server {
    listen 443 ssl;
    server_name leeyoungjun.duckdns.org;
    ssl_certificate /etc/letsencrypt/live/leeyoungjun.duckdns.org-0002/fullchain.pem; # 실제 경로
    ssl_certificate_key /etc/letsencrypt/live/leeyoungjun.duckdns.org-0002/privkey.pem; # 실제 경로

    # 뉴스봇 프론트엔드 (SPA) 서브 경로 설정
    location /news-bot/ {
        proxy_pass http://newsbotfrontend; # 👈 중요: proxy_pass 뒤에 슬래시 없음
        # ... (proxy_set_header 들) ...
    }
    # /news-bot (슬래시 없는 경우) -> /news-bot/ 으로 리다이렉트
    location = /news-bot {
        return 301 /news-bot/;
    }

    # 사용자 설정 페이지 링크에 대한 Nginx 리다이렉션 (프론트엔드 앱으로)
    location = /preferences {
        return 301 /news-bot/preferences$is_args$args;
    }

    # 뉴스봇 백엔드 API 경로 설정 (newsbotgateway)
    location /news-settings {
        proxy_pass http://newsbotgateway;
        # ... (proxy_set_header 들) ...
    }
    location /get-categories {
        proxy_pass http://newsbotgateway;
        # ... (proxy_set_header 들) ...
    }
    # ... (다른 모든 백엔드 API 경로들: /subscribe, /unsubscribe, /news-click, /webhook, /update-preferences 등) ...

    # 메인 도메인 (루트 /)은 WordPress로 프록시
    location / {
        proxy_pass http://wordpress;
        # ... (proxy_set_header 들) ...
    }
}
```

### Nginx 컨테이너 재로드:
```
docker exec [YOUR_NGINX_CONTAINER_NAME_OR_ID] nginx -t # 설정 문법 검사
docker exec [YOUR_NGINX_CONTAINER_NAME_OR_ID] nginx -s reload # 설정 재로드
```

### 🌐 접속하기
- 모든 설정이 완료되면, 다음 URL로 접속하여 서비스를 확인하세요.
- 뉴스레터 구독/해지 페이지: https://leeyoungjun.duckdns.org/news-bot/
- 설정 페이지 (토큰 포함): https://leeyoungjun.duckdns.org/news-settings?token=YOUR_TOKEN_HERE
- 직접 설정 페이지: https://leeyoungjun.duckdns.org/preferences/?token=YOUR_TOKEN_HERE

🛠️ 개발 & 배포 가이드
- pm2 list: 실행 중인 PM2 프로세스 목록을 확인합니다.
- pm2 logs [app_name]: 특정 앱의 로그를 실시간으로 확인합니다.
- pm2 restart [app_name]: 앱을 재시작합니다.
- pm2 save: 현재 PM2 프로세스 상태를 저장하여 서버 재부팅 시 자동 실행되도록 합니다.
- pm2 startup: 시스템 시작 시 PM2를 실행하도록 스크립트를 생성합니다.

### 🤝 기여하기
프로젝트에 기여하고 싶다면, 이슈를 등록하거나 Pull Request를 보내주세요.

### 📄 라이선스
이 프로젝트는 MIT 라이선스(LICENSE 파일 참조)를 따릅니다.