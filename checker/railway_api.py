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
    
    async def update_service_branch(self, service_id: str, branch_name: str) -> Dict[str, Any]:
        """서비스의 GitHub 브랜치 변경"""
        # GraphiQL에서 확인된 정확한 스키마
        mutation = """
        mutation serviceConnect($id: String!, $input: ServiceConnectInput!) {
            serviceConnect(id: $id, input: $input) {
                id
                name
                updatedAt
                source {
                    repo
                    branch
                }
            }
        }
        """
        
        variables = {
            "id": service_id,
            "input": {
                "branch": branch_name
            }
        }
        
        logger.info(f"서비스 {service_id}의 브랜치를 {branch_name}으로 변경 시도 중...")
        result = await self._execute_query(mutation, variables)
        logger.info(f"브랜치 변경 성공: {result}")
        return result


# 편의 함수들
async def switch_to_branch(branch_name: str) -> bool:
    """
    브랜치 전환 편의 함수
    
    Args:
        branch_name: 전환할 브랜치명 ('main' 또는 'test')
        
    Returns:
        bool: 성공 여부
    """
    try:
        import os
        
        # Railway 설정 읽기
        service_id = os.getenv("RAILWAY_SERVICE_ID")
        if not service_id:
            logger.error("RAILWAY_SERVICE_ID 환경변수가 설정되지 않았습니다")
            return False
        
        # Railway API 클라이언트 생성
        railway_api = RailwayAPI()
        
        # 브랜치 전환
        result = await railway_api.update_service_branch(service_id, branch_name)
        
        if result and "data" in result:
            logger.info(f"브랜치 '{branch_name}' 전환 성공")
            return True
        else:
            logger.error(f"브랜치 '{branch_name}' 전환 실패: {result}")
            return False
            
    except Exception as e:
        logger.error(f"브랜치 전환 중 오류 발생: {e}")
        return False
    
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


async def switch_to_branch(branch_name: str) -> bool:
    """
    지정된 브랜치로 전환하고 재배포
    
    Args:
        branch_name: 전환할 브랜치 이름 ("main", "test" 등)
    
    Returns:
        bool: 성공 여부
    """
    try:
        if not RAILWAY_PROJECT_ID or not RAILWAY_SERVICE_ID:
            logger.error("RAILWAY_PROJECT_ID 또는 RAILWAY_SERVICE_ID가 설정되지 않았습니다")
            return False
        
        if branch_name not in BRANCH_THEME_MAPPING:
            logger.error(f"지원하지 않는 브랜치: {branch_name}")
            return False
        
        railway_api = RailwayAPI()
        
        # 1. 브랜치 변경
        await railway_api.update_service_branch(RAILWAY_SERVICE_ID, branch_name)
        
        # 2. 재배포 트리거
        await railway_api.trigger_deployment(RAILWAY_SERVICE_ID)
        
        # 3. 로컬 config도 업데이트 (필요시)
        # update_local_theme_config(BRANCH_THEME_MAPPING[branch_name])
        
        logger.info(f"✅ {branch_name} 브랜치로 성공적으로 전환되었습니다")
        return True
        
    except Exception as e:
        logger.error(f"❌ 브랜치 전환 실패: {e}")
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