from fastapi import APIRouter, Depends
from app.schemas.agent_schema import AgentMitre, AgentMitreRequest, AgentRansomware, AgentRansomwareRequest, AgentCVE, AgentCVERequest, AgentIoC, AgentIoCRequest, AgentCompliance, AgentComplianceRequest, AgentInfo, AgentInfoRequest, AgentInfoResponse
from app.controllers.auth import AuthController
from app.models.user_db import UserModel
from app.ext.error import UnauthorizedError, PermissionError, InternalServerError
from app.controllers.agent import AgentDetailController
from app.controllers.wazuh import AgentController
from logging import getLogger


logger = getLogger('app_logger')

router = APIRouter()

@router.get("/agent-info", response_model=AgentInfoResponse)
async def get_agent_info(
    agent_name: str,
    current_user: UserModel = Depends(AuthController.get_current_user)
):
    """
    Endpoint to get the agent info.

    Request:
    curl -X 'GET' \
      'https://flask.aixsoar.com/api/agent_detail/agent-info' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer [Token]'
      -d '{"agent_name": "agent_name"}'
    Response:
    {
      "success": true,
      "content": [
        {
          "agent_id": "string",
          "agent_name": "string",
          "ip": "string",
          "os": "string",
          "os_version": "string",
          "agent_status": "string",
          "last_keep_alive": "2023-07-30T12:00:00Z"
        }
      ]
    }
    """
    try:
        if current_user.disabled:
            raise PermissionError("User account is disabled")
        if current_user.user_role == 'admin':
            agent_details = await AgentDetailController.get_agent_info(agent_name)
            return AgentInfoResponse(success=True, message="Agent info retrieved successfully", content=agent_details)
        # here have a logic error that using agent_name to search can pass the permission check: new to add new function to check agent_name    
        user_groups = UserModel.get_user_groups(current_user.id)
        permission_error = await AgentController.check_user_permission(current_user, user_groups)
        if permission_error:
            raise PermissionError("Permission denied")
        agent_details = await AgentDetailController.get_agent_info(agent_name)
        return AgentInfoResponse(success=True, message="Agent info retrieved successfully", content=agent_details)
    except UnauthorizedError:
        raise UnauthorizedError("Authentication required")
    except PermissionError:
        raise PermissionError("Permission denied")
    except Exception as e:
        logger.error(f"Error in get_agent_info endpoint: {e}")
        raise InternalServerError()

@router.get("/agent_mitre", response_model=AgentMitre)
async def get_agent_mitre(
    request: AgentMitreRequest = Depends(),
    current_user: UserModel = Depends(AuthController.get_current_user),
):
    """
    Get the agent mitre data
    Request:
    curl -X 'GET' \
      'https://flask.aixsoar.com/api/agent_detail/agent_mitre?start_time=2024-10-10T00%3A00%3A00&end_time=2024-10-11T00%3A00%3A00' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer Token'
      -d '{"agent_name": "agent_name"}'
    Response:
    {
        "mitre_data": [
        {
            "mitre_tactic": "Defense Evasion",
            "mitre_technique": "Masquerading",
            "mitre_count": 3,
            "mitre_ids": ["T1027", "T1055", "T1078"],
            "rule_description": "Detects the use of Windows Management Instrumentation Command Line Utility (cmd.exe) to masquerade as a legitimate Windows process."
        },
        {
            "mitre_tactic": "Credential Access",
            "mitre_technique": "Brute Force",
            "mitre_count": 2,
            "mitre_ids": ["T1003", "T1003"],
            "rule_description": "Detects the use of Windows Management Instrumentation Command Line Utility (cmd.exe) to masquerade as a legitimate Windows process."
        }
    ]
    }
    """

    try:
        if current_user.disabled:
            raise PermissionError("User account is disabled")
        if current_user.user_role == 'admin':
            mitre_data = await AgentDetailController.get_agent_mitre(request.agent_name, request.start_time, request.end_time)
            return AgentMitre(mitre_data=mitre_data)
        # here have a logic error that using agent_name to search can pass the permission check: new to add new function to check agent_name    
        user_groups = UserModel.get_user_groups(current_user.id)
        permission_error = await AgentController.check_user_permission(current_user, user_groups)
        if permission_error:
            raise PermissionError("Permission denied")
        mitre_data = await AgentDetailController.get_agent_mitre(request.agent_name, request.start_time, request.end_time)
        return AgentMitre(mitre_data=mitre_data)
    except UnauthorizedError:
        raise UnauthorizedError("Authentication required")
    except PermissionError:
        raise PermissionError("Permission denied")
    except Exception as e:
        raise InternalServerError(f"An unexpected error occurred: {str(e)}")

