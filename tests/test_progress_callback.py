from qwen_cpp_review.callbacks import ThroughputAndMemoryCallback, _format_duration


class FakeState:
    def __init__(self, **kwargs):
        self.global_step = kwargs.get("global_step", 10)
        self.max_steps = kwargs.get("max_steps", 100)
        self.epoch = kwargs.get("epoch", 0.1)
        self.num_input_tokens_seen = kwargs.get("num_input_tokens_seen", 0)
        self.best_metric = kwargs.get("best_metric")


def test_format_duration_renders_hours_minutes_seconds():
    assert _format_duration(0) == "0:00:00"
    assert _format_duration(59) == "0:00:59"
    assert _format_duration(3661) == "1:01:01"


def test_format_duration_handles_unknown_eta():
    assert _format_duration(float("inf")) == "--:--:--"
    assert _format_duration(-1) == "--:--:--"


def test_progress_line_carries_the_required_fields(capsys):
    callback = ThroughputAndMemoryCallback()
    callback.on_train_begin(None, FakeState(global_step=0), None)
    callback.on_log(
        None,
        FakeState(global_step=50, max_steps=200, epoch=0.25, num_input_tokens_seen=100_000),
        None,
        logs={"loss": 1.2345, "learning_rate": 1.5e-4, "grad_norm": 0.87},
    )

    out = capsys.readouterr().out
    assert "step 50/200" in out
    assert "25.0%" in out
    assert "loss 1.2345" in out
    assert "lr 1.50e-04" in out
    assert "grad 0.87" in out
    assert "it/s" in out
    assert "tok/s" in out
    assert "eta" in out


def test_log_without_loss_is_ignored(capsys):
    callback = ThroughputAndMemoryCallback()
    callback.on_log(None, FakeState(), None, logs={"learning_rate": 1e-4})

    assert capsys.readouterr().out == ""


def test_missing_grad_norm_does_not_crash(capsys):
    callback = ThroughputAndMemoryCallback()
    callback.on_log(None, FakeState(), None, logs={"loss": 2.0, "grad_norm": None})

    assert "grad 0.00" in capsys.readouterr().out


def test_evaluate_reports_loss_and_perplexity(capsys):
    callback = ThroughputAndMemoryCallback()
    callback.on_evaluate(
        None,
        FakeState(global_step=250, best_metric=1.1),
        None,
        metrics={"eval_loss": 1.5, "eval_runtime": 42.0},
    )

    out = capsys.readouterr().out
    assert "EVAL step 250" in out
    assert "eval_loss 1.5000" in out
    assert "perplexity 4.48" in out
    assert "best 1.1000" in out
    assert "took 42s" in out


def test_evaluate_without_metrics_is_silent(capsys):
    ThroughputAndMemoryCallback().on_evaluate(None, FakeState(), None, metrics=None)

    assert capsys.readouterr().out == ""
