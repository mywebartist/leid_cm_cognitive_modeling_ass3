from python_actr import *
from collections import deque


class TowerOfHanoi(Model):

    m = None
    y = None

    def __init__(self, n_disks):
        self.n_disks = n_disks
        self.steps = 0
        self.pegs = {
            'A': deque(range(1, n_disks+1)),
            'B': deque(),
            'C': deque()
        }
        print(f'Step {self.steps}:')
        print(f'    Peg A has disks {list(self.pegs["A"])}, peg B has disks {list(self.pegs["B"])}, peg C has disks {list(self.pegs["C"])}.\n')

    def move(self, disk, dest):
        disk = int(disk)
        for key, peg in self.pegs.items():
            if disk in self.pegs[dest]:
                return
            if peg and peg[0] == disk:
                self.pegs[key].popleft()
                self.pegs[dest].appendleft(disk)
                self.steps += 1
                print(f'Step {self.steps}:')
                print(f'    Disk {disk} was moved to peg {dest}.')
                print(f'    Peg A has disks {list(self.pegs["A"])}, peg B has disks {list(self.pegs["B"])}, peg C has disks {list(self.pegs["C"])}.\n')
                return
        raise ValueError(f'Disk {disk} was not found on any peg. A move must specify a disk that is currently on top of one of the pegs.')

    def check(self, disk, dest):
        disk = int(disk)
        source = None
        for key, peg in self.pegs.items():
            if disk in peg:
                source = key
                break
        self.y = ({'A', 'B', 'C'} - {source, dest}).pop()
        src_peg = self.pegs[source]
        dst_peg = self.pegs[dest]
        if src_peg[0] != disk:
            self.m = src_peg[src_peg.index(disk)-1]
        elif dst_peg and dst_peg[-1] < disk:
            self.m = dst_peg[-1]
        else:
            self.m = None

    def satisfy(self, disk, dest):
        self.s = int(disk) in self.pegs[dest]


class WrapperEnv(Model):

    print('start...\n')
    towers = TowerOfHanoi(3)


class MyAgent(ACTR):

    goal = Buffer()
    DMBuffer = Buffer()
    DM = Memory(DMBuffer)

    def init():
        goal.set('p:3 pTo:C d:None dTo:None check:False recall:False satisfied:False')
        DM.add('count 1 2')
        DM.add('count 2 3')

    def check(goal='d:!None?d dTo:!None?dTo check:False?check'):
        # x = input()
        # # print(goal.chunk, end='\t')
        # # print(f'd: {d}, dTo: {dTo}')
        towers.check(d, dTo)
        goal.modify(check='True')

    def start_tower(goal='p:!1?p pTo:?pTo d:None?d dTo:None?dTo check:False recall:False satisfied:False'):
        # x = input()
        # print(goal.chunk)
        goal.modify(d=p, dTo=pTo)

    def subgoal_blocker(goal='d:?d dTo:?dTo check:True?check', towers='m:!None?m y:?y'):
        # x = input()
        # print(goal.chunk, end='\t')
        # print(f'm: {m}, y: {y}')
        goal.modify(d=m, dTo=y, check='False')
        DM.add('?m ?y ?d ?dTo')

    def move(goal='d:!None?d dTo:!None?dTo check:True?check recall:?recall', towers='m:None?m y:!None?y'):
        towers.move(d, dTo)
        goal.modify(d='None', dTo='None', check='False', recall='True')
        # x = input()
        # print(goal.chunk, end='\t')
        # print(f'm: {m}, y: {y}')
        DM.request('?d ?dTo ? ?')

    def recall(goal='recall:True?recall', DMBuffer='? ? ?d ?dTo'):
        goal.modify(d=d, dTo=dTo, recall='False')
        # x = input()
        # print(goal.chunk)

    def observe(goal='p:!None?p pTo:!None?pTo recall:True?recall'):
        towers.satisfy(p, pTo)
        # x = input()
        # print(goal.chunk)
        goal.modify(recall='False')

    def satisfy(goal='satisfied:False?satisfied recall:False?recall', towers='s:True?s'):
        goal.modify(satisfied=s)
        # x = input()
        # print(goal.chunk, end='\t')
        # print(f's: {s}')

    def change_2(goal='p:3?p d:None?d dTo:None?dTo check:False recall:False satisfied:True?satisfied'):
        goal.modify(p='2', satisfied='False')


if __name__ == "__main__":
    env = WrapperEnv()
    env.agent = MyAgent()
    env.agent.towers = env.towers
    env.run()
    print()
