use criterion::{black_box, criterion_group, criterion_main, Criterion};
use chronos::ChronosEngine;

fn bench_measure(c: &mut Criterion) {
    let mut engine = ChronosEngine::new_native();
    
    c.bench_function("measure", |b| {
        b.iter(|| {
            black_box(engine.measure_native());
        });
    });
}

fn bench_analyze(c: &mut Criterion) {
    let mut engine = ChronosEngine::new_native();
    
    // Pre-populate with samples
    for _ in 0..1000 {
        engine.measure_native();
    }
    
    c.bench_function("analyze", |b| {
        b.iter(|| {
            black_box(engine.analyze_native());
        });
    });
}

fn bench_full_workflow(c: &mut Criterion) {
    c.bench_function("full_workflow", |b| {
        b.iter(|| {
            let mut engine = ChronosEngine::new_native();
            for _ in 0..100 {
                engine.measure_native();
            }
            black_box(engine.analyze_native());
        });
    });
}

fn bench_sample_count(c: &mut Criterion) {
    let mut engine = ChronosEngine::new_native();
    
    for _ in 0..500 {
        engine.measure_native();
    }
    
    c.bench_function("sample_count", |b| {
        b.iter(|| {
            black_box(engine.sample_count());
        });
    });
}

fn bench_clear(c: &mut Criterion) {
    c.bench_function("clear", |b| {
        b.iter(|| {
            let mut engine = ChronosEngine::new_native();
            for _ in 0..500 {
                engine.measure_native();
            }
            black_box(engine.clear());
        });
    });
}

criterion_group!(
    benches,
    bench_measure,
    bench_analyze,
    bench_full_workflow,
    bench_sample_count,
    bench_clear
);
criterion_main!(benches);
