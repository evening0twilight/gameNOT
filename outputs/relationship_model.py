"""Executable design probe, Python 3.9+, standard library only.

Run: python3 relationship_model.py
Writes balance-results.json beside this file. This is NOT a game, player model,
market forecast or fun validation. All coefficients are design hypotheses.
Probe scope: attributed memories, repair anti-farming, threshold hysteresis,
and exhaustive plans in a deliberately small mission cost model.
"""
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path
import json
import random
import copy


def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


@dataclass
class Memory:
    incident: str
    observer: str
    target: str
    category: str
    amplitude: float
    day: int  # when the observer learned of the incident
    half_life: float
    floor: float
    trust_loss: float
    remedy: str
    stage: int = 0

    def value(self, day):
        elapsed = max(0, day - self.day)
        floor = self.floor if self.stage < 2 else 0.0
        factor = (1.0, 0.85, 0.45)[self.stage]
        return self.amplitude * factor * (
            floor + (1 - floor) * 2 ** (-elapsed / self.half_life))


class Model:
    def __init__(self):
        self.memories = []
        self.seen = set()
        self.trust = defaultdict(lambda: 60.0)
        self.apologies = set()
        self.cooperations = set()
        self.used_repairs = set()
        self.stress = defaultdict(float)

    def incident(self, incident, observer, blame, day, *, severity=12,
                 sensitivity=1.0, category='fairness', serious=False,
                 trust_loss=8.0, known=True, remedy='restore_allocation',
                 half_life=None):
        # Ownership belongs in authored event rules, not an opaque model.
        if any(v < 0 for v in blame.values()) or sum(blame.values()) > 1.000001:
            raise ValueError('Responsibility weights must be >=0 and sum <=1')
        key = (incident, observer)
        if not known or key in self.seen:
            return False
        self.seen.add(key)
        total = min(40.0, max(0.0, severity * sensitivity))
        for target, weight in blame.items():
            if weight == 0:
                continue
            old_trust = self.trust[observer, target]
            self.trust[observer, target] = clamp(old_trust - trust_loss * weight)
            loss = old_trust - self.trust[observer, target]
            self.memories.append(Memory(
                incident, observer, target, category, total * weight, day,
                half_life or (8.0 if serious else 3.0),
                0.35 if serious else 0.0, loss, remedy))
        return True

    def resentment(self, observer, target, day):
        groups = defaultdict(list)
        serious = 0.0
        for m in self.memories:
            if (m.observer, m.target) != (observer, target):
                continue
            if m.floor:
                serious += m.value(day)
            else:
                groups[m.category].append(m.value(day))
        # Cap each ordinary category at the three strongest active memories.
        # Trust loss is not capped: repeated mistreatment is not free.
        return clamp(serious + sum(sum(sorted(v, reverse=True)[:3])
                                   for v in groups.values()))

    def acknowledge(self, incident, observer, target):
        for m in self.memories:
            if (m.incident, m.observer, m.target) == (incident, observer, target):
                if m.stage == 0:
                    m.stage = 1
                    return True
        return False

    def repair(self, incident, observer, target, action_id, remedy):
        # The actual game must validate that action_id was earned by gameplay.
        # This probe accepts such a validated action token as input.
        if action_id in self.used_repairs:
            return False
        for m in self.memories:
            if (m.incident, m.observer, m.target) == (incident, observer, target):
                if m.stage != 1 or m.remedy != remedy:
                    return False
                m.stage = 2
                self.used_repairs.add(action_id)
                key = (observer, target)
                # Restitution alone cannot raise trust above pre-harm trust.
                self.trust[key] = clamp(self.trust[key] + min(4.0, m.trust_loss / 2))
                return True
        return False

    def apologize(self, incident, observer, target):
        key = (incident, observer, target)
        if key in self.apologies or not any(
            (m.incident, m.observer, m.target) == key for m in self.memories):
            return False
        self.apologies.add(key)
        self.stress[observer] = clamp(self.stress[observer] - 4)
        return True  # no trust / resentment gain

    def cooperate(self, opportunity, observer, target):
        # A unique, externally validated meaningful cooperation opportunity.
        key = (opportunity, observer, target)
        if key in self.cooperations:
            return False
        self.cooperations.add(key)
        self.trust[observer, target] = clamp(self.trust[observer, target] + 4)
        return True


def pressure(resentment, stress):
    return clamp(resentment + 0.25 * max(0, stress - 40))


def band(previous, resentment, stress):
    q = pressure(resentment, stress)
    if previous:
        return q > 30 and resentment > 20
    return q >= 45 and resentment >= 25