@router.get("/agent_ransomware", response_model=AgentRansomware)
async def get_agent_ransomware(
    request: AgentRansomwareRequest = Depends(),
    current_user: UserModel = Depends(AuthController.get_current_user),
):
    """
    Get the agent ransomware data
    Request:
    curl -X 'GET' \
      'https://flask.aixsoar.com/api/agent_detail/agent_ransomware?start_time=2024-10-10T00%3A00%3A00&end_time=2024-10-11T00%3A00%3A00' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer Token'
      -d '{"agent_name": "test0"}'
    Response:
    {
        "ransomware_data": [
            {
                "name": "VirusTotal: Alert - c:\\users\\admin\\downloads\\unnamed0.zip - 5 engines detected this file",
                "value": 1
            },
            {
                "name": "VirusTotal: Alert - c:\\users\\admin\\downloads\\teslacrypt.zip - 5 engines detected this file",
                "value": 1
            }
        ]
    }
    """
    try:
        if current_user.disabled:
            raise PermissionError("User account is disabled")
        if current_user.user_role == 'admin':
            ransomware_data = await AgentDetailController.get_agent_ransomware(request.agent_name, request.start_time, request.end_time)
            return AgentRansomware(ransomware_data=ransomware_data)
        # here have a logic error that using agent_name to search can pass the permission check: new to add new function to check agent_name    
        user_groups = UserModel.get_user_groups(current_user.id)
        permission_error = await AgentController.check_user_permission(current_user, user_groups)
        if permission_error:
            raise PermissionError("Permission denied")
        ransomware_data = await AgentDetailController.get_agent_ransomware(request.agent_name, request.start_time, request.end_time)
        return AgentRansomware(ransomware_data=ransomware_data)
    except UnauthorizedError:
        raise UnauthorizedError("Authentication required")
    except PermissionError:
        raise PermissionError("Permission denied")
    except Exception as e:
        raise InternalServerError(f"An unexpected error occurred: {str(e)}") 

@router.get("/agent_cve", response_model=AgentCVE)
async def get_agent_cve(
    request: AgentCVERequest = Depends(),
    current_user: UserModel = Depends(AuthController.get_current_user),
):
    """
    Get the agent cve data
    Request:
    curl -X 'GET' \
      'https://flask.aixsoar.com/api/agent_detail/agent_cve?start_time=2024-10-10T00%3A00%3A00&end_time=2024-10-11T00%3A00%3A00' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer Token'
      -d '{"agent_name": "001"}'    
    Response:
    {
        "cve_data": {
        "cve_name": ["CVE-2024-1234", "CVE-2024-1235"],
        "cve_count": 2
        }
    }
    """
    try:
        if current_user.user_role == 'admin':
            group_names = None
        else:
            group_names = UserModel.get_user_groups(current_user.id)    
        if not group_names:
            raise PermissionError("Permission denied")
        cve_data = await AgentDetailController.get_agent_cve(request.agent_id, request.start_time, request.end_time)
        return AgentCVE(cve_data=cve_data)
    except UnauthorizedError:
        raise UnauthorizedError("Authentication required")
    except PermissionError:
        raise PermissionError("Permission denied")
    except Exception as e:
        raise InternalServerError()

@router.get("/agent_ioc", response_model=AgentIoC)
async def get_agent_ioc(
    request: AgentIoCRequest = Depends(),
    current_user: UserModel = Depends(AuthController.get_current_user),
):
    """
    Get the agent ioc data
    Request:
    curl -X 'GET' \
      'https://flask.aixsoar.com/api/agent_detail/agent_ioc?start_time=2024-10-10T00%3A00%3A00&end_time=2024-10-11T00%3A00%3A00' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer Token'
      -d '{"agent_name": "001"}'
    Response:
    {
        "ioc_data": [
        {
            "ioc_type": "phishing_domain",
            "ioc_count": 2,
            "ioc_data": ["example.com", "test.com"]
        },
        {
            "ioc_type": "blacklist_ip",
            "ioc_count": 2,
            "ioc_data": ["192.168.1.1", "10.10.10.10"]
        }
        ]
    }
    """
    try:
        if current_user.user_role == 'admin':
            group_names = None
        else:
            group_names = UserModel.get_user_groups(current_user.id)    
        if not group_names:
            raise PermissionError("Permission denied")
        ioc_data = await AgentDetailController.get_agent_ioc(request.agent_id, request.start_time, request.end_time)
        return AgentIoC(ioc_data=ioc_data)
    except UnauthorizedError:
        raise UnauthorizedError("Authentication required")
    except PermissionError:
        raise PermissionError("Permission denied")
    except Exception as e:
        raise InternalServerError()

@router.get("/agent_compliance", response_model=AgentCompliance)
async def get_agent_compliance(
    request: AgentComplianceRequest = Depends(),
    current_user: UserModel = Depends(AuthController.get_current_user),
):
    """
    Get the agent compliance data
    Request:
    curl -X 'GET' \
      'https://flask.aixsoar.com/api/agent_detail/agent_compliance?start_time=2024-10-10T00%3A00%3A00&end_time=2024-10-11T00%3A00%3A00' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer Token'
      -d '{"agent_id": "001"}'
    Response:
    {
        "compliance_data": {
        "compliance_name": ["CIS-1234", "CIS-1235"],
        "compliance_count": 2
        }
    }
    """
    try:
        if current_user.user_role == 'admin':
            group_names = None
        else:
            group_names = UserModel.get_user_groups(current_user.id)    
        if not group_names:
            raise PermissionError("Permission denied")
        compliance_data = await AgentDetailController.get_agent_compliance(request.agent_id, request.start_time, request.end_time)
        return AgentCompliance(compliance_data=compliance_data)
    except UnauthorizedError:
        raise UnauthorizedError("Authentication required")
    except PermissionError:
        raise PermissionError("Permission denied")
    except Exception as e:
        raise InternalServerError()