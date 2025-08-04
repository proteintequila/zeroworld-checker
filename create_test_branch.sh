#!/bin/bash
# test 브랜치 생성 및 푸시 스크립트

echo "🌿 test 브랜치 생성 중..."

# 1. test 브랜치 생성 및 체크아웃
git checkout -b test

# 2. config.py에서 테마 변경 (사랑하는감? 테마로)
echo "⚙️ config.py 테마 변경 중..."
sed -i 's/THEME_NAME = "층간소음"/THEME_NAME = "사랑하는감?"/' checker/config.py

# 또는 Windows에서 (PowerShell 사용 시)
# (Get-Content checker/config.py) -replace 'THEME_NAME = "층간소음"', 'THEME_NAME = "사랑하는감?"' | Set-Content checker/config.py

# 3. UTF-8 인코딩 설정
git config core.quotepath false
git config i18n.commitencoding utf-8
git config i18n.logoutputencoding utf-8

# 4. 변경사항 커밋 및 푸시
echo "📝 커밋 및 푸시 중..."
git add .
git commit -m "Add test branch: 사랑하는감? 테마 모니터링"
git push origin test

echo "✅ test 브랜치 생성 완료!"
echo "💡 이제 Railway에서 /branch test 명령어를 사용할 수 있습니다."