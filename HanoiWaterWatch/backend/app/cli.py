import argparse,json,os
from .service import Service

def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True);sub.add_parser('seed');devices=sub.add_parser('devices').add_subparsers(dest='action',required=True);rotate=devices.add_parser('rotate-key');rotate.add_argument('device_code');args=parser.parse_args();svc=Service(os.getenv('DATABASE_URL','sqlite:///./waterwatch.db'));svc.seed()
    if args.command=='devices':print(json.dumps(svc.rotate_key(args.device_code)))
    else:print('Registry, rules and configured demo users seeded; existing passwords and rule edits preserved.')
if __name__=='__main__':main()
