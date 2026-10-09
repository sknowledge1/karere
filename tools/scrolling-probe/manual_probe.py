#!/usr/bin/env python3
"""Start/finish an observation-only physical-input capture."""
import argparse,json,time
from pathlib import Path
from conversation_probe import connect

ROOT=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['start','finish']);p.add_argument('label');args=p.parse_args()
    c=connect()
    try:
        if args.command=='start':
            c.evaluate((ROOT/'conversation_probe.js').read_text())
            geometry=c.evaluate("window.__karereConversationProbe.start({mode:'observe',warmup:0,duration:600000})")
            (ROOT/'results'/f'{args.label}_manual_start.json').write_text(json.dumps({'wall':time.time(),'monotonic':time.monotonic(),'geometry':geometry}))
            print(json.dumps({'armed':args.label,'geometry':geometry}))
        else:
            c.evaluate('window.__karereConversationProbe.cancel();true')
            report=c.evaluate('window.__karereConversationProbe.result')
            (ROOT/'results'/f'{args.label}_page.json').write_text(json.dumps(report))
            print(json.dumps({'finished':args.label,'wheel_events':len(report['wheels']),'frames':report['observed_frames']}))
    finally:c.close()
if __name__=='__main__':main()
