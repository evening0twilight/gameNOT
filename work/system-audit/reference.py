"""Design calculations only. This module is NOT imported by the game runtime.

Active memory amplitudes are funded once, with irreversible compression at caps.
The archive retains facts, but archived/unfunded weight never silently resurfaces.
"""
from dataclasses import dataclass, field
from copy import deepcopy

ENTER = (0, 45, 65, 80)
EXIT = (0, 35, 50, 60)

def band_after(previous, resentment, stress):
    q = min(100, resentment + .25 * max(stress - 40, 0))
    if resentment < 25:
        return 0
    while previous > 0 and q < EXIT[previous]:
        previous -= 1
    while previous < 3 and q >= ENTER[previous + 1]:
        previous += 1
    return previous

def value(m, day):
    if not m.get('active', True):
        return 0.0
    stage = m.get('stage', 0)
    floor = .35 if m['severe'] and stage < 2 else 0
    half = 8 if m['severe'] else 3
    return m['strength'] * (1, .85, .45)[stage] * (
        floor + (1 - floor) * 2 ** (-max(0, day - m['day']) / half))

def total(grudge, memories, day):
    # No clamp hides overflow: allocations themselves must satisfy the budget.
    result = grudge + sum(value(m, day) for m in memories)
    assert result <= 100 + 1e-8
    return min(100., result)

def fund(grudge, memories, day):
    """Run after adding/amending an incident, never refill weights after repair."""
    groups = {}
    for m in memories:
        if m.get('active', True) and not m['severe']:
            groups.setdefault(m['category'], []).append(m)
    for rows in groups.values():
        rows.sort(key=lambda m: (-value(m, day), str(m['id'])))
        for m in rows[3:]:
            m['active'] = False
        amount = sum(value(m, day) for m in rows[:3])
        if amount > 24:
            for m in rows[:3]:
                m['strength'] *= 24 / amount
    amount = sum(value(m, day) for m in memories)
    if amount > 100 - grudge:
        scale = (100 - grudge) / amount
        for m in memories:
            if m.get('active', True):
                m['strength'] *= scale
    return total(grudge, memories, day)

@dataclass
class Direction:
    grudge: float = 0
    trust: float = 50
    memories: list = field(default_factory=list)
    facts: dict = field(default_factory=dict)
    history_stage: int = 0
    used_tokens: set = field(default_factory=set)
    grudge_categories: tuple = ('promise',)

    def resentment(self, day):
        return total(self.grudge, self.memories, day)

    def add(self, incident, day, severity=12, loss=8, category='promise',
            severe=False, share=1, sensitivity=1, stress=10, known=True,
            occurrence_day=None, promise=None, deliberate=True, warned=False):
        assert incident and 0 <= share <= 1 and 0 <= self.grudge <= 100
        if not known or share == 0 or incident in self.facts or severity == 0:
            return False
        occurred = day if occurrence_day is None else occurrence_day
        assert occurred <= day
        recent = [f for f in self.facts.values()
                  if f['category'] == category and 0 <= occurred - f['occurred'] <= 2]
        unique_promises = {f['promise'] for f in recent
                           if f['deliberate'] and f['promise'] is not None}
        # Late discovery can create a memory, never retroactively invent a warning.
        escalate = (deliberate and promise is not None and promise not in unique_promises
                    and len(unique_promises) >= 2 and warned and occurred == day)
        if escalate:
            severity, loss, severe = 18, 12, True
        r = self.resentment(day)
        relevant_grudge = self.grudge if category in self.grudge_categories else 0
        multiplier = (min(1.3, max(.8, sensitivity))
                        * (1 + .7 * (relevant_grudge / 100) ** 2)
                        * (1 + .8 * (r / 100) ** 2)
                        * (1 + .25 * stress / 100)
                        * (1 + min(.4, .1 * len(recent))))
        amplitude = min(40, severity * share * multiplier)
        actual_loss = min(self.trust, loss * share)
        self.trust -= actual_loss
        self.memories.append(dict(id=incident, day=day, category=category,
                                  raw_strength=amplitude, strength=amplitude,
                                  severe=severe, stage=0, active=True,
                                  multiplier=multiplier, requested_loss=loss*share,
                                  actual_trust_loss=actual_loss, refunded=0))
        self.facts[incident] = dict(occurred=occurred, learned=day, category=category,
                                   promise=promise, deliberate=deliberate, severe=severe)
        fund(self.grudge, self.memories, day)
        return True

    def acknowledge(self, incident):
        m = next(m for m in self.memories if m['id'] == incident)
        if m['stage'] != 0:
            return False
        m['stage'] = 1
        return True

    def revise_consequence(self, incident, day, severity, loss, severe, share=1):
        """New authenticated consequences amend one incident, without reusing current R.
        This entry point only strengthens evidence. Proven false blame uses revoke().
        """
        m = next(m for m in self.memories if m['id'] == incident)
        assert not m.get('revoked') and day >= m['day'] and 0 < share <= 1
        raw_new = min(40, severity * share * m['multiplier'])
        assert raw_new >= m['raw_strength'] and loss*share >= m['requested_loss']
        before_template = dict(m, strength=m['raw_strength'], active=True)
        after_template = dict(m, strength=raw_new, active=True, severe=severe)
        gain = max(0, value(after_template,day)-value(before_template,day))
        current = value(m,day)
        unit = value(dict(after_template,strength=1),day)
        m['strength'] = (current+gain)/unit if unit else 0
        m['active'] = current+gain > 0
        m['raw_strength'] = raw_new
        m['severe'] = severe
        extra = min(self.trust, loss*share-m['requested_loss'])
        m['requested_loss'] = loss*share
        m['actual_trust_loss'] += extra
        self.trust -= extra
        fund(self.grudge,self.memories,day)

    def revoke(self, incident):
        m = next(m for m in self.memories if m['id'] == incident)
        if m.get('revoked'):
            return False
        m['active'] = False
        m['revoked'] = True
        self.trust = min(100,self.trust+max(0,m['actual_trust_loss']-m['refunded']))
        return True

    def repair(self, incident, token, evidence_incident):
        m = next(m for m in self.memories if m['id'] == incident)
        if not token or token in self.used_tokens or evidence_incident != incident or m['stage'] != 1 or m.get('revoked'):
            return False
        m['stage'] = 2
        self.used_tokens.add(token)
        m['refunded'] = min(4, m['actual_trust_loss'] / 2)
        self.trust = min(100, self.trust + m['refunded'])
        return True

    def history(self, stage, token):
        if stage != self.history_stage + 1 or stage > 3 or not token or token in self.used_tokens:
            return False
        self.grudge = max(0, self.grudge - (6, 12, 12)[stage - 1])
        self.history_stage = stage
        self.used_tokens.add(token)
        return True

