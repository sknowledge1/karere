#!/usr/bin/env python3
"""Reopen the previously selected row and settle loaded history, without reading it."""
import json,time
from conversation_probe import connect

def main():
    c=connect()
    try:
        if not c.evaluate("!!document.querySelector('#main')"):
            point=c.evaluate("(()=>{let e=[...document.querySelectorAll('#pane-side [role=row]')][4];if(!e)return null;let r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()")
            if not point:raise RuntimeError('Original chat row position unavailable')
            for event in ['mousePressed','mouseReleased']:
                c.call('Input.dispatchMouseEvent',dict(type=event,button='left',clickCount=1,**point))
        time.sleep(3)
        c.evaluate("window.__karerePane=[...document.querySelectorAll('#main *')].find(e=>e.clientHeight>100&&e.scrollHeight>e.clientHeight+300&&/auto|scroll/.test(getComputedStyle(e).overflowY));!!window.__karerePane")
        for _ in range(4):
            state=c.evaluate("(()=>{let e=window.__karerePane;return{height:e.clientHeight,scroll_height:e.scrollHeight,top:e.scrollTop}})()")
            if state['scroll_height']-state['height']>=4852.5:break
            c.evaluate("window.__karerePane.scrollTo({top:0,behavior:'instant'});true")
            time.sleep(5)
        else:raise RuntimeError('Could not load matching history range')
        c.evaluate("window.__karerePane.scrollTo({top:window.__karerePane.scrollHeight-window.__karerePane.clientHeight-3452.5,behavior:'instant'});true")
        time.sleep(3)
        print(json.dumps(c.evaluate("(()=>{let e=window.__karerePane;return{height:e.clientHeight,scroll_height:e.scrollHeight,top:e.scrollTop,images:document.querySelector('#main').querySelectorAll('img').length}})()")))
    finally:c.close()

if __name__=='__main__':main()
