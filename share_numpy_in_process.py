import time
from concurrent.futures.process import ProcessPoolExecutor
from dataclasses import dataclass
from multiprocessing.managers import SharedMemoryManager
from multiprocessing.shared_memory import SharedMemory
from typing import NamedTuple

import numpy as np
import numpy.typing as npt


def create_shared_memory(
    shape: tuple[int, ...], dtype: npt.DTypeLike, smm: SharedMemoryManager
) -> SharedMemory:
    size = int(np.dtype(dtype).itemsize * np.prod(shape))

    shm = smm.SharedMemory(size)
    return shm


def get_array_from_shared_memory(
    shape: tuple[int, ...], dtype: npt.DTypeLike, shm: SharedMemory
) -> npt.NDArray:
    array: npt.NDArray = np.ndarray(shape=shape, dtype=dtype, buffer=shm.buf)
    return array


class MemoryInfo(NamedTuple):
    shape: tuple[int, ...]
    dtype: npt.DTypeLike
    memory: SharedMemory


@dataclass(frozen=True)
class MemoryInfos:
    mem1: MemoryInfo
    mem2: MemoryInfo


def create_memory_info(
    shape: tuple[int, ...], dtype: npt.DTypeLike, smm: SharedMemoryManager
) -> MemoryInfo:
    shm = create_shared_memory(shape, dtype, smm)
    info = MemoryInfo(shape, dtype, shm)
    return info


def get_shm_array(info: MemoryInfo) -> npt.NDArray:
    array = get_array_from_shared_memory(info.shape, info.dtype, info.memory)
    return array


def process_func(memory_infos: MemoryInfos, i: int) -> None:
    array_mem1 = get_shm_array(memory_infos.mem1)
    array_mem2 = get_shm_array(memory_infos.mem2)
    array_mem1[i] += 1
    array_mem2[i] += 1
    print(array_mem1)
    print(array_mem2)


def main():
    NUM_WORKERS = 3
    with (
        SharedMemoryManager() as smm,
        ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor,
    ):
        memory_infos = MemoryInfos(
            mem1=create_memory_info(shape=(5,), dtype=np.float32, smm=smm),
            mem2=create_memory_info(shape=(4,), dtype=np.uint32, smm=smm),
        )
        array_mem1 = get_shm_array(memory_infos.mem1)
        array_mem2 = get_shm_array(memory_infos.mem2)
        array_mem1[0] = 13.4
        array_mem2[1] = 999
        print(array_mem1)
        print(array_mem2)
        for i in range(NUM_WORKERS):
            executor.submit(process_func, memory_infos, i)
            time.sleep(0.5)


if __name__ == "__main__":
    main()
