import os
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import create_app

def batch(seq=0, value=7.2, at=None, **reading):
    return {'schema':'hww.frames.v1','station_code':'HWW-KNG-001','device_code':'wokwi-esp32-01','boot_id':'abcdef01','fw_version':'0.4.0','sent_at':None,'sent_uptime_ms':max(100000, seq*2000),'diag':{},'frames':[{'seq':seq,'measured_at':(at or datetime.now(timezone.utc)).isoformat().replace('+00:00','Z'),'time_source':'ntp','uptime_ms':seq*2000,'buffered':False,'mode':'manual','readings':{'ph':{'v':value,'u':'pH','q':'ok','raw':2109,'gen':'input',**reading}}}]}

@pytest.fixture
def client(tmp_path):
    app=create_app('sqlite:///'+str(tmp_path/'test.db'), testing=True)
    with TestClient(app,base_url='https://testserver') as c:
        app.state.service.rotate_key('wokwi-esp32-01', 'hwwk_test_device_secret')
        yield c

def ingest(c,b): return c.post('/api/v1/ingest/frames',json=b,headers={'X-Device-Key':'hwwk_test_device_secret'})
def state(c): return c.get('/api/v1/stations/HWW-KNG-001/state').json()

def test_idempotent_and_monotonic(client):
    now=datetime.now(timezone.utc)
    assert ingest(client,batch(10,7.2,now)).json()['accepted']==1
    version=state(client)['version']
    assert ingest(client,batch(10,7.2,now)).json()['duplicates']==1
    assert state(client)['version']==version
    assert ingest(client,batch(9,8.0,now-timedelta(seconds=2))).status_code==200
    assert state(client)['sensors'][0]['value']==7.2

def test_strict_provenance_unit_and_auth(client):
    b=batch(); b['source']='field_observation'
    assert ingest(client,b).status_code==422
    b=batch(); b['frames'][0]['readings']['ph']['u']='NTU'
    assert ingest(client,b).json()['code']=='unit_mismatch'
    assert client.post('/api/v1/ingest/frames',json=batch()).status_code==401
    assert state(client)['version']==0

def test_persistence_fault_clear_and_review_guard(client):
    now=datetime.now(timezone.utc)-timedelta(seconds=20)
    for i in range(3): assert ingest(client,batch(i,5.4,now+timedelta(seconds=i*2))).status_code==200
    alerts=client.get('/api/v1/alerts').json()['items']
    assert len(alerts)==1 and alerts[0]['rule_code']=='REF_PH_BAND'
    assert alerts[0]['evidence_class']=='simulated_anomaly'
    assert state(client)['sensors'][0]['status']=='abnormal'
    assert ingest(client,batch(3,None,now+timedelta(seconds=6),q='fault',fr='injected')).status_code==200
    sensor=state(client)['sensors'][0]
    assert sensor['value'] is None and sensor['last_valid']['value']==5.4
    assert client.post('/api/v1/alerts/1/acknowledge',json={},headers={'X-Requested-With':'hww'}).status_code==401
    svc=client.app.state.service
    svc.create_user('reviewer','secret-password','reviewer')
    assert client.post('/api/v1/auth/login',json={'username':'reviewer','password':'secret-password'},headers={'X-Requested-With':'hww'}).status_code==200
    review=client.post('/api/v1/incident-reviews',json={'alert_ids':[1],'note':'Demo'},headers={'X-Requested-With':'hww'})
    assert review.status_code==201
    result=client.post('/api/v1/incident-reviews/'+str(review.json()['id'])+'/submit',json={'outcome':'verified_incident','lab_reference':'fake'},headers={'X-Requested-With':'hww'})
    assert result.status_code==422

def test_offline_nulls_and_recovery(client):
    ingest(client,batch())
    client.app.state.service.freshness(datetime.now(timezone.utc)+timedelta(seconds=16))
    assert state(client)['station_status']=='offline'
    assert state(client)['sensors'][0]['value'] is None
    ingest(client,batch(1))
    assert state(client)['station_status']!='offline'

