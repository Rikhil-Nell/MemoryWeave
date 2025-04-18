from supabase import create_client
from supabase.lib.client_options import SyncClientOptions
from app.core.config import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY, SyncClientOptions(
    auto_refresh_token=False, persist_session=False))
