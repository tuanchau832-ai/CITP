"""Deterministic simulated device. Never produces environmental evidence.

--out emits hww.frames.v1 request JSONL. Replay fixtures wrap frames with
t_offset_ms instead; regenerate them with --fixtures.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import secrets
import random
import time
import urllib.request
import urllib.error

SCENARIOS=('demo-golden','tlh-loop','turbidity-spike','gradual-ph','sensor-fault','network-gap','do-drop','normal')
UNITS={'ph':'pH','do':'mg/L','turbidity':'NTU','temp':'degC'}
START=dt.datetime(2026,11,18,tzinfo=dt.timezone.utc)
def iso(value): return value.isoformat(timespec='milliseconds').replace('+00:00','Z')
def frame(seq, scenario='normal', start=START, clock='server'):
    seconds=seq*2
    vals={'ph':7.21,'do':6.4,'turbidity':18.4,'temp':27.25}
    raws={'ph':2109,'do':1310,'turbidity':555,'temp':None}
    readings={k:{'v':v,'u':UNITS[k],'q':'ok','raw':raws[k],'gen':'input'} for k,v in vals.items()}
    mode='manual'
    if scenario in ('turbidity-spike','demo-golden','tlh-loop') and 70<=seconds<130:
        mode='spike_turb';readings['turbidity'].update(v=180,raw=None,gen='profile')
    if scenario=='gradual-ph' and seconds<180:
        mode='gradual_ph';readings['ph'].update(v=round(7.2-1.8*min(seconds/120,1),2),raw=None,gen='profile')
    if scenario=='do-drop' and 70<=seconds<130:
        mode='do_drop';readings['do'].update(v=1.8,raw=None,gen='profile')
    if (scenario=='sensor-fault' and 70<=seconds<110) or (scenario=='demo-golden' and 150<=seconds<180):
        readings['turbidity'].update(v=None,raw=None,q='fault',fr='injected')
    return {'seq':seq,'measured_at':None if clock=='uptime' else iso(start+dt.timedelta(seconds=seconds)),
            'time_source':clock,'uptime_ms':seconds*1000,'buffered':False,'mode':mode,'readings':readings}
def envelope(frames,station,device,boot,sent_uptime=None,start=START,dropped=0):
    uptime=max(f['uptime_ms'] for f in frames) if sent_uptime is None else sent_uptime
    return {'schema':'hww.frames.v1','station_code':station,'device_code':device,'boot_id':boot,
            'fw_version':'0.4.0','sent_at':iso(start+dt.timedelta(milliseconds=uptime)),
            'sent_uptime_ms':uptime,'diag':{'buffer_depth':len(frames),'dropped_frames':dropped,'rejected_batches':0,'wifi_rssi':-42},'frames':frames}
def fixtures(directory):
    directory.mkdir(parents=True,exist_ok=True)
    for scenario in SCENARIOS[:6]:
        with (directory/(scenario+'.jsonl')).open('w',encoding='utf-8') as out:
            backlog=[]
            for seq in range(131 if scenario=='demo-golden' else 121):
                f=frame(seq,scenario)
                if (scenario=='network-gap' and 35<=seq<50) or (scenario=='demo-golden' and 100<=seq<115):
                    backlog.append(f);continue
                frames=[f]
                if backlog:
                    for old in backlog:old['buffered']=seq*2000-old['uptime_ms']>4000
                    frames+=backlog;backlog=[]
                out.write(json.dumps({'t_offset_ms':seq*2000,'frames':frames},separators=(',',':'))+'\n')
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scenario',default='normal',choices=SCENARIOS+('spike_turb','gradual_ph','do_drop'))
    p.add_argument('--base-url');p.add_argument('--key',default=os.getenv('HWW_DEVICE_KEY'))
    p.add_argument('--station',default='HWW-KNG-001');p.add_argument('--device',default='wokwi-esp32-01')
    p.add_argument('--frames',type=int,default=121);p.add_argument('--out',type=Path)
    p.add_argument('--recording',action='store_true',help='write --out as replay {t_offset_ms,frames}, instead of ingest envelopes')
    p.add_argument('--fault',action='append',default=[],metavar='CHANNEL[:START:END]',help='inject channel fault; seconds window optional, repeatable')
    p.add_argument('--outage',metavar='SECONDS|START:END',help='outage starting at 60 s for duration SECONDS, or explicit seconds window')
    p.add_argument('--fixtures',type=Path);p.add_argument('--interval',type=float,default=2)
    p.add_argument('--clock',choices=('server','ntp','uptime'),default='server')
    a=p.parse_args()
    if a.frames<1 or a.interval<0:p.error('--frames must be positive and --interval nonnegative')
    if a.fixtures:fixtures(a.fixtures);return
    if not a.out and not a.base_url:p.error('provide --out or --base-url')
    if a.base_url and not a.key:p.error('--key or HWW_DEVICE_KEY required')
    faults=[]
    try:
        for value in a.fault:
            parts=value.split(':');channel=parts[0]
            if channel not in UNITS:raise ValueError('unknown fault channel')
            begin,end=(0,float('inf')) if len(parts)==1 else map(float,parts[1:])
            if begin<0 or end<=begin:raise ValueError('invalid fault window')
            faults.append((channel,begin,end))
        outage=((60,60+float(a.outage)) if ':' not in a.outage else tuple(map(float,a.outage.split(':')))) if a.outage else None
        if outage and (len(outage)!=2 or outage[0]<0 or outage[1]<=outage[0]):raise ValueError('invalid outage window')
    except (ValueError,TypeError) as exc:p.error(str(exc))
    scenario={'spike_turb':'turbidity-spike','gradual_ph':'gradual-ph','do_drop':'do-drop'}.get(a.scenario,a.scenario)
    start=dt.datetime.now(dt.timezone.utc);boot=secrets.token_hex(4);pending=[];dropped=0;retry=1;batch_size=20
    output=a.out.open('w',encoding='utf-8') if a.out else None
    try:
        for seq in range(a.frames):
            pending.append(frame(seq,scenario,start,a.clock))
            for channel,begin,end in faults:
                if begin<=seq*2<end:pending[-1]['readings'][channel].update(v=None,raw=None,q='fault',fr='injected')
            if len(pending)>600:pending.pop(0);dropped+=1
            if ((scenario=='network-gap' and 35<=seq<50) or (scenario=='demo-golden' and 100<=seq<115)
                    or (outage and outage[0]<=seq*2<outage[1])):
                if a.base_url:time.sleep(a.interval)
                continue
            selected=[pending[-1]]+pending[:-1][:batch_size-1]
            for f in selected:f['buffered']=seq*2000-f['uptime_ms']>4000
            payload=envelope(selected,a.station,a.device,boot,seq*2000,start,dropped)
            payload['diag']['buffer_depth']=len(pending)
            if output:
                record={'t_offset_ms':seq*2000,'frames':selected} if a.recording else payload
                output.write(json.dumps(record,separators=(',',':'))+'\n')
                sent={f['seq'] for f in selected};pending=[f for f in pending if f['seq'] not in sent]
            if a.base_url:
                req=urllib.request.Request(a.base_url.rstrip('/')+'/api/v1/ingest/frames',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','X-Device-Key':a.key})
                delay=a.interval
                try:
                    with urllib.request.urlopen(req,timeout=8) as response:result=json.load(response)
                    ack={r['seq'] for r in result['results']};pending=[f for f in pending if f['seq'] not in ack]
                    delay=max(delay,result.get('next_min_interval_ms',2000)/1000);retry=1
                    print(json.dumps({'seq':seq,'station_status':result.get('station_status'),'queued':len(pending)}))
                except urllib.error.HTTPError as exc:
                    if exc.code in (401,403):delay=60
                    elif exc.code==409:pending=[f for f in pending if f['seq']!=seq];delay=10
                    elif exc.code==413:batch_size=max(1,batch_size//2)
                    elif exc.code==422:pending=[f for f in pending if f not in selected]
                    elif exc.code==429:delay=float(exc.headers.get('Retry-After','30'))
                    else:delay=retry*random.uniform(.8,1.2);retry=min(30,retry*2)
                    print(f'HTTP {exc.code}; {len(pending)} retained',flush=True)
                except OSError as exc:
                    delay=retry*random.uniform(.8,1.2);retry=min(30,retry*2);print(f'Network: {exc}; {len(pending)} retained',flush=True)
                time.sleep(delay)
    finally:
        if output:output.close()
if __name__=='__main__':main()
