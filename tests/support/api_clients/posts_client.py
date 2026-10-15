from qa_framework.api import BaseApiClient


class PostsClient:
    def __init__(self, base_url: str, session, timeout: float) -> None:
        self.client = BaseApiClient(
            base_url, session=session, timeout=timeout, retry_count=0, request_budget=1
        )

    def get_post(self, post_id: int):
        return self.client.get(f"/posts/{post_id}")
