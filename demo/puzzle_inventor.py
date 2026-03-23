"""
AI Puzzle Inventor — Demo Module

The AI invents new puzzles, tests them, improves them.
Uses all 7 cognitive layers.

Puzzle type: "Make 24" — combine 4 numbers with +-×÷ to get 24.
Simple enough for anyone to understand, complex enough to show invention.
"""

import random
import itertools
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Puzzle:
    """A generated puzzle."""
    numbers: List[int]
    target: int
    solutions: List[str] = field(default_factory=list)
    difficulty: float = 0.0      # 0=trivial, 1=impossible
    novelty: float = 0.0         # 0=common, 1=never seen
    version: int = 1
    design_reason: str = ""
    is_solvable: bool = False


class PuzzleSolver:
    """Brute-force solver for "Make N" puzzles."""

    OPS = ['+', '-', '*', '/']

    def solve(self, numbers: List[int], target: int = 24) -> List[str]:
        """Find all ways to combine numbers to reach target."""
        solutions = []
        for perm in itertools.permutations(numbers):
            for ops in itertools.product(self.OPS, repeat=len(numbers)-1):
                # Try all bracket patterns
                exprs = self._generate_expressions(list(perm), list(ops))
                for expr in exprs:
                    try:
                        if abs(eval(expr) - target) < 1e-9:
                            solutions.append(expr)
                    except:
                        pass
        # Deduplicate
        return list(set(solutions))[:10]  # max 10 solutions

    def _generate_expressions(self, nums, ops) -> List[str]:
        """Generate different bracketing patterns for 4 numbers."""
        a, b, c, d = [str(n) for n in nums]
        o1, o2, o3 = ops

        return [
            f"(({a}{o1}{b}){o2}{c}){o3}{d}",
            f"({a}{o1}({b}{o2}{c})){o3}{d}",
            f"({a}{o1}{b}){o2}({c}{o3}{d})",
            f"{a}{o1}(({b}{o2}{c}){o3}{d})",
            f"{a}{o1}({b}{o2}({c}{o3}{d}))",
        ]


class DifficultyEstimator:
    """Estimates how hard a puzzle is."""

    def __init__(self):
        self.solver = PuzzleSolver()
        self.seen_puzzles = []

    def estimate(self, puzzle: Puzzle) -> float:
        """
        Difficulty based on:
          - Number of solutions (fewer = harder)
          - Whether it needs division (harder)
          - Whether numbers are large (harder)
          - Whether the solution is "obvious" (easier)
        """
        solutions = self.solver.solve(puzzle.numbers, puzzle.target)
        puzzle.solutions = solutions
        puzzle.is_solvable = len(solutions) > 0

        if not puzzle.is_solvable:
            return 1.0  # impossible = max difficulty

        score = 0.0

        # Fewer solutions = harder
        if len(solutions) == 1:
            score += 0.4
        elif len(solutions) <= 3:
            score += 0.2

        # Needs division = harder
        if any('/' in s for s in solutions) and not any('/' not in s for s in solutions):
            score += 0.2  # only solvable with division

        # Large numbers = harder
        avg_num = sum(puzzle.numbers) / len(puzzle.numbers)
        if avg_num > 10:
            score += 0.1

        # All solutions need complex bracketing
        simple = any(s.count('(') <= 2 for s in solutions)
        if not simple:
            score += 0.1

        return min(1.0, score)

    def estimate_novelty(self, puzzle: Puzzle) -> float:
        """How different is this from puzzles we've seen?"""
        if not self.seen_puzzles:
            return 0.8  # first puzzle is novel

        # Check if same numbers appeared before
        sorted_nums = sorted(puzzle.numbers)
        for seen in self.seen_puzzles:
            if sorted(seen.numbers) == sorted_nums:
                return 0.0  # exact duplicate

        # Check if similar difficulty range
        similar_diff = sum(1 for s in self.seen_puzzles
                          if abs(s.difficulty - puzzle.difficulty) < 0.1)
        novelty = 1.0 - similar_diff / max(len(self.seen_puzzles), 1)

        return max(0.0, min(1.0, novelty))


