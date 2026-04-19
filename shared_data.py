import threading


class SensorData:
    """Thread-safe shared sensor readings."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._temp_c: int = 0
        self._humd: int = 0

    @property
    def temp_c(self) -> int:
        with self._lock:
            return self._temp_c

    @temp_c.setter
    def temp_c(self, value: int) -> None:
        with self._lock:
            self._temp_c = int(value)

    @property
    def humd(self) -> int:
        with self._lock:
            return self._humd

    @humd.setter
    def humd(self, value: int) -> None:
        with self._lock:
            self._humd = int(value)


# Backwards-compatible alias
SharedSHT31 = SensorData
