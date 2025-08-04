# -*- coding: utf-8 -*-
"""
Railway API 클라이언트 모듈

Railway GraphQL API를 사용해서 서비스 설정을 변경하는 기능 제공
"""

import os
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from loguru import logger


class RailwayAPI:
    """Railway GraphQL API 클라이언트"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("RAILWAY_API_TOKEN")
        self.graphql_url = "https://backboard.railway.com/graphql/v2"
        
        if not self.api_token:
            logger.warning("Railway API 토큰이 설정되지 않았습니다. 환경변수 RAILWAY_API_TOKEN을 설정하세요.")
    
    async def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GraphQL 쿼리 실행"""
        if not self.api_token:
            raise ValueError("Railway API 토큰이 설정되지 않았습니다")
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.graphql_url,
                json=payload,
                headers=headers
            ) as response:
                result = await response.json()
                
                if response.status != 200:
                    logger.error(f"Railway API 요청 실패: {response.status} - {result}")
                    raise Exception(f"Railway API 오류: {result}")
                
                if "errors" in result:
                    logger.error(f"GraphQL 오류: {result['errors']}")
                    raise Exception(f"GraphQL 오류: {result['errors']}")
                
                return result
    
    async def get_project_services(self, project_id: str) -> Dict[str, Any]:
        """프로젝트의 서비스 목록 조회"""
        query = """
        query getProject($projectId: String!) {
            project(id: $projectId) {
                id
                name
                services {
                    edges {
                        node {
                            id
                            name
                            source {
                                repo
                                branch
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {"projectId": project_id}
        return await self._execute_query(query, variables)
    
    async def get_service_info(self, service_id: str) -> Dict[str, Any]:
        """서비스 정보 조회 (간단한 스키마)"""
        query = """
        query {
            me {
                projects {
                    edges {
                        node {
                            id
                            name
                            services {
                                edges {
                                    node {
                                        id
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        logger.info(f"서비스 {service_id} 정보 조회 중 (간단한 스키마)...")
        result = await self._execute_query(query)
        logger.info(f"서비스 정보: {result}")
        return result

    async def update_service_branch(self, service_id: str, branch_name: str) -> Dict[str, Any]:
        """서비스의 GitHub 브랜치 변경 (Railway API v2 스키마 기반)"""
        
        # 서비스 정보 먼저 가져오기 (필수 정보 수집)
        service_info = await self.get_service_info(service_id)
        current_repo = None
        current_branch = None
        
        if service_info and "data" in service_info and service_info["data"]["service"]:
            source = service_info["data"]["service"]["source"]
            if source:
                current_repo = source.get("repo")
                current_branch = source.get("branch")
                logger.info(f"📋 현재 상태 - 리포: {current_repo}, 브랜치: {current_branch}")
        
        if not current_repo:
            raise ValueError("리포지토리 정보를 가져올 수 없습니다. GitHub 연결을 확인하세요.")
        
        # 방법 1: serviceSourceUpdate (정확한 Railway v2 API)
        mutation_v1 = """
        mutation serviceSourceUpdate($serviceId: String!, $input: ServiceSourceUpdateInput!) {
            serviceSourceUpdate(serviceId: $serviceId, input: $input) {
                id
                name
                source {
                    repo
                    branch
                }
            }
        }
        """
        
        variables_v1 = {
            "serviceId": service_id,
            "input": {
                "branch": branch_name
            }
        }
        
        try:
            logger.info(f"🔄 방법 1: serviceSourceUpdate로 브랜치 '{branch_name}' 변경 시도...")
            result = await self._execute_query(mutation_v1, variables_v1)
            logger.info(f"✅ serviceSourceUpdate 성공: {result}")
            return result
        except Exception as e:
            logger.warning(f"⚠️ serviceSourceUpdate 실패: {e}")
            
        # 방법 2: serviceConnect (전체 재연결)
        mutation_v2 = """
        mutation serviceConnect($id: String!, $input: ServiceConnectInput!) {
            serviceConnect(id: $id, input: $input) {
                id
                name
                source {
                    repo
                    branch
                }
            }
        }
        """
        
        variables_v2 = {
            "id": service_id,
            "input": {
                "repo": current_repo,
                "branch": branch_name
            }
        }
        
        try:
            logger.info(f"🔄 방법 2: serviceConnect로 브랜치 '{branch_name}' 변경 시도...")
            logger.info(f"📋 연결 정보: repo={current_repo}, branch={branch_name}")
            result = await self._execute_query(mutation_v2, variables_v2)
            logger.info(f"✅ serviceConnect 성공: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ serviceConnect도 실패: {e}")
            
        # 방법 3: serviceDeploy (브랜치 지정 배포)
        mutation_v3 = """
        mutation serviceDeploy($serviceId: String!, $input: ServiceDeployInput!) {
            serviceDeploy(serviceId: $serviceId, input: $input) {
                id
                status
                createdAt
            }
        }
        """
        
        variables_v3 = {
            "serviceId": service_id,
            "input": {
                "branch": branch_name
            }
        }
        
        try:
            logger.info(f"🔄 방법 3: serviceDeploy로 브랜치 '{branch_name}' 배포 시도...")
            result = await self._execute_query(mutation_v3, variables_v3)
            logger.info(f"✅ serviceDeploy 성공: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ serviceDeploy도 실패: {e}")
            raise Exception(f"모든 Railway API 방법 실패. 마지막 오류: {e}")


    async def trigger_deployment(self, service_id: str) -> Dict[str, Any]:
        """서비스 재배포 트리거"""
        mutation = """
        mutation serviceInstanceRedeploy($serviceId: String!) {
            serviceInstanceRedeploy(serviceId: $serviceId) {
                id
                createdAt
                status
            }
        }
        """
        
        variables = {"serviceId": service_id}
        
        logger.info(f"서비스 {service_id} 재배포 트리거 중...")
        result = await self._execute_query(mutation, variables)
        logger.info(f"재배포 트리거 성공: {result}")
        return result


# 환경변수 설정
RAILWAY_PROJECT_ID = os.getenv("RAILWAY_PROJECT_ID")
RAILWAY_SERVICE_ID = os.getenv("RAILWAY_SERVICE_ID")

# 브랜치별 테마 매핑
BRANCH_THEME_MAPPING = {
    "main": "층간소음",
    "test": "사랑하는감?",
    # 필요시 더 추가 가능
}


# 편의 함수들
async def switch_to_branch_cli(branch_name: str) -> bool:
    """
    Railway CLI를 사용한 브랜치 전환 (대안 방법)
    """
    try:
        import subprocess
        import os
        
        logger.info(f"🚂 Railway CLI로 브랜치 '{branch_name}' 전환 시도...")
        
        # Railway CLI 명령어 실행
        result = subprocess.run([
            "railway", "service", "update", 
            "--source-branch", branch_name
        ], capture_output=True, text=True, cwd="/app" if os.path.exists("/app") else ".")
        
        if result.returncode == 0:
            logger.info(f"✅ Railway CLI로 브랜치 '{branch_name}' 전환 성공")
            return True
        else:
            logger.error(f"❌ Railway CLI 실패: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Railway CLI 브랜치 전환 실패: {e}")
        return False

async def switch_to_branch(branch_name: str) -> bool:
    """
    지정된 브랜치로 전환하고 재배포
    
    Args:
        branch_name: 전환할 브랜치 이름 ("main", "test" 등)
    
    Returns:
        bool: 성공 여부
    """
    try:
        # 1. 환경변수 확인 및 상세 로깅
        api_token = os.getenv("RAILWAY_API_TOKEN")
        project_id = os.getenv("RAILWAY_PROJECT_ID") 
        service_id = os.getenv("RAILWAY_SERVICE_ID")
        
        logger.info(f"🔧 브랜치 '{branch_name}' 전환 시도...")
        logger.info(f"  - API 토큰: {'✅ 설정됨' if api_token else '❌ 미설정'}")
        logger.info(f"  - 프로젝트 ID: {'✅ 설정됨' if project_id else '❌ 미설정'}")
        logger.info(f"  - 서비스 ID: {'✅ 설정됨' if service_id else '❌ 미설정'}")
        
        if not api_token:
            logger.error("❌ RAILWAY_API_TOKEN 환경변수가 설정되지 않았습니다")
            logger.error("   Railway 대시보드에서 API 토큰을 생성하고 환경변수에 추가하세요")
            return False
            
        if not service_id:
            logger.error("❌ RAILWAY_SERVICE_ID 환경변수가 설정되지 않았습니다")
            logger.error("   Railway 대시보드에서 서비스 ID를 확인하고 환경변수에 추가하세요")
            return False
        
        if branch_name not in BRANCH_THEME_MAPPING:
            logger.error(f"❌ 지원하지 않는 브랜치: {branch_name}")
            logger.error(f"   지원하는 브랜치: {list(BRANCH_THEME_MAPPING.keys())}")
            return False
        
        # 2. Railway API 클라이언트 생성
        railway_api = RailwayAPI(api_token)
        
        # 2.5. 서비스 정보 먼저 확인
        logger.info(f"📋 서비스 정보 확인 중...")
        try:
            service_info = await railway_api.get_service_info(service_id)
            if service_info and "data" in service_info:
                current_branch = service_info["data"]["service"]["source"]["branch"]
                current_repo = service_info["data"]["service"]["source"]["repo"]
                logger.info(f"  - 현재 브랜치: {current_branch}")
                logger.info(f"  - 연결된 리포지토리: {current_repo}")
                
                if current_branch == branch_name:
                    logger.info(f"✅ 이미 {branch_name} 브랜치입니다!")
                    return True
        except Exception as e:
            logger.warning(f"⚠️ 서비스 정보 확인 실패 (계속 진행): {e}")
        
        # 3. 브랜치 변경
        logger.info(f"🔄 브랜치 '{branch_name}' 변경 중...")
        branch_result = await railway_api.update_service_branch(service_id, branch_name)
        logger.info(f"브랜치 변경 결과: {branch_result}")
        
        # 4. 재배포 트리거
        logger.info(f"🚀 재배포 트리거 중...")
        deploy_result = await railway_api.trigger_deployment(service_id)
        logger.info(f"재배포 결과: {deploy_result}")
        
        logger.info(f"✅ {branch_name} 브랜치로 성공적으로 전환되었습니다")
        return True
        
    except ValueError as e:
        logger.error(f"❌ 설정 오류: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 브랜치 전환 실패: {type(e).__name__}: {str(e)}")
        logger.error(f"   상세 오류: {e}")
        return False


def test_railway_settings() -> bool:
    """
    Railway API 설정 상태 확인
    
    Returns:
        bool: 모든 필수 설정이 완료되었는지 여부
    """
    try:
        import os
        
        # 환경변수 확인
        api_token = os.getenv("RAILWAY_API_TOKEN")
        project_id = os.getenv("RAILWAY_PROJECT_ID") 
        service_id = os.getenv("RAILWAY_SERVICE_ID")
        
        logger.info("🔧 Railway API 설정 상태:")
        logger.info(f"  - RAILWAY_API_TOKEN: {'✅ 설정됨' if api_token else '❌ 미설정'}")
        logger.info(f"  - RAILWAY_PROJECT_ID: {'✅ 설정됨' if project_id else '❌ 미설정'}")
        logger.info(f"  - RAILWAY_SERVICE_ID: {'✅ 설정됨' if service_id else '❌ 미설정'}")
        
        missing_vars = []
        if not api_token:
            missing_vars.append("RAILWAY_API_TOKEN")
        if not service_id:
            missing_vars.append("RAILWAY_SERVICE_ID")
            
        if missing_vars:
            logger.error(f"\n❌ 누락된 환경변수: {', '.join(missing_vars)}")
            logger.error("\n📖 설정 방법:")
            logger.error("1. Railway 대시보드 (railway.app) 접속")
            logger.error("2. 프로젝트 선택 → Settings → Tokens")
            logger.error("3. 새 토큰 생성 후 RAILWAY_API_TOKEN에 설정")
            logger.error("4. 서비스 페이지에서 Service ID 복사 후 RAILWAY_SERVICE_ID에 설정")
            logger.error("\n🔧 Railway 환경변수 설정:")
            logger.error("   Variables 탭에서 위 환경변수들 추가")
            return False
        
        logger.info("\n✅ 모든 필수 환경변수가 설정되었습니다!")
        logger.info("💡 이제 /branch main 또는 /branch test 명령어를 사용할 수 있습니다.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Railway 설정 확인 중 오류: {e}")
        return False


def update_local_theme_config(theme_name: str):
    """
    로컬 config.py 파일의 테마 이름 업데이트
    """
    try:
        config_path = "checker/config.py"
        
        # config.py 파일 읽기
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # THEME_NAME 라인 찾아서 교체
        import re
        pattern = r'THEME_NAME = ".*?"'
        replacement = f'THEME_NAME = "{theme_name}"'
        
        updated_content = re.sub(pattern, replacement, content)
        
        # 파일에 다시 쓰기
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info(f"로컬 config 업데이트: THEME_NAME = '{theme_name}'")
        
    except Exception as e:
        logger.error(f"로컬 config 업데이트 실패: {e}")