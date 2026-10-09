//! Temporary, opt-in diagnostic timing. Numeric metadata only; no page content.
use gtk::prelude::*;
use parking_lot::Mutex;
use serde::Serialize;
use std::{cell::Cell, fs::File, io::BufWriter, path::PathBuf, sync::LazyLock};

#[derive(Serialize)]
struct Entry {
    stage: &'static str,
    start_us: i64,
    end_us: i64,
    data: [i64; 8],
}
struct Capture {
    path: PathBuf,
    entries: Mutex<Vec<Entry>>,
}
static CAPTURE: LazyLock<Option<Capture>> = LazyLock::new(|| {
    std::env::var_os("KARERE_STAGE_TRACE").map(|path| Capture {
        path: path.into(),
        entries: Mutex::new(Vec::with_capacity(32768)),
    })
});

pub fn now() -> i64 {
    glib::monotonic_time()
}

pub fn record(stage: &'static str, start_us: i64, values: &[i64]) {
    let Some(capture) = CAPTURE.as_ref() else {
        return;
    };
    let end_us = now();
    let mut data = [0; 8];
    for (slot, value) in data.iter_mut().zip(values) {
        *slot = *value;
    }
    let mut entries = capture.entries.lock();
    if entries.len() < 500000 {
        entries.push(Entry {
            stage,
            start_us,
            end_us,
            data,
        });
    }
}

pub struct Span {
    stage: &'static str,
    start: i64,
    data: [i64; 8],
}
impl Span {
    pub fn new(stage: &'static str, values: &[i64]) -> Self {
        let mut data = [0; 8];
        for (slot, value) in data.iter_mut().zip(values) {
            *slot = *value;
        }
        Self {
            stage,
            start: now(),
            data,
        }
    }
}
impl Drop for Span {
    fn drop(&mut self) {
        record(self.stage, self.start, &self.data);
    }
}

pub fn observe_clock(widget: &impl IsA<gtk::Widget>) {
    if CAPTURE.is_none() {
        return;
    }
    if let Some(clock) = widget.frame_clock() {
        let last = Cell::new(clock.history_start() - 1);
        clock.connect_after_paint(move |clock| {
            for frame in (last.get() + 1).max(clock.history_start())..=clock.frame_counter() {
                let Some(t) = clock.timings(frame) else {
                    continue;
                };
                if !t.is_complete() {
                    break;
                }
                record(
                    "presentation",
                    t.frame_time(),
                    &[
                        frame,
                        t.presentation_time(),
                        t.predicted_presentation_time(),
                        t.refresh_interval(),
                    ],
                );
                last.set(frame);
            }
        });
    }
}

pub fn flush() {
    let Some(capture) = CAPTURE.as_ref() else {
        return;
    };
    match File::create(&capture.path) {
        Ok(file) => {
            let entries = std::mem::take(&mut *capture.entries.lock());
            if let Err(error) = serde_json::to_writer(BufWriter::new(file), &entries) {
                eprintln!("stage probe write failed: {error}");
            }
        }
        Err(error) => eprintln!("stage probe open failed: {error}"),
    }
}