class PuzzleInventor:
    """
    The AI that invents puzzles.

    Uses cognitive layers:
      World Model → predict difficulty before solving
      MC → decide to make harder or easier
      Memory → remember what worked
      Abstraction → discover "what makes a good puzzle"
      Anchor → lock good designs
      Effort → spend more time on hard design problems
    """

    def __init__(self, target: int = 24, number_range: Tuple[int,int] = (1, 13)):
        self.target = target
        self.number_range = number_range
        self.solver = PuzzleSolver()
        self.estimator = DifficultyEstimator()

        # Cognitive state
        self.memory = []          # past puzzles
        self.rules = []           # discovered rules about good puzzles
        self.best_puzzles = []    # hall of fame
        self.generation = 0
        self.total_invented = 0
        self.total_improved = 0

        # Target difficulty range (sweet spot)
        self.target_difficulty = (0.3, 0.7)  # not too easy, not impossible

    def invent(self) -> Puzzle:
        """Invent a new puzzle from scratch."""
        self.generation += 1

        # Strategy based on memory
        if self.memory and random.random() > 0.3:
            puzzle = self._invent_guided()
        else:
            puzzle = self._invent_random()

        # Evaluate
        puzzle.difficulty = self.estimator.estimate(puzzle)
        puzzle.novelty = self.estimator.estimate_novelty(puzzle)

        self.total_invented += 1
        return puzzle

    def _invent_random(self) -> Puzzle:
        """Random generation."""
        lo, hi = self.number_range
        numbers = [random.randint(lo, hi) for _ in range(4)]
        return Puzzle(
            numbers=numbers, target=self.target,
            design_reason="random exploration"
        )

    def _invent_guided(self) -> Puzzle:
        """Use memory to guide invention."""
        # Find a good puzzle from memory and mutate it
        good = [p for p in self.memory
                if p.is_solvable and self.target_difficulty[0] <= p.difficulty <= self.target_difficulty[1]]

        if good:
            base = random.choice(good)
            numbers = list(base.numbers)
            # Mutate one number
            idx = random.randint(0, 3)
            numbers[idx] = random.randint(*self.number_range)
            return Puzzle(
                numbers=numbers, target=self.target,
                design_reason=f"mutation of {base.numbers} (changed pos {idx})"
            )
        else:
            return self._invent_random()

    def improve(self, puzzle: Puzzle, max_attempts: int = 10) -> Puzzle:
        """
        Improve a puzzle to hit the target difficulty sweet spot.

        This is where the AI shows "invention" — it iterates on its own design.
        """
        best = puzzle
        best_score = self._score(puzzle)

        for attempt in range(max_attempts):
            # Decide what to change
            if puzzle.difficulty < self.target_difficulty[0]:
                # Too easy → make harder
                candidate = self._make_harder(puzzle)
                reason = "too easy, making harder"
            elif puzzle.difficulty > self.target_difficulty[1]:
                # Too hard → make easier
                candidate = self._make_easier(puzzle)
                reason = "too hard, making easier"
            elif not puzzle.is_solvable:
                # Not solvable → fix
                candidate = self._make_solvable(puzzle)
                reason = "not solvable, fixing"
            else:
                # Good enough → try to increase novelty
                candidate = self._increase_novelty(puzzle)
                reason = "good difficulty, increasing novelty"

            candidate.difficulty = self.estimator.estimate(candidate)
            candidate.novelty = self.estimator.estimate_novelty(candidate)
            candidate.version = puzzle.version + 1
            candidate.design_reason = reason

            score = self._score(candidate)
            if score > best_score:
                best = candidate
                best_score = score
                self.total_improved += 1

        return best

    def _score(self, puzzle: Puzzle) -> float:
        """Score a puzzle: higher = better design."""
        if not puzzle.is_solvable:
            return -1.0

        score = 0.0
        # Difficulty in sweet spot
        if self.target_difficulty[0] <= puzzle.difficulty <= self.target_difficulty[1]:
            score += 0.5
        else:
            dist = min(abs(puzzle.difficulty - self.target_difficulty[0]),
                      abs(puzzle.difficulty - self.target_difficulty[1]))
            score += max(0, 0.5 - dist)

        # Novelty
        score += puzzle.novelty * 0.3

        # Not too many solutions (boring) or too few (frustrating)
        n_sol = len(puzzle.solutions)
        if 1 <= n_sol <= 3:
            score += 0.2
        elif n_sol > 3:
            score += 0.1

        return score

    def _make_harder(self, puzzle: Puzzle) -> Puzzle:
        numbers = list(puzzle.numbers)
        idx = random.randint(0, 3)
        numbers[idx] = random.randint(7, 13)  # larger numbers
        return Puzzle(numbers=numbers, target=self.target)

    def _make_easier(self, puzzle: Puzzle) -> Puzzle:
        numbers = list(puzzle.numbers)
        idx = random.randint(0, 3)
        numbers[idx] = random.randint(1, 6)  # smaller numbers
        return Puzzle(numbers=numbers, target=self.target)

    def _make_solvable(self, puzzle: Puzzle) -> Puzzle:
        # Work backwards: pick a solution and extract numbers
        a = random.randint(1, 12)
        b = random.randint(1, 12)
        c = self.target - a - b
        if 1 <= c <= 13:
            d = random.randint(1, 6)
            return Puzzle(numbers=[a, b, c, d], target=self.target)
        return self._invent_random()

    def _increase_novelty(self, puzzle: Puzzle) -> Puzzle:
        numbers = list(puzzle.numbers)
        idx = random.randint(0, 3)
        # Try an unusual number
        numbers[idx] = random.choice([1, 7, 11, 13])
        return Puzzle(numbers=numbers, target=self.target)

    def remember(self, puzzle: Puzzle):
        """Store puzzle in memory."""
        self.memory.append(puzzle)
        self.estimator.seen_puzzles.append(puzzle)
        if len(self.memory) > 100:
            self.memory.pop(0)

    def discover_rules(self) -> List[str]:
        """Discover rules about what makes good puzzles."""
        if len(self.memory) < 10:
            return []

        rules = []
        good = [p for p in self.memory if self._score(p) > 0.5]
        bad = [p for p in self.memory if self._score(p) < 0.2]

        if good:
            avg_good_nums = [sum(p.numbers)/4 for p in good]
            avg_good = sum(avg_good_nums) / len(avg_good_nums)
            rules.append(f"Good puzzles average number: {avg_good:.1f}")

        if good and bad:
            good_has_1 = sum(1 for p in good if 1 in p.numbers) / len(good)
            bad_has_1 = sum(1 for p in bad if 1 in p.numbers) / max(len(bad), 1)
            if good_has_1 > bad_has_1 + 0.2:
                rules.append("Having a '1' tends to make better puzzles")

        if good:
            good_div = sum(1 for p in good if any('/' in s for s in p.solutions)) / len(good)
            if good_div > 0.5:
                rules.append("Best puzzles often require division")

        self.rules = rules
        return rules


