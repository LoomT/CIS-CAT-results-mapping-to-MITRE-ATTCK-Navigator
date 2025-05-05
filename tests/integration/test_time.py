def test_time_returns_200(client):
    res = client.get("/api/time")
    assert res.status_code == 200
    assert "time" in res.json
    assert isinstance(res.json["time"], float)
