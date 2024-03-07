import re

BASE_URL_RE = re.compile(
    """https:\/\/[a-zA-Z0-9]{4,8}-adaptive\.akamaized.net\/exp=[0-9]{10}~acl=%2F[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}%2F%2A~hmac=[0-9a-fA-F]{64}\/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"""
)
PRE_SCRIPT_URL_RE = re.compile(
    """https:\/\/siteassets.parastorage.com\/pages\/pages\/thunderbolt\?((([^=]+)\=([^& \n"]+)))*"""
)
MASTER_URL_RE = re.compile(
    """https:\/\/[a-zA-Z0-9]{4,8}-adaptive\.akamaized.net\/[^& \n\"]+\/master\.json"""
)
VIMEO_URL_RE = re.compile("""https:\/\/vimeo\.com\/[0-9]*""")
VIDEO_PAGE_RE = re.compile(
    """https:\/\/www\.alevelphysicsonline\.com\/aqa-3-[0-9]{1,2}"""
)
