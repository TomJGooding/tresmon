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
        self.plt.yticks([0, 100], ["0", "100%"])
        self.plt.xfrequency(0)
        self.plt.plot(self.data)

    def update(self, cpu_percent: float) -> None:
        self.data.append(cpu_percent)
        self.plt.clear_data()
        self.plt.ylim(0, 100)
        self.plt.plot(self.data)
        self.refresh()


class TresmonApp(App):
    def compose(self) -> ComposeResult:
        yield CpuUsageHistory()

    def on_mount(self) -> None:
        self.set_interval(1.0, self.update_cpu_usage_history)  # type: ignore[arg-type]

    @work(thread=True, exclusive=True)
    def update_cpu_usage_history(self) -> None:
        cpu_usage_history = self.query_one(CpuUsageHistory)
        self.call_from_thread(cpu_usage_history.update, psutil.cpu_percent())
