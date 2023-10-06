from collections import deque

import psutil
from textual import work
from textual.app import App, ComposeResult
from textual_plotext import PlotextPlot


class CpuUsageHistory(PlotextPlot):
    data = deque([0.0] * 60, maxlen=60)

    def on_mount(self) -> None:
        self.plt.title("CPU Usage History")
        self.plt.ylim(0, 100)
        self.plt.yticks(ticks=[0, 100], labels=["0", f"{100:5}%"])
        self.plt.xfrequency(0)
        self.plt.plot(self.data)

    def update(self, cpu_percent: float) -> None:
        self.data.append(cpu_percent)
        self.plt.clear_data()
        self.plt.ylim(0, 100)
        self.plt.plot(self.data)
        self.refresh()


def format_bytes(bytes: int) -> str:
    size_unit = " B"
    size = float(bytes)
    for unit in [" B", "KB", "MB", "GB", "TB", "PB"]:
        size_unit = unit
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:3.1f} {size_unit}"


class MemoryUsageHistory(PlotextPlot):
    data = deque([0.0] * 60, maxlen=60)
    available_memory = psutil.virtual_memory().available

    def on_mount(self) -> None:
        self.plt.title("Memory Usage History")
        self.plt.ylim(0, self.available_memory)
        self.plt.yticks(
            ticks=[0, self.available_memory],
            labels=["0", format_bytes(self.available_memory)],
        )
        self.plt.xfrequency(0)
        self.plt.plot(self.data)

    def update(self, used_memory: int) -> None:
        self.data.append(used_memory)
        self.plt.clear_data()
        self.plt.ylim(0, self.available_memory)
        self.plt.plot(self.data)
        self.refresh()


class TresmonApp(App):
    def compose(self) -> ComposeResult:
        yield CpuUsageHistory()
        yield MemoryUsageHistory()

    def on_mount(self) -> None:
        self.set_interval(1.0, self.update_usage_history)  # type: ignore[arg-type]

    @work(thread=True, exclusive=True)
    def update_usage_history(self) -> None:
        cpu_usage_history = self.query_one(CpuUsageHistory)
        self.call_from_thread(cpu_usage_history.update, psutil.cpu_percent())

        memory_usage_history = self.query_one(MemoryUsageHistory)
        used_memory = psutil.virtual_memory().used
        self.call_from_thread(memory_usage_history.update, used_memory)
