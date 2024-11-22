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
            return
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

    def check(self, p, disk, dest):
        p, disk = int(p), int(disk)
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
        if dst_peg and dst_peg[0] < disk:
            self.m = max(d for d in dst_peg if d < p)
            return
        self.m = None

    def satisfy(self, disk, dest):
        self.s = int(disk) in self.pegs[dest]


class WrapperEnv(Model):

    print('start...\n')
    towers = TowerOfHanoi(4)


class AlgorithmicAgent(ACTR):

    goal = Buffer()
    imaginal = Buffer()
    DMBuffer = Buffer()
    DM = Memory(DMBuffer)

    debug = True

    def init():
        goal.set('p:4 pTo:C d:None dTo:None check:False recall:False tree:None satisfied:False')
        imaginal.set('None')
        DM.add('count 0 1')
        DM.add('count 1 2')
        DM.add('count 2 3')
        DM.add('count 3 4')
        DM.add('count 5 6')
        if debug:
            print(f'\nINIT: {goal.chunk}')

    def start_tower(goal='p:!1?p pTo:?pTo d:None?d dTo:None?dTo check:False recall:False', imaginal='None'):
        imaginal.set('0')
        goal.modify(d=p, dTo=pTo)
        if debug:
            print(f'START: {goal.chunk}')

    def final_move(goal='p:1?p pTo:?pTo d:None dTo:None check:False recall:False', imaginal='None'):
        towers.move(p, pTo)
        goal.clear()
        if debug:
            print(f'\nFINAL: {goal.chunk}')
        self.stop()

    def check(goal='p:!None?p d:!None?d dTo:!None?dTo check:False?check tree:None', imaginal='?depth'):
        towers.check(p, d, dTo)
        goal.modify(check='True')
        if debug:
            print(f'CHECK: {goal.chunk}    DEPTH: {depth}')

    def subgoal(goal='check:True tree:None?tree', towers='m:!None?m y:?y', imaginal='?depth'):
        DM.request('count ?depth ?')
        goal.modify(tree='Down')
        if debug:
            print(f'SUBGOAL: {goal.chunk}    DEPTH: {depth}')

    def down(goal='tree:Down?tree', DMBuffer='count ? ?n', imaginal='?depth'):
        imaginal.set('?n')
        goal.modify(tree='Blocked')
        if debug:
            print(f'DOWN: {goal.chunk}    DEPTH: {depth}')

    def blocker(goal='p:?p d:?d dTo:?dTo check:True?check tree:Blocked?tree', towers='m:!None?m y:?y', imaginal='?depth'):
        DM.add('?p ?depth ?m ?y ?d ?dTo')
        goal.modify(d=m, dTo=y, check='False', tree='None')
        if debug:
            print(f'BLOCKER: {goal.chunk}    DEPTH: {depth}\n\n\tADD DMBuffer: {p} {depth} {m} {y} {d} {dTo}\n')

    def move(goal='p:?p pTo:?pTo d:!None?d dTo:!None?dTo check:True?check recall:?recall', towers='m:None?m y:!None?y', imaginal='?depth'):
        towers.move(d, dTo)
        towers.satisfy(p, pTo)
        DM.request('?p ?depth ?d ?dTo ? ?')
        goal.modify(d='None', dTo='None', check='False', recall='True')
        if debug:
            print(f'\nMOVE: {goal.chunk}    DEPTH: {depth}\n\n\tREQ DMBuffer: {p} {depth} {d} {dTo} ? ?\n')

    def recall(goal='recall:True?recall tree:None', DMBuffer='? ? ? ? ?d ?dTo', towers='s:False', imaginal='?depth'):
        DM.request('count ? ?depth')
        goal.modify(d=d, dTo=dTo, recall='False', tree='Up')
        if debug:
            print(f'RECALL: {goal.chunk}    DEPTH: {depth}\n\n\tREC DMBuffer: {DMBuffer.chunk}\n')

    def up(goal='tree:Up?tree', DMBuffer='count ?n ?', imaginal='?depth'):
        imaginal.set('?n')
        goal.modify(tree='None')
        if debug:
            print(f'UP: {goal.chunk}    DEPTH: {depth}')

    def satisfy(goal='p:?p d:?d dTo:?dTo recall:True?recall satisfied:False?satisfied', towers='s:True?s', imaginal='?depth'):
        DM.request('count ? ?p')
        goal.modify(satisfied='True')
        if debug:
            print(f'SATISFY: {goal.chunk}    DEPTH: {depth}')

    def change(goal='p:?p satisfied:True?satisfied', DMBuffer='count ?n ?', imaginal='?depth'):
        imaginal.set('None')
        goal.modify(p=n, d='None', dTo='None', recall='False', satisfied='False')
        if debug:
            print(f'CHANGE: {goal.chunk}    DEPTH: {depth}')


if __name__ == "__main__":
    env = WrapperEnv()
    env.agent = AlgorithmicAgent()
    env.agent.towers = env.towers
    env.run()
    print()