def test_backfill_cannot_replace_current_status(client):
    now=datetime.now(timezone.utc)
    ingest(client,batch(20,7.2,now))
    ingest(client,batch(1,None,now-timedelta(seconds=20),q='fault',fr='injected'))
    assert state(client)['sensors'][0]['status']=='normal'

def test_baseline_frozen_and_clear(client):
    from app.schemas import Batch
    from app.service import stamp
    svc=client.app.state.service;device=svc.authenticate('hwwk_test_device_secret');start=datetime.now(timezone.utc)-timedelta(seconds=200)
    def send(seq,value):
        b=batch(seq,7.2,start+timedelta(seconds=seq*2));b['sent_uptime_ms']=1000000;b['frames'][0]['readings']={'turbidity':{'v':value,'u':'NTU','q':'ok','raw':555,'gen':'input'}}
        return svc.ingest(Batch.model_validate(b),device,received=start+timedelta(seconds=seq*2))
    for i in range(36):send(i,18.4)
    send(36,142.5);send(37,142.5)
    alerts=client.get('/api/v1/alerts?rule=CHG_TURB_SPIKE').json()['items'];assert len(alerts)==1
    a=client.get('/api/v1/alerts/'+str(alerts[0]['id'])).json();assert a['baseline_value']==pytest.approx(18.4);assert a['threshold_value']==pytest.approx(68.4)
    for i in range(38,90):send(i,142.5)
    assert client.get('/api/v1/alerts/'+str(a['id'])).json()['cleared_at'] is None
    for i in range(90,95):send(i,18.4)
    assert client.get('/api/v1/alerts/'+str(a['id'])).json()['cleared_at'] is not None

def test_review_close_notes_csrf_and_roles(client):
    now=datetime.now(timezone.utc)-timedelta(seconds=10)
    for i in range(3):ingest(client,batch(i,5.4,now+timedelta(seconds=2*i)))
    svc=client.app.state.service;svc.create_user('op','operator-password','operator');svc.create_user('rev','reviewer-password','reviewer');headers={'X-Requested-With':'hww'}
    assert client.post('/api/v1/auth/login',json={'username':'op','password':'operator-password'}).status_code==403
    client.post('/api/v1/auth/login',json={'username':'op','password':'operator-password'},headers=headers)
    assert client.post('/api/v1/incident-reviews',json={'alert_ids':[1]},headers=headers).status_code==403
    assert client.post('/api/v1/alerts/1/notes',json={'text':'Private operator note'},headers=headers).status_code==201
    assert client.post('/api/v1/auth/logout',json={},headers=headers).status_code==204
    detail=client.get('/api/v1/alerts/1').json();assert 'Private operator note' not in str(detail) and '"actor"' not in str(detail)
    client.post('/api/v1/auth/login',json={'username':'rev','password':'reviewer-password'},headers=headers)
    r=client.post('/api/v1/incident-reviews',json={'alert_ids':[1]},headers=headers).json()
    result=client.post('/api/v1/incident-reviews/'+str(r['id'])+'/submit',json={'outcome':'confirmed_simulated_anomaly'},headers=headers)
    assert result.status_code==200 and result.json()['alerts'][0]['review_status']=='closed'
    assert result.json()['alerts'][0]['is_preliminary'] is False

def test_batch_validation_atomic_and_temperature_fault(client):
    b=batch();b['frames'].append(batch(1)['frames'][0]);b['frames'][1]['readings']['ph']['u']='bad'
    assert ingest(client,b).status_code==422 and state(client)['version']==0
    b=batch();b['frames'][0]['readings']={'temp':{'v':100.,'u':'degC','q':'ok','raw':None,'gen':'input'}}
    assert ingest(client,b).status_code==200
    alerts=client.get('/api/v1/alerts').json()['items'];assert [a['rule_code'] for a in alerts]==['VALID_RANGE']
    assert state(client)['sensors'][3]['status']=='sensor_fault'