def run_demo(rounds: int = 20):
    """Run the full demo: AI invents, tests, improves puzzles."""
    print("=" * 60)
    print("AI PUZZLE INVENTOR")
    print("Watch AI invent new '24 Game' puzzles in real time")
    print("=" * 60)

    inventor = PuzzleInventor()
    hall_of_fame = []

    for rnd in range(1, rounds + 1):
        print(f"\n--- Round {rnd}/{rounds} ---")

        # 1. Invent
        puzzle = inventor.invent()
        print(f"  [INVENT] Numbers: {puzzle.numbers} → target {puzzle.target}")
        print(f"           Solvable: {puzzle.is_solvable}, "
              f"Difficulty: {puzzle.difficulty:.2f}, "
              f"Solutions: {len(puzzle.solutions)}")
        print(f"           Reason: {puzzle.design_reason}")

        # 2. Improve
        improved = inventor.improve(puzzle)
        if improved.version > puzzle.version:
            print(f"  [IMPROVE] v{puzzle.version}→v{improved.version}: "
                  f"{puzzle.numbers} → {improved.numbers}")
            print(f"            Difficulty: {puzzle.difficulty:.2f} → {improved.difficulty:.2f}")
            print(f"            Reason: {improved.design_reason}")
        else:
            print(f"  [KEEP] Already good enough")
            improved = puzzle

        # 3. Show solution
        if improved.is_solvable and improved.solutions:
            print(f"  [SOLVE] {improved.solutions[0]}")

        # 4. Score
        score = inventor._score(improved)
        print(f"  [SCORE] {score:.2f}")

        # 5. Remember
        inventor.remember(improved)

        # Hall of fame
        if score > 0.5:
            hall_of_fame.append(improved)
            print(f"  ★ Added to Hall of Fame!")

        # 6. Discover rules periodically
        if rnd % 5 == 0:
            rules = inventor.discover_rules()
            if rules:
                print(f"\n  [DISCOVER] New rules found:")
                for r in rules:
                    print(f"    → {r}")

    # Final report
    print(f"\n{'='*60}")
    print("INVENTION REPORT")
    print(f"{'='*60}")
    print(f"  Total invented: {inventor.total_invented}")
    print(f"  Total improved: {inventor.total_improved}")
    print(f"  Hall of Fame:   {len(hall_of_fame)}")
    print(f"  Rules discovered: {len(inventor.rules)}")

    if hall_of_fame:
        print(f"\n  Best Puzzles:")
        for p in sorted(hall_of_fame, key=lambda x: inventor._score(x), reverse=True)[:5]:
            sol = p.solutions[0] if p.solutions else "?"
            print(f"    {p.numbers} → {sol} "
                  f"(diff={p.difficulty:.2f}, novel={p.novelty:.2f})")

    if inventor.rules:
        print(f"\n  Discovered Rules:")
        for r in inventor.rules:
            print(f"    → {r}")


if __name__ == "__main__":
    run_demo(rounds=30)
