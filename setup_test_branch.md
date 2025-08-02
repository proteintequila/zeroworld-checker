# 테스트 브랜치 설정 가이드

## 1. 테스트 브랜치 생성

```bash
# 현재 main 브랜치에서 test 브랜치 생성
git checkout -b test

# config.py에서 테마 변경
# THEME_NAME = "층간소음" -> THEME_NAME = "사랑하는감?"
```

## 2. config.py 수정

test 브랜치에서 다음과 같이 수정:

```python
# 모니터링 대상 설정
THEME_NAME = "사랑하는감?"  # 기존: "층간소음"
```

## 3. Git 커밋 및 푸시

```bash
git add .
git commit -m "feat: test 브랜치용 테마 변경 - 사랑하는감?"
git push origin test
```

## 4. Railway 환경변수 설정

Railway 대시보드에서 다음 환경변수들을 추가:

```
RAILWAY_API_TOKEN=your_railway_api_token_here
RAILWAY_PROJECT_ID=your_project_id_here
RAILWAY_SERVICE_ID=your_service_id_here
```

### Railway API 토큰 생성 방법:

1. Railway 대시보드 → Account Settings → Tokens
2. "Create Token" 클릭
3. Account Token 생성 (Team이 있다면 Team Token도 가능)
4. 생성된 토큰을 `RAILWAY_API_TOKEN` 환경변수에 설정

### Project ID / Service ID 확인 방법:

1. Railway 프로젝트에서 `Cmd/Ctrl + K` 누르기
2. "Copy Project ID" 또는 "Copy Service ID" 선택
3. 복사된 ID를 해당 환경변수에 설정

## 5. 텔레그램 봇 명령어 사용법

배포 후 텔레그램에서 다음 명령어 사용:

```
/branch test   # 테스트 브랜치로 전환 (사랑하는감? 테마)
/branch main   # 메인 브랜치로 전환 (층간소음 테마)
/help          # 모든 명령어 확인
```

## 6. 주의사항

- 브랜치 전환 시 새로운 배포가 시작되며 약 2-3분 소요됩니다
- Railway API 호출에 실패할 경우 로그를 확인하세요
- GraphQL mutation이 실제 Railway API 스키마와 다를 수 있으니 필요시 수정이 필요할 수 있습니다

## 7. 문제 해결

### Railway API 호출 실패 시:

1. Railway GraphiQL playground 접속: https://backboard.railway.com/graphql/v2
2. Authorization 헤더에 토큰 설정
3. 실제 스키마 확인 후 `railway_api.py`의 mutation 수정

### 예시 스키마 확인 쿼리:

```graphql
query {
  __schema {
    mutationType {
      fields {
        name
        description
      }
    }
  }
}
```