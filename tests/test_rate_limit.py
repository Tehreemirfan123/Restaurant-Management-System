from core.rate_limit import limiter


def test_login_is_rate_limited(client):
    # The limiter is disabled for the suite; turn it on just for this test.
    limiter.enabled = True
    limiter.reset()
    try:
        codes = [
            client.post(
                "/auth/login",
                data={"username": "nobody", "password": "wrong"},
            ).status_code
            for _ in range(12)
        ]
    finally:
        limiter.enabled = False
        limiter.reset()

    # Wrong credentials are 401; once the 10/minute cap trips we get 429.
    assert 429 in codes
    assert codes.count(429) >= 1
