from termcolor import cprint


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
        self._id = mem_id
        self._size = size
        self._upper_limit = 0
        self._occupied_by = None

    def get_int_frag(self):
        if not self.is_available():
            return self._size - self._occupied_by._size
        return 0

    def is_available(self):
        return not self._occupied_by

    def is_job_finished(self):
        return self._occupied_by.is_complete()

    def set_occupied(self, job):
        self._occupied_by = job

    def set_upper_limit(self, limit):
        self._upper_limit = limit

    def decrement(self):
        self._occupied_by.decrement()

    def __repr__(self):
        return "Memory %d: Size: %d Occupied By? %s" % (self._id, self._size, self._occupied_by)


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
        self._int_frag = []
        self._queue_length = 0
        self._time_in_queue = 0
        self._total_mem = 10

    def add_throughput(self, curr_mem_list):
        self._throughput.append(
            sum(1 if not mem.is_available() else 0 for mem in curr_mem_list))

    def add_mem_never_used(self, curr_mem_list):
        self._mem_never_used.append(
            sum(1 if mem.is_available() else 0 for mem in curr_mem_list))

    def add_mem_heavily_used(self, curr_mem_list):
        self._mem_heavily_used.append(
            sum(1 if not mem.is_available() else 0 for mem in curr_mem_list))

    def add_int_frag(self, curr_mem_list):
        self._int_frag.append(
            sum(mem.get_int_frag() for mem in curr_mem_list))

    def get_curr_throughput(self):
        return self._throughput[-1]

    def get_mem_never_used(self):
        return "%.1f%%" % ((self._mem_never_used[-1]/self._total_mem) * 100)

    def get_mem_heavily_used(self):
        return self._mem_heavily_used[-1]

    def get_int_frag(self):
        return self._int_frag[-1]


class System:
    def __init__(self, job_list, mem_list):
        self._job_list = [Job(*job) for job in job_list]
        self._mem_list = [Memory(*mem) for mem in mem_list]
        self._queue = self._job_list.copy()
        self._clock = Clock()
        self._metrics = Metrics()
        self.configure_limit()

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
                        self._queue.sort(key=lambda job: job._id)
                    else:
                        self._queue.append(job)
                else:
                    idx += 1
            else:
                break

    def run(self):
        while self.is_occupied() or self.is_jobs_allocatable():
            cprint("\nTime Elapsed: %ds\n" % self._clock._tick, "light_green")

            self._metrics.add_mem_never_used(self._mem_list)
            self._metrics.add_throughput(self._mem_list)
            self._metrics.add_mem_never_used(self._mem_list)
            self._metrics.add_int_frag(self._mem_list)
            self.status()

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

    def is_jobs_allocatable(self):
        for mem in self._mem_list:
            if self.is_mem_allocatable(mem):
                return True
        return False

    def is_valid_job(self, job):
        for mem in self._mem_list:
            if job._size <= mem._size:
                return True
        return False

    def get_top(self):
        if len(self._queue) > 0:
            return self._queue.pop(0)
        else:
            return None

    def get_queue_length(self):
        return sum(1 if self.is_valid_job(job) else 0 for job in self._queue)

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

    def configure_limit(self):
        curr_sum = 0
        for mem in self._mem_list:
            curr_sum += mem._size
            mem.set_upper_limit(curr_sum)

    def status(self):
        cprint("┅" * 38 + " " + self._title + " " + 38 * "┅", "cyan")
        self.display_chart()

        print()
        cprint("Throughput:", "light_magenta", end=' ')
        print(self._metrics.get_curr_throughput())
        cprint("Storage utilization:", "light_magenta")
        cprint('{:>40}'.format("Percentage of Partitions Never Used:"
                               ), "dark_grey", end=' ')
        print(self._metrics.get_mem_never_used())

        cprint('{:>42}'.format("Percentage of Partitions Heavily Used:"
                               ), "dark_grey", end=' ')
        print(None)  # Change this

        cprint("Waiting Queue Length:", "light_magenta", end=' ')
        print(self.get_queue_length())

        cprint("Waiting Time in Queue:", "light_magenta", end=' ')
        print(None)  # Change this

        cprint("Total Internal Fragmentation:", "light_magenta", end=' ')
        print(self._metrics.get_int_frag())

    def display_chart(self):
        mem_list = sorted(self._mem_list, key=lambda mem: mem._id)
        print("{:<18}".format(""), end='')
        print("┌──────────────────────┬── 0")
        for (idx, mem) in enumerate(mem_list):
            if mem.is_available():
                print("{:^18}".format("Memory Block %d" % mem._id), end='')
                print("│ {:^20} │".format("No Job Assigned"))
            else:
                int_frag = mem.get_int_frag()
                print("{:<18}".format(""), end='')
                print("│ {:^20} │".format(
                    "Job %d (%ds)" % (mem._occupied_by._id,  mem._occupied_by._time)))

                print("{:^18}".format("Memory Block %d" % mem._id), end='')
                print("│ {:^20} │".format("Size: %d" % mem._size))

                print("{:<18}".format(""), end='')
                print("│ {:^20} │".format(
                    "Int. Frag.: %d" % int_frag))

            print("{:<18}".format(""), end='')
            if idx == len(mem_list) - 1:
                print(
                    "└──────────────────────┴──", mem._upper_limit)
            else:
                print(
                    "├──────────────────────┼──", mem._upper_limit)

    def final_metrics(self):
        print("Time Elapsed: %ds" % self._clock._tick)


class FirstFit(System):
    def __init__(self, job_list, mem_list):
        super().__init__(job_list, mem_list)
        self._title = "First Fit"
        self.initialize()


class BestFit(System):
    def __init__(self, job_list, mem_list):
        super().__init__(job_list, mem_list)
        self._title = "Best Fit"
        self._mem_list.sort(key=lambda mem: mem._size)
        self.initialize()


class WorstFit(System):
    def __init__(self, job_list, mem_list):
        super().__init__(job_list, mem_list)
        self._title = "Worst Fit"
        self._mem_list.sort(key=lambda mem: mem._size, reverse=True)
        self.initialize()


def main():
    job_file = open('job_list.txt', 'r')
    mem_file = open('mem_list.txt', 'r')

    job_file.readline()
    mem_file.readline()

    job_list = [list(map(int, job.split())) for job in job_file]
    mem_list = [list(map(int, mem.split())) for mem in mem_file]

    first_fit = FirstFit(job_list, mem_list)
    # best_fit = BestFit(job_list, mem_list)
    worst_fit = WorstFit(job_list, mem_list)

    first_fit.run()
    first_fit.final_metrics()
    # print()
    # best_fit.run()
    # best_fit.final_metrics()
    # print()
    # worst_fit.run()
    # worst_fit.final_metrics()
    return


main()
