"""Locust load test for the deployed API.

Run against the Azure deployment:
    locust -f tests/load/locustfile.py --host https://<container_app_fqdn>

Or headless, e.g. 50 users ramping at 5/s for 2 minutes:
    locust -f tests/load/locustfile.py --host https://<container_app_fqdn> \
        --headless -u 50 -r 5 -t 2m
"""

from locust import HttpUser, between, task


class ApiUser(HttpUser):
    """Simulates a client hitting the app's public endpoints."""

    wait_time = between(1, 3)

    @task(3)
    def about(self) -> None:
        self.client.get("/api/v1/about", name="/api/v1/about")

    @task(2)
    def health_live(self) -> None:
        self.client.get("/api/v1/health/live", name="/api/v1/health/live")

    @task(1)
    def health_ready(self) -> None:
        # Exercises the Redis dependency, unlike the other two endpoints.
        self.client.get("/api/v1/health/ready", name="/api/v1/health/ready")
