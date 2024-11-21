from python_actr import *
from collections import deque


class TowerOfHanoi(Model):

    s = False
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
        print(f'    Peg A has disks {list(self.pegs["A"])}, peg B has disks {list(self.pegs["B"])}, peg C has disks {list(self.pegs["C"])}.')

    def move(self, disk, dest):
        disk = int(disk)
        if dest not in self.pegs:
            raise ValueError(f'Invalid destination peg {dest}. Must be one of: A, B, C')
        src = None
        for key, peg in self.pegs.items():
            if peg and peg[0] == disk:
                src = key
                break
        if src is None:
            return
        if src == dest:
            return
        if any(d < disk for d in self.pegs[src]):
            return
        if self.pegs[dest] and self.pegs[dest][0] < disk:
            return
        self.pegs[src].popleft()
        self.pegs[dest].appendleft(disk)
        self.steps += 1
        print(f'\nStep {self.steps}:')
        print(f'    Disk {disk} was moved to peg {dest}.')
        print(f'    Peg A has disks {list(self.pegs["A"])}, peg B has disks {list(self.pegs["B"])}, peg C has disks {list(self.pegs["C"])}.')

    def check(self, disk, dest):
        disk = int(disk)
        src = None
        for key, peg in self.pegs.items():
            if disk in peg:
                src = key
                break
        self.y = ({'A', 'B', 'C'} - {src, dest}).pop()
        src_peg = self.pegs[src]
        dst_peg = self.pegs[dest]
        if src_peg[0] != disk:
            self.m = src_peg[src_peg.index(disk)-1]
            return
        if dst_peg and dst_peg[-1] < disk:
            self.m = dst_peg[-1]
            return
        self.m = None

    def satisfy(self, disk, dest):
        self.s = int(disk) in self.pegs[dest]


class WrapperEnv(Model):

    print('start...\n')
    towers = TowerOfHanoi(3)


class MyAgent(ACTR):

    goal = Buffer()
    imaginal = Buffer()
    DMBuffer = Buffer()
    DM = Memory(DMBuffer)

    def init():
        goal.set('p:3 pTo:C d:None dTo:None check:False recall:False count:False')
        DM.add('count 1 2')
        DM.add('count 2 3')

    def check(goal='d:!None?d dTo:!None?dTo check:False?check'):
        towers.check(d, dTo)
        goal.modify(check='True')

    def start_tower(goal='p:!1?p pTo:?pTo d:None?d dTo:None?dTo check:False recall:False'):
        goal.modify(d=p, dTo=pTo)

    def final_move(goal='p:1?p pTo:?pTo d:None?d dTo:None?dTo check:False recall:False'):
        towers.move(p, pTo)
        goal.clear()
        self.stop()

    def subgoal_blocker(goal='p:?p d:?d dTo:?dTo check:True?check', towers='m:!None?m y:?y'):
        DM.add('?p ?m ?y ?d ?dTo')
        goal.modify(d=m, dTo=y, check='False')

    def move(goal='p:?p pTo:?pTo d:!None?d dTo:!None?dTo check:True?check recall:?recall', towers='m:None?m y:!None?y'):
        towers.move(d, dTo)
        towers.satisfy(p, pTo)
        DM.request('?p ?d ?dTo ? ?')
        goal.modify(d='None', dTo='None', check='False', recall='True')

    def recall(goal='recall:True?recall', DMBuffer='? ? ? ?d ?dTo', towers='s:False'):
        goal.modify(d=d, dTo=dTo, recall='False')

    def satisfy(goal='p:?p d:?d dTo:?dTo recall:True?recall count:?count', towers='s:True?s'):
        DM.request('count ? ?p')
        goal.modify(count='True')

    def count(goal='count:True?count', DMBuffer='count ?n ?'):
        imaginal.set('?n')

    def change(goal='p:?p count:True?count', imaginal='!None?n'):
        imaginal.set('None')
        goal.modify(p=n, d='None', dTo='None', count='False', recall='False')


if __name__ == "__main__":
    env = WrapperEnv()
    env.agent = MyAgent()
    env.agent.towers = env.towers
    env.run()
    print()
