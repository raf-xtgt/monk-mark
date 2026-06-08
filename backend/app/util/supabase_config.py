import os
import httpx
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# We override the default httpx client factory so that whenever 
# Postgrest or GoTrue tries to instantiate a network engine, 
# it explicitly uses HTTP/1.1 with completely isolated connection pooling.
def create_isolated_http_client(*args, **kwargs):
    kwargs["http2"] = False
    # pool_limits with 0 means connections are never kept alive/reused in a broken pool
    kwargs["limits"] = httpx.Limits(max_keepalive_connections=0, max_connections=100)
    kwargs["timeout"] = httpx.Timeout(30.0, connect=10.0)
    return httpx.Client(*args, **kwargs)

def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_PROJECT_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    if not url or not key:
        raise ValueError("Supabase credentials missing in .env")
        
    client = create_client(url, key)
    # Force patch the synchronous engine
    client.postgrest.session = create_isolated_http_client()
    return client

def get_supabase_admin_client() -> Client:
    url = os.environ.get("SUPABASE_PROJECT_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not service_key:
        raise ValueError("Supabase service role credentials missing in .env")
        
    client = create_client(url, service_key)
    # Force patch the synchronous engine
    client.postgrest.session = create_isolated_http_client()
    return client

# Initialize singleton instances
supabase = get_supabase_client()
supabase_admin = get_supabase_admin_client()