def attribution(known, commander_decision=True, informed_voluntary_proposer=None):
    if not known or not commander_decision:
        return {}
    return {'leader': .5, informed_voluntary_proposer: .5} if informed_voluntary_proposer else {'leader': 1.}

def coalesce_effects(effects):
    """One decision's injury/failed evacuation/treatment delay are one breach.
    Distinct later concealment is a new incident; category is authored, not inferred.
    """
    groups = {}
    for e in effects:
        key = (e['observer'], e['target'], e['root_decision'])
        current = groups.get(key)
        if current is None:
            groups[key] = deepcopy(e)
        else:
            current['severity'] = max(current['severity'], e['severity'])
            current['loss'] = max(current['loss'], e['loss'])
            current['severe'] = current['severe'] or e['severe']
    return list(groups.values())

@dataclass
class ConflictScenes:
    next_day: dict = field(default_factory=dict)
    missions: set = field(default_factory=set)
    def trigger(self, pair, day, mission, band, relevant, warned, new_trigger):
        key = tuple(sorted(pair))
        if (band != 3 or not relevant or not warned or not new_trigger
                or day < self.next_day.get(key, 0) or mission in self.missions):
            return False
        self.next_day[key] = day + 2
        self.missions.add(mission)
        return True

def retrieval(downed, extracted, difficulty, abandoned_or_expired):
    if not downed:
        return 'healthy' if extracted else 'injury'
    if extracted:
        return 'injury'
    if difficulty == 'hard' and abandoned_or_expired:
        return 'medical_withdrawal'
    return 'injury'

def resolve_due_round(deadline, stabilized=False, extracted=False):
    # Called at end of this round, AFTER the full player phase and transport.
    return None if extracted else deadline + int(stabilized)

def contract_deadline(actor, created_day):
    # Plans requiring post-plan main duties cannot be promised too late.
    return created_day <= (21 if actor == 'su' else 20 if actor=='chen' else 22 if actor in {'lin','xu','he'} else 23)

def contract_status(created, fulfilled, withdrawn):
    return ('not_promised' if not created else 'fulfilled' if fulfilled else
            'interrupted_by_injury' if withdrawn else 'unfulfilled')

def relationship_overlays(events, actor):
    # Repairs reference exact incidents and directions; an unrelated repair cannot clear all.
    repaired = {(e['observer'], e['target'], e['repairs']) for e in events if e['kind']=='repair'}
    return [e for e in events if e['kind']=='breach'
            and actor in (e['observer'],e['target'])
            and (e['observer'],e['target'],e['id']) not in repaired]

def restitution_option(category):
    return {
        'promise': '重订一份带期限和退出条件的同范围安排，并在后续任务实际守约；不需收费',
        'fairness': '由责任方承担原先转嫁的真实班次；不能让受害者付费替其补偿',
        'humiliation': '在原公开范围更正事实，保留伤害曾发生的记录；不能撤回他人的记忆',
    }[category]