def mission(seed, difficulty):
    rng = random.Random(seed)
    return dict(deadline=rng.randint(7, 10) + {'relaxed': 2, 'standard': 0, 'hard': -1}[difficulty],
                cash=rng.randint(0, 3), door=rng.randint(1, 2),
                bridge=2 + rng.randint(0, 2),
                tunnel=3 + rng.randint(0, 2), detour=4 + rng.randint(0, 1))


def plans(m, strained):
    result = []
    # 3 routes x 3 tools x 2 objectives. One equipment slot, known costs.
    for route in ('bridge', 'tunnel', 'detour'):
        for tool, cost in (('none', 0), ('winch', 2), ('crowbar', 1)):
            if cost > m['cash']:
                continue
            for medicine in (0, 1):
                travel = m[route]
                door = m['door']
                if route == 'bridge':
                    if tool == 'winch':
                        travel = max(1, travel - 1)
                    elif strained:
                        travel += 1  # agreed safety check, visible before choice
                if tool == 'crowbar':
                    door = max(0, door - 1)
                time = travel + door + 2 + 2 * medicine
                if time <= m['deadline']:
                    result.append(dict(route=route, tool=tool, medicine=medicine,
                                       cash_spent=cost, time=time))
    return result


def frontier(options):
    def dominates(a, b):
        av = (a['medicine'], -a['cash_spent'], -a['time'])
        bv = (b['medicine'], -b['cash_spent'], -b['time'])
        return all(x >= y for x, y in zip(av, bv)) and any(x > y for x, y in zip(av, bv))
    return [b for b in options if not any(dominates(a, b) for a in options)]


def checks():
    passed = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        passed.append(name)

    m = Model()
    m.incident('leader-order', 'Lin', {'leader': 1}, 0)
    check('leader decision does not blame uninvolved teammate', m.resentment('Lin', 'Xu', 0) == 0)
    check('relationships remain directional', m.resentment('leader', 'Lin', 0) == 0)
    before = m.resentment('Lin', 'leader', 0)
    m.incident('leader-order', 'Lin', {'leader': 1}, 0)
    check('replayed event is not applied twice', m.resentment('Lin', 'leader', 0) == before)
    m.incident('hidden', 'Lin', {'Xu': 1}, 0, known=False)
    check('unobserved event cannot cause mind-reading resentment', m.resentment('Lin', 'Xu', 0) == 0)
    m.incident('hidden', 'Lin', {'Xu': 1}, 2)
    check('later discovery applies event once', m.resentment('Lin', 'Xu', 2) == 12)
    m.stress['Lin'] = 80
    r0, t0 = m.resentment('Lin', 'Xu', 2), m.trust['Lin', 'Xu']
    for _ in range(100):
        m.apologize('hidden', 'Lin', 'Xu')
    check('100 apologies cannot farm trust or clear memory', (m.resentment('Lin', 'Xu', 2), m.trust['Lin', 'Xu'], m.stress['Lin']) == (r0, t0, 76))
    check('wrong restitution cannot erase a different injury', not m.repair('hidden', 'Lin', 'Xu', 'a', 'buy_gift'))
    m.acknowledge('hidden', 'Lin', 'Xu')
    check('wrong restitution is rejected even after acknowledgement', not m.repair('hidden', 'Lin', 'Xu', 'wrong', 'buy_gift'))
    m.repair('hidden', 'Lin', 'Xu', 'a', 'restore_allocation')
    check('hurt then repair cannot farm trust', m.trust['Lin', 'Xu'] < 60)
    for _ in range(100):
        m.cooperate('actual-mission-1', 'Lin', 'Xu')
    check('same cooperation cannot be farmed', m.trust['Lin', 'Xu'] == 60)
    m.incident('other', 'Lin', {'Xu': 1}, 3)
    m.acknowledge('other', 'Lin', 'Xu')
    check('one restitution action cannot pay for multiple harms', not m.repair('other', 'Lin', 'Xu', 'a', 'restore_allocation'))
    m.incident('severe', 'Lin', {'Xu': 1}, 3, severity=32, serious=True)
    mem = m.memories[-1]
    check('serious unresolved memory retains a floor', abs(mem.value(1000) - 11.2) < 1e-6)
    ordinary = m.memories[0]
    check('ordinary memory fades without infinite accumulation', ordinary.value(1000) < 1e-10)
    check('stress alone does not blame a teammate', not band(False, 0, 100))
    check('hysteresis stops threshold chatter', band(True, 44, 40) and not band(False, 44, 40))
    cycle = Model()
    for n in range(30):
        cycle.incident(str(n), 'A', {'B': 1}, n)
        cycle.acknowledge(str(n), 'A', 'B')
        cycle.repair(str(n), 'A', 'B', str(n), 'restore_allocation')
    check('repeated harm/repair remains worse than benign relationship', cycle.trust['A', 'B'] < 60)
    for start in range(101):
        low = Model()
        low.trust['A', 'B'] = start
        low.incident('harm', 'A', {'B': 1}, 0)
        low.acknowledge('harm', 'A', 'B')
        low.repair('harm', 'A', 'B', 'repair', 'restore_allocation')
        if low.trust['A', 'B'] > start:
            raise AssertionError('trust-floor restitution exploit')
    check('harm/repair cannot farm any starting trust level 0..100', True)
    for seed in range(100):
        f = Model()
        rng = random.Random(seed)
        for day in range(100):
            f.incident(str(day), 'A', {'B': rng.random()}, day,
                       severity=rng.uniform(0, 60), sensitivity=rng.uniform(.8, 1.3),
                       serious=rng.random() < .1)
            check_value = f.resentment('A', 'B', day)
            if not (0 <= check_value <= 100 and 0 <= f.trust['A', 'B'] <= 100):
                raise AssertionError('boundedness sweep')
    check('100 event streams x 100 days stay bounded', True)
    check('same seed reproduces mission', mission(55, 'standard') == mission(55, 'standard'))
    matched = True
    for seed in range(100):
        relaxed, standard, hard = [mission(seed, d) for d in ('relaxed', 'standard', 'hard')]
        matched &= relaxed.pop('deadline') == standard['deadline'] + 2
        matched &= hard.pop('deadline') == standard.pop('deadline') - 1
        matched &= relaxed == standard == hard
    check('difficulty comparison holds weather and equipment budget constant', matched)
    return passed


