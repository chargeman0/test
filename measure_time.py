import csv
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, stdev
from typing import Callable


@dataclass
class ValueInfo:
    n: int
    values: list
    index: int
    count: int

    def __init__(self, n: int, index: int) -> None:
        self.values = []
        self.n = n
        self.index = index
        self.count = 0


class Measurer:
    def __init__(self, save_path: str) -> None:
        self._value_dict: dict[str, ValueInfo] = {}
        self._save_path = Path(save_path)
        if not self._save_path.exists():
            self._save_path.touch()
        self._index = 0
        self._has_finished_values: list[bool] = []

    def add_stat(self, name: str, n: int) -> None:
        self._value_dict[name] = ValueInfo(n, self._index)
        self._has_finished_values.append(False)
        self._index += 1

    def add_value(self, name: str, value) -> None:
        info = self._value_dict[name]
        idx = info.index
        if not self._has_finished_values[idx]:
            info.values.append(value)
            info.count += 1
            if info.count >= info.n:
                self._has_finished_values[idx] = True
                if all(self._has_finished_values):
                    self.write_result()

    def _calc_statistics(self, name: str) -> tuple:
        values = self._value_dict[name].values
        _max = max(values)
        _min = min(values)
        _mean = mean(values)
        _stdev = stdev(values)
        return _max, _min, _mean, _stdev

    def _calc_stat_dict(self) -> dict:
        stat_dict: dict[str, tuple] = {}
        for name in self._value_dict.keys():
            stat_dict[name] = self._calc_statistics(name)
        return stat_dict

    def write_result(self) -> None:
        stat_dict: dict = self._calc_stat_dict()
        with open(self._save_path, "w", newline="") as f:
            writer = csv.writer(f)
            HEADER = ["name", "count", "max", "min", "mean", "stdev"]
            writer.writerow(HEADER)
            for name in self._value_dict.keys():
                low = (name, self._value_dict[name].n) + stat_dict[name]
                writer.writerow(low)


def time_measurable_func(
    func: Callable,
    name: str,
    n: int,
    measurer: Measurer,
    get_start=None,
    measure_time=None,
):
    def _get_start() -> float:
        start = time.perf_counter()
        return start

    def _time_measurer():
        measurer.add_stat(name, n)

        def _measure(start: float):
            elapsed = time.perf_counter() - start
            measurer.add_value(name, elapsed)

        return _measure

    if get_start is None:
        _get_start = _get_start
    else:
        _get_start = get_start
    if measure_time is None:
        _measure_time = _time_measurer()
    else:
        _measure_time = measure_time

    def _wrapper(*args, **kwargs):
        start = _get_start()
        result = func(*args, **kwargs)
        _measure_time(start)
        return result

    return _wrapper


if __name__ == "__main__":
    save_path = ".\\data\\stat.csv"
    measurer = Measurer(save_path)

    def _print(a):
        print("1" + a)

    class Test:
        def __init__(self, need_wrap) -> None:
            self.func2 = _print
            self.func1 = self._func1
            if need_wrap:
                self.func2 = time_measurable_func(self.func2, "func2", 3, measurer)
                self.func1 = time_measurable_func(self._func1, "func1", 3, measurer)

        def _func1(self, a):
            print("2" + a)

    need_measure = True
    test = Test(need_measure)
    for i in range(5):
        test.func1("a")
        test.func2("b")