def test_replay_catalog_start_stop_and_takeover(client):
    svc=client.app.state.service;svc.create_user('op','operator-password','operator');h={'X-Requested-With':'hww'}
    client.post('/api/v1/auth/login',json={'username':'op','password':'operator-password'},headers=h)
    ingest(client,batch())
    assert client.post('/api/v1/replays/demo-golden/runs',json={'station_code':'HWW-KNG-001','takeover':False},headers=h).status_code==409
    r=client.post('/api/v1/replays/demo-golden/runs',json={'station_code':'HWW-KNG-001','speed':5,'takeover':True},headers=h)
    assert r.status_code==202
    assert ingest(client,batch(1)).status_code==409
    assert client.get('/api/v1/stations/HWW-KNG-001/link').json()['link_status']=='replay'
    stopped=client.post('/api/v1/replay-runs/'+r.json()['session_id']+'/stop',json={},headers=h)
    assert stopped.status_code==200 and stopped.json()['end_reason']=='replay_stopped'

def test_fixture_speed_same_alerts_and_do_drop(tmp_path):
    import json
    from app.service import Service,ROOT
    from app.schemas import Batch
    from app.models import Alert
    from sqlalchemy import select
    found=[]
    for speed in (1,5):
        svc=Service('sqlite:///'+str(tmp_path/('speed'+str(speed)+'.db')),True);svc.seed();svc.rotate_key('wokwi-esp32-01','hwwk_fixture');device=svc.authenticate('hwwk_fixture');start=datetime.now(timezone.utc)
        lines=[json.loads(x) for x in (ROOT/'shared/fixtures/replays/demo-golden.jsonl').read_text().splitlines()]
        for line in lines:
            frames=line['frames'];received=start+timedelta(milliseconds=line['t_offset_ms']/speed)
            for f in frames:f['measured_at']=(start+timedelta(milliseconds=f['uptime_ms']/speed)).isoformat().replace('+00:00','Z')
            b=batch();b['frames']=frames;b['sent_uptime_ms']=max(f['uptime_ms'] for f in frames);svc.ingest(Batch.model_validate(b),device,received,speed)
        with svc.DB() as db:found.append(sorted(a.rule_code for a in db.scalars(select(Alert))))
    assert found[0]==found[1] and 'CHG_TURB_SPIKE' in found[0] and 'VALID_RANGE' in found[0]

def test_do_drop_fault_suppression_and_clear(client):
    from app.schemas import Batch
    svc=client.app.state.service;device=svc.authenticate('hwwk_test_device_secret');start=datetime.now(timezone.utc)-timedelta(seconds=120)
    def send(seq,value,q='ok'):
        b=batch(seq,7.2,start+timedelta(seconds=seq*2));b['sent_uptime_ms']=1000000;r={'v':value,'u':'mg/L','q':q,'raw':1310 if q=='ok' else None,'gen':'input'}
        if q=='fault':r['fr']='injected'
        b['frames'][0]['readings']={'do':r};svc.ingest(Batch.model_validate(b),device,start+timedelta(seconds=seq*2))
    for i in range(36):send(i,6.4)
    send(36,None,'fault')
    assert not client.get('/api/v1/alerts?rule=CHG_DO_DROP').json()['items']
    send(37,1.8);send(38,1.8)
    assert not client.get('/api/v1/alerts?rule=CHG_DO_DROP').json()['items']
    send(39,1.8)
    a=client.get('/api/v1/alerts?rule=CHG_DO_DROP').json()['items'][0]
    for i in range(40,45):send(i,6.4)
    assert client.get('/api/v1/alerts/'+str(a['id'])).json()['cleared_at'] is not None

