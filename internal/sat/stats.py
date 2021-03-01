import time


class Stats:
    def __init__(self):
        self.branching_count = 0
        self.start_time = time.perf_counter()

    def inc_bc(self):
        self.branching_count += 1

    def string(self) -> str:
        end_time = time.perf_counter()

        s = f"""
        ----- STATISTICS -----
        Branching count: {self.branching_count}
        Time elapsed: {end_time-self.start_time:0.4f} seconds
        ----------------------
        """
        return s
