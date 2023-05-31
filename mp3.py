class Job:
    def __init__(self, job_id, time, size):
        self._id = job_id
        self._time = time
        self._size = size
        self._waiting_time = 0

    def decrement(self):
        self._time -= 1

    def is_complete(self):
        return self._time <= 0

    def set_waiting_time(self, waiting_time):
        self._waiting_time = waiting_time

    def __repr__(self):
        return "Job %d: Time: %d Size: %d" % (self._id, self._time, self._size)


class Memory:
    def __init__(self, mem_id, size):
        self._mem_id = mem_id
        self._size = size
        self._occupied_by = None

    def get_internal_fragmentation(self):
        if not self.available():
            return self._size - self._occupied_by._size

    def is_available(self):
        return not self._occupied_by

    def is_job_finished(self):
        return self._occupied_by.is_complete()

    def set_occupied(self, job):
        self._occupied_by = job

    def decrement(self):
        self._occupied_by.decrement()

    def __repr__(self):
        return "Memory %d: Size: %d Occupied By? %s" % (self._mem_id, self._size, self._occupied_by)


class Clock:
    def __init__(self):
        self._tick = 0

    def up(self):
        self._tick += 1


class Metrics:
    def __init__(self):
        self._throughput = []
        self._mem_never_used = []
        self._mem_heavily_used = []
        self._queue_length = 0
        self._time_in_queue = 0
        self._internal_fragmentation = []

    def add_throughput(self, curr_mem_list):
        self._throughput.append(
            sum(1 if not mem.is_available() else 0 for mem in curr_mem_list))

    def get_curr_throughput(self):
        return self._throughput[-1]


class System:
    def __init__(self, job_list, mem_list):
        self._job_list = [Job(*job) for job in job_list]
        self._mem_list = [Memory(*mem) for mem in mem_list]
        self._queue = self._job_list.copy()
        self._clock = Clock()
        self._metrics = Metrics()
        self.initialize()

    def initialize(self):
        idx = 0
        while idx < len(self._mem_list):
            mem = self._mem_list[idx]
        # for mem in self._mem_list:
            if not self.is_memory_full():
                if self.is_mem_allocatable(mem) and mem.is_available():
                    job = self.get_top()
                    if job._size <= mem._size:
                        mem.set_occupied(job)
                        idx += 1
                    else:
                        self._queue.append(job)
                else:
                    idx += 1
            else:
                break

        self._queue.sort(key=lambda job: job._id)

    def run(self):
        while self.is_occupied() or self.is_job_allocatable():
            print("Time Elapsed: %ds" % self._clock._tick)

            self._metrics.add_throughput(self._mem_list)
            self.status()
            # self._metrics.add_throughput(self._mem_list)
            # self.status()
            # self._clock.up()
            for mem in self._mem_list:
                if not mem.is_available():
                    if mem.is_job_finished():
                        mem.set_occupied(None)
                        self.initialize()
                    else:
                        mem.decrement()

            self._clock.up()
            input()

    def is_mem_allocatable(self, curr_mem):
        for job in self._queue:
            if job._size <= curr_mem._size:
                return True
        return False

    def is_job_allocatable(self):
        for mem in self._mem_list:
            if self.is_mem_allocatable(mem):
                return True
        return False

    def get_top(self):
        if len(self._queue) > 0:
            return self._queue.pop(0)
        else:
            return None

    def is_occupied(self):
        for mem in self._mem_list:
            if not mem.is_available():
                return True
        return False

    def is_empty(self):
        return len(self._queue) == 0

    def is_memory_full(self):
        for mem in self._mem_list:
            if mem.is_available():
                return False
        return True

    def status(self):
        for mem in self._mem_list:
            print(mem)

        print()
        print("Throughput:", end=' ')
        print(self._metrics.get_curr_throughput())
        print()

    def final_metrics(self):
        print("Time Elapsed: %ds" % self._clock._tick)

    def get_throughput(self):
        return sum(1 if not mem.is_available else 0 for mem in self._mem_list)


class FirstFit(System):
    def __init__(self, job_list, mem_list):
        super().__init__(job_list, mem_list)


class BestFit(System):
    def __init__(self, job_list, mem_list):
        super().__init__(job_list, mem_list)
        self._mem_list.sort(key=lambda mem: mem._size)


class WorstFit(System):
    def __init__(self, job_list, mem_list):
        super().__init__(job_list, mem_list)


def main():
    job_file = open('job_list.txt', 'r')
    mem_file = open('mem_list.txt', 'r')

    job_file.readline()
    mem_file.readline()

    job_list = [list(map(int, job.split())) for job in job_file]
    mem_list = [list(map(int, mem.split())) for mem in mem_file]

    first_fit = FirstFit(job_list, mem_list)
    # best_fit = BestFit(job_list, mem_list)
    # worst_fit = WorstFit(job_list, mem_list)

    first_fit.run()
    first_fit.final_metrics()
    # print()
    # best_fit.run()
    # print()
    # worst_fit.run()
    return


main()
