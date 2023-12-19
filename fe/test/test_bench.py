from fe.bench.run import run_bench


def test_bench():
    try:
        run_bench()
    except Exception:
        assert 200 == 100, "test_bench过程出现异常"
