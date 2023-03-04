from time import perf_counter, time


class restCalculator:
    def __init__(self, interval: float, coefficient: float = 1.5) -> None:
        self._start = 0.0
        self._interval = interval
        self._threshold = coefficient * interval
        self._prev_val = 0.0

    def reset(self, value: float) -> None:
        self._start = value
        self._prev_val = value

    def calc(self, value: float) -> float:
        diff = value - self._prev_val
        if diff < self._threshold:
            remainder = self._interval - (value - self._start) % self._interval
        else:
            self._start = value
            remainder = 0.0
        self._prev_val = value
        return remainder


class SleepCalculator:
    def __init__(self, interval: float, coefficient: float = 1.1) -> None:
        self._start_count = 0.0
        self._interval = interval
        self._time_threshold = coefficient * interval
        self._prev_count = 0.0
        self._prev_time = 0.0
        self._start_count = 0.0
        self._start_time = 0.0

    def reset(self) -> None:
        self._set_start(perf_counter(), time())
        self._prev_count = self._start_count
        self._prev_time = self._start_time

    def calc(self) -> float:
        count = perf_counter()
        _time = time()
        if count >= self._prev_count:
            time_sleep, has_exceeded = self._calc(
                count, self._prev_count, self._start_count
            )
        else:
            time_sleep, has_exceeded = self._calc(
                _time, self._prev_time, self._start_time
            )
        if has_exceeded:
            self._set_start(count, _time)
        self._prev_count = count
        self._prev_time = _time
        return time_sleep

    def _calc(self, now: float, prev: float, start: float) -> tuple[float, bool]:
        diff = now - prev
        if diff < self._time_threshold:
            time_sleep = self._interval - (now - start) % self._interval
            has_exceeded = False
        else:
            time_sleep = 0.0
            has_exceeded = True
        return time_sleep, has_exceeded

    def _set_start(self, count: float, _time: float) -> None:
        self._start_count = count
        self._start_time = _time


if __name__ == "__main__":
    from time import sleep

    calculator = SleepCalculator(1)

    calculator.reset()
    for i in range(100):
        sleep_time = calculator.calc()
        sleep(sleep_time)
        print(time())