def test_database_persistence_restart(tmp_path):
    from app.service import Service
    from app.schemas import Batch
    path='sqlite:///'+str(tmp_path/'restart.db');svc=Service(path,True);svc.seed();svc.rotate_key('wokwi-esp32-01','hwwk_restart');device=svc.authenticate('hwwk_restart');start=datetime.now(timezone.utc)-timedelta(seconds=10)
    svc.ingest(Batch.model_validate(batch(0,5.4,start)),device);svc.ingest(Batch.model_validate(batch(1,5.4,start+timedelta(seconds=2))),device);svc.engine.dispose()
    svc=Service(path,True);svc.seed();device=svc.authenticate('hwwk_restart');svc.ingest(Batch.model_validate(batch(2,5.4,start+timedelta(seconds=4))),device)
    assert svc.snapshot('HWW-KNG-001')['sensors'][0]['status']=='abnormal'

def test_scaled_replay_freshness_and_staff_reads(client):
    from app.schemas import Batch
    svc=client.app.state.service
    with svc.DB() as db:
        from app.models import Device
        device=db.get(Device,'replay-hww-kng-001')
    b=batch();b['device_code']=device.code;start=datetime.now(timezone.utc)
    svc.ingest(Batch.model_validate(b),device,start,speed=5)
    svc.freshness(start+timedelta(seconds=3.5))
    assert state(client)['station_status']=='offline'
    assert client.get('/api/v1/replays').status_code==401

def test_old_boot_duplicate_cannot_supersede_current_session(client):
    start=datetime.now(timezone.utc)-timedelta(seconds=12)
    original=batch(0,7.2,start);assert ingest(client,original).status_code==200
    for i in range(3):
        current_batch=batch(i,5.4,start+timedelta(seconds=2+i*2));current_batch['boot_id']='bbbbbbbb';assert ingest(client,current_batch).status_code==200
    before=state(client);assert before['sensors'][0]['status']=='abnormal'
    assert ingest(client,original).json()['duplicates']==1
    after=state(client)
    for key in ('session','version','sensors','open_alerts'):assert after[key]==before[key]

def test_rejected_only_batch_does_not_claim_station(client):
    from app.models import Device,Station,Session
    from app.schemas import Batch
    from sqlalchemy import select
    svc=client.app.state.service
    for at in (datetime.now(timezone.utc)-timedelta(days=2),datetime.now(timezone.utc)+timedelta(minutes=6)):
        ack=ingest(client,batch(0,7.2,at)).json();assert ack['accepted']==0 and ack['rejected']==1
        with svc.DB() as db:
            assert db.get(Station,'HWW-KNG-001').active_device is None
            assert not list(db.scalars(select(Session)))
    with svc.DB.begin() as db:db.add(Device(code='script-other',station='HWW-KNG-001',kind='sim_script',enabled=True))
    svc.rotate_key('script-other','hwwk_other_device')
    b=batch();b['device_code']='script-other'
    assert svc.ingest(Batch.model_validate(b),svc.authenticate('hwwk_other_device'))['accepted']==1

def test_legacy_empty_session_expires(client):
    from app.models import Session,Station
    from app.service import stamp
    import uuid
    svc=client.app.state.service;sid=str(uuid.uuid4());start=datetime.now(timezone.utc)-timedelta(seconds=61)
    with svc.DB.begin() as db:
        db.add(Session(id=sid,station='HWW-KNG-001',device='wokwi-esp32-01',boot_id='aaaaaaaa',source='simulated_wokwi',started_at=stamp(start),speed=1))
        st=db.get(Station,'HWW-KNG-001');st.active_device='wokwi-esp32-01';st.current_session=sid
    svc.freshness()
    with svc.DB() as db:
        assert db.get(Session,sid).end_reason=='idle_timeout'
        assert db.get(Station,'HWW-KNG-001').active_device is None