def run():
    results = dict(model_version='0.1-design-probe', date='2026-10-31',
                   limitations=['Synthetic inputs, not player behaviour or win rates',
                                'No economy, roster, full map, story selector or engine integration',
                                'Feasibility only at mission entry; does not rescue later bad choices',
                                'No verification of fun, willingness to pay or long-run optimal teams'],
                   checks=checks())
    results['trajectories'] = []
    for serious in (False, True):
        m = Model()
        m.incident('example', 'Lin', {'Xu': 1}, 0, severity=32 if serious else 12, serious=serious)
        repaired = copy.deepcopy(m)
        repaired.acknowledge('example', 'Lin', 'Xu')
        repaired.repair('example', 'Lin', 'Xu', 'real-restitution', 'restore_allocation')
        results['trajectories'].append(dict(serious=serious, days=[0, 3, 6, 12, 24],
            untreated=[round(m.resentment('Lin','Xu',d),2) for d in [0,3,6,12,24]],
            repaired_at_day_0=[round(repaired.resentment('Lin','Xu',d),2) for d in [0,3,6,12,24]]))
    results['mission_sweep'] = []
    for difficulty in ('relaxed', 'standard', 'hard'):
        for strained in (False, True):
            invalid, single, tool_frontier = [], 0, defaultdict(int)
            for seed in range(1000):
                options = plans(mission(seed, difficulty), strained)
                if not options:
                    invalid.append(seed)
                    continue
                f = frontier(options)
                outcomes = {(p['medicine'], p['cash_spent'], p['time']) for p in f}
                single += len(outcomes) == 1
                for tool in sorted({p['tool'] for p in f}):
                    tool_frontier[tool] += 1
            results['mission_sweep'].append(dict(difficulty=difficulty, strained=strained,
                candidates=1000, rejected_no_rescue_plan=len(invalid),
                rejection_seed_examples=invalid[:5], accepted=1000-len(invalid),
                accepted_with_only_one_pareto_outcome=single,
                frontier_tool_presence=dict(tool_frontier)))
    # Sensitivity probe: identical scripted minor incidents at d0,d2,d4,
    # one serious breach at d6. This is deliberately NOT a simulated player.
    results['sensitivity'] = []
    for multiplier in (.75, 1.0, 1.25):
        for ordinary_half_life in (2.0, 3.0, 5.0):
            m, active, pressure_days = Model(), False, []
            for day in range(21):
                if day in (0, 2, 4, 6):
                    m.incident(str(day), 'Lin', {'Xu': 1}, day,
                               severity=(32 if day == 6 else 12) * multiplier,
                               serious=day == 6, half_life=8 if day == 6 else ordinary_half_life)
                stress = 80 if day <= 6 else max(20, 80 - 12 * (day-6))
                active = band(active, m.resentment('Lin','Xu',day), stress)
                if active:
                    pressure_days.append(day)
            results['sensitivity'].append(dict(severity_multiplier=multiplier,
                ordinary_half_life=ordinary_half_life, active_band_days=pressure_days,
                note='band is not a count of disputes; encounter gates/cooldowns are not implemented'))
    path = Path(__file__).with_name('balance-results.json')
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    run()
