#!/usr/bin/env python3
import argparse,json,subprocess,time
from pathlib import Path
from conversation_probe import connect

ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument('prefix');p.add_argument('--mode',default='programmatic',choices=['programmatic','wheel']);args=p.parse_args()
    c=connect()
    c.evaluate((ROOT/'wallpaper_probe.js').read_text())
    try:
        for enabled,suffix in [(False,'original_1'),(True,'layer_1'),(True,'layer_2'),(False,'original_2')]:
            actual=c.evaluate('window.__karereWallpaperProbe.set('+str(enabled).lower()+')')
            time.sleep(3)
            print(json.dumps({'condition':actual,'sample':suffix}),flush=True)
            subprocess.run(['python3',str(ROOT/'conversation_probe.py'),args.prefix+'_'+suffix,
                            '--anchor-bottom','3452.5','--mode',args.mode],check=True)
    finally:
        c.evaluate('window.__karereWallpaperProbe.set(false)')
        c.close()

if __name__=='__main__':main()