def test_snapshot_etag_changes_for_staff_lifecycle(client):
    start=datetime.now(timezone.utc)-timedelta(seconds=10)
    for i in range(3):ingest(client,batch(i,5.4,start+timedelta(seconds=i*2)))
    svc=client.app.state.service;svc.create_user('rev','reviewer-password','reviewer');h={'X-Requested-With':'hww'};client.post('/api/v1/auth/login',json={'username':'rev','password':'reviewer-password'},headers=h)
    url='/api/v1/stations/HWW-KNG-001/state'
    before=client.get(url)
    assert client.post('/api/v1/alerts/1/acknowledge',json={},headers=h).status_code==200
    acknowledged=client.get(url,headers={'If-None-Match':before.headers['etag']});assert acknowledged.status_code==200
    assert acknowledged.json()['version']>before.json()['version']
    r=client.post('/api/v1/incident-reviews',json={'alert_ids':[1]},headers=h);assert r.status_code==201
    reviewed=client.get(url,headers={'If-None-Match':acknowledged.headers['etag']});assert reviewed.status_code==200
    assert client.post('/api/v1/incident-reviews/'+str(r.json()['id'])+'/submit',json={'outcome':'confirmed_simulated_anomaly'},headers=h).status_code==200
    closed=client.get(url,headers={'If-None-Match':reviewed.headers['etag']});assert closed.status_code==200 and closed.json()['open_alert_count']==0

def test_session_end_invalidates_snapshot_etag(client):
    ingest(client,batch());url='/api/v1/stations/HWW-KNG-001/state';client.app.state.service.freshness(datetime.now(timezone.utc)+timedelta(seconds=16));before=client.get(url)
    client.app.state.service.freshness(datetime.now(timezone.utc)+timedelta(seconds=61))
    ended=client.get(url,headers={'If-None-Match':before.headers['etag']});assert ended.status_code==200 and ended.json()['session']['ended_at']

def test_historical_fault_clears_only_at_real_valid_evidence(client):
    start=datetime.now(timezone.utc)-timedelta(seconds=20)
    for frame in (
        batch(100,7.2,start+timedelta(seconds=16)),
        batch(101,7.2,start+timedelta(seconds=18)),
        batch(1,None,start,q='fault',fr='injected'),
        batch(2,None,start+timedelta(seconds=2),q='fault',fr='injected'),
    ):
        assert ingest(client,frame).json()['accepted']==1
    alerts=client.get('/api/v1/alerts?rule=VALID_RANGE').json()['items'];assert len(alerts)==1
    assert alerts[0]['detected_late'] is True
    assert alerts[0]['cleared_at']==(start+timedelta(seconds=18)).isoformat(timespec='milliseconds').replace('+00:00','Z')
    assert state(client)['sensors'][0]['status']=='normal'

def test_replay_concurrent_takeover_stop_and_reset_join_writers(client):
    import concurrent.futures,time
    from app.models import Session,FrameRow,Measurement
    from sqlalchemy import select,func
    svc=client.app.state.service;svc.create_user('admin','admin-password','admin');h={'X-Requested-With':'hww'};client.post('/api/v1/auth/login',json={'username':'admin','password':'admin-password'},headers=h)
    def start():return client.post('/api/v1/replays/demo-golden/runs',json={'station_code':'HWW-KNG-001','speed':5,'takeover':True},headers=h)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:start(),range(2)))
    assert all(r.status_code==202 for r in results)
    with svc.DB() as db:
        opened=list(db.scalars(select(Session).where(Session.ended_at.is_(None),Session.station=='HWW-KNG-001')));assert len(opened)==1;sid=opened[0].id
    assert client.post('/api/v1/replay-runs/'+sid+'/stop',json={},headers=h).status_code==200
    before=state(client);time.sleep(.5);assert state(client)['version']==before['version']
    assert start().status_code==202
    assert client.post('/api/v1/admin/demo-reset',json={'confirm':'RESET'},headers=h).status_code==202
    time.sleep(.5)
    with svc.DB() as db:
        assert db.scalar(select(func.count()).select_from(FrameRow))==0
        assert db.scalar(select(func.count()).select_from(Measurement))==0
