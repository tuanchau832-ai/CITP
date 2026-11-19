"""Exercise the local demo API using credentials from ignored .env.local.

Run only against the developer-created local demo database: this starts and
stops a replay and creates simulated alerts for review.
"""
import http.cookiejar
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://127.0.0.1:8000/api/v1'


def main():
    config = dict(line.split('=', 1) for line in (ROOT / '.env.local').read_text().splitlines() if '=' in line)
    cookies = http.cookiejar.CookieJar()
    client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))

    def call(path, body=None):
        req = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body is not None else None,
                                     headers={'Content-Type': 'application/json', 'X-Requested-With': 'hww'})
        with client.open(req, timeout=15) as response:
            return json.load(response) if response.status != 204 else None

    user = call('/auth/login', {'username': config['DEMO_REVIEWER_USERNAME'], 'password': config['DEMO_REVIEWER_PASSWORD']})
    assert user['user']['role'] == 'reviewer'
    recordings = call('/replays')['items']
    assert any(item['name'] == 'demo-golden' for item in recordings)
    run = call('/replays/demo-golden/runs', {'station_code': 'HWW-KNG-001', 'speed': 5, 'takeover': True, 'loop': False})
    seen = set()
    deadline = time.monotonic() + 70
    try:
        while time.monotonic() < deadline:
            state = call('/stations/HWW-KNG-001/state')
            sensor = next(s for s in state['sensors'] if s['channel'] == 'turbidity')
            seen.add(sensor['status'])
            if sensor['status'] in ('sensor_fault', 'offline', 'unavailable'):
                assert sensor['value'] is None
            alerts = call('/alerts?station=HWW-KNG-001')['items']
            if {'normal', 'abnormal', 'sensor_fault', 'offline'}.issubset(seen) and state['station_status'] != 'offline':
                assert any(a['rule_code'] == 'CHG_TURB_SPIKE' for a in alerts)
                assert any(a['rule_code'] == 'VALID_RANGE' for a in alerts)
                assert any(a['rule_code'] == 'STN_OFFLINE' for a in alerts)
                print('PASS: golden replay produced normal, spike, sensor fault, offline and recovery')
                break
            time.sleep(0.5)
        else:
            raise AssertionError('Golden replay did not reproduce every documented state: ' + str(sorted(seen)))
        target = next(a for a in alerts if a['rule_code'] == 'CHG_TURB_SPIKE' and a['review_status'] == 'open')
        call('/alerts/' + str(target['id']) + '/acknowledge', {'note': 'Local automated demo check'})
        review = call('/incident-reviews', {'alert_ids': [target['id']], 'note': 'Local simulated-data review'})
        result = call('/incident-reviews/' + str(review['id']) + '/submit', {'outcome': 'confirmed_simulated_anomaly', 'note': 'Expected deterministic replay'})
        assert result['status'] == 'submitted'
        alert = call('/alerts/' + str(target['id']))
        assert alert['review_status'] == 'closed'
        call('/auth/logout', {})
        public = call('/alerts/' + str(target['id']))
        assert 'Local automated demo check' not in json.dumps(public)
        assert 'Expected deterministic replay' not in json.dumps(public)
        print('PASS: acknowledge, review, close and anonymous note redaction')
    finally:
        try:
            call('/auth/login', {'username': config['DEMO_REVIEWER_USERNAME'], 'password': config['DEMO_REVIEWER_PASSWORD']})
            call('/replay-runs/' + run['session_id'] + '/stop', {})
        except urllib.error.HTTPError as error:
            if error.code != 404:
                raise


if __name__ == '__main__':
    main()
