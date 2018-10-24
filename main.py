"""
Grant H. Slape
CS 4328.001 Operating Systems
CPU Scheduler Simulator
"""
from src.sim import Simulator


def main():
    sim = Simulator(method=Simulator.Method['FCFS'])
    sim.run()


if __name__ == '__main__':
    main()
