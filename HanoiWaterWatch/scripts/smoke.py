"""Read-only smoke checks for a running deployment; no external packages needed."""
import argparse
import json
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    args = parser.parse_args()
    base = args.base_url.rstrip('/')
    def get(path):
        with urllib.request.urlopen(base + path, timeout=10) as response:
            assert response.status == 200
            return json.load(response)
    health = get('/api/v1/health')
    assert health['db'] == 'ok', health
    stations = get('/api/v1/stations')
    assert len(stations['items']) == 3
    assert stations['is_simulated'] is True
    for station in stations['items']:
        state = get('/api/v1/stations/' + station['code'] + '/state')
        assert state['is_simulated'] is True
        assert len(state['sensors']) == 4
        for sensor in state['sensors']:
            if sensor['status'] in ('sensor_fault', 'offline', 'unavailable'):
                assert sensor['value'] is None
        if station['data_mode'] == 'planned':
            assert state['station_status'] == 'unavailable'
    for route in ('/', '/simulation', '/alerts', '/stations/HWW-KNG-001/model'):
        with urllib.request.urlopen(base + route, timeout=10) as response:
            assert 'text/html' in response.headers['Content-Type']
            assert '<div id="root"' in response.read().decode()
    print('PASS: API health, three stations, provenance, null masking and SPA route serving')


if __name__ == '__main__':
    main()

