from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BOBSERVER_",
        case_sensitive=False,
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    admin_username: str = "admin"
    admin_password: str = "nowibm"
    bob_mcp_config: str = ".bob/mcp.json"   # path to the .bob/mcp.json seeded into each run
    appid_client_id: str = ""
    appid_client_secret: str = ""
    appid_discovery_endpoint: str = ""
    appid_redirect_uri: str = ""
    appid_session_secret: str = "change-this-in-production"
    appid_session_https_only: bool = True
    bob_command: str = "bob"
    bob_max_coins: int = 30
    executor_command: str = "/app/scripts/run-pipeline.sh"
    executor_timeout_seconds: int = 900
    oauth_access_token_ttl_seconds: int = 3600
    salesforce_case_watch_db_path: str = "/workspace/bobserver_state.db"
    salesforce_case_watch_enabled: bool = False
    salesforce_case_watch_interval_seconds: int = 60
    salesforce_case_watch_limit: int = 10
    salesforce_case_watch_query: str = "IsClosed = false AND Priority = 'Critical'"
    salesforce_case_watch_script: str = "/app/scripts/salesforce-cases.py"
    slack_auto_intervene_cooldown_seconds: int = 300
    slack_auto_intervene_enabled: bool = False
    slack_auto_intervene_keywords: str = (
        "don't know what is the problem,dont know what is the problem,what is the problem,"
        "not sure what is wrong,instana reports,5xx,error rate,latency,agentforce failing,agentforce is failing"
    )
    slack_bot_token: str = ""
    slack_context_cache_limit: int = 20
    slack_history_limit: int = 5
    slack_signing_secret: str = ""
    slack_warroom_users: str = ""
    workspace_root: str = "/workspace"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
