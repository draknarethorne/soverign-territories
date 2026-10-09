import unittest
from unittest import mock

import codex_drift as cd


def altered(name, old, new):
    real = cd.read

    def read(n):
        t = real(n)
        return t.replace(old, new, 1) if n == name else t
    return mock.patch.object(cd, "read", read)


class CodexDriftTests(unittest.TestCase):
    def test_documents_match_the_data_now(self):
        self.assertEqual([], check_all())

    def test_a_changed_roster_cell_is_caught(self):
        with altered("sovereign_dawn_codex.md", "| Necromancer ", "| Wizard      "):
            self.assertTrue(any("class" in p for p in cd.check_roster()))

    def test_a_changed_physique_line_is_caught(self):
        with altered("drakn_sisters_physique.md", "Very long, lean athletic legs", "Short legs"):
            self.assertTrue(any("legs differs" in p for p in cd.check_blocks(
                "drakn_sisters_physique.md", "drakn-sisters/*-thorne.json", (), ("legs",))))

    def test_a_changed_dragon_field_is_caught(self):
        with altered("elder_dragons_details.md", 'silhouette: "Heavy, broad-chested colossus', 'silhouette: "Small lizard'):
            self.assertTrue(any("silhouette" in p for p in cd.check_dragons()))

    def test_a_changed_angel_build_is_caught(self):
        with altered("angel_primes_physique.md", "Petite, short, compact build", "Giant build"):
            self.assertTrue(any("Haniya" in p for p in cd.check_angels()))


def check_all():
    return (cd.check_roster() + cd.check_dragons() + cd.check_angels())


if __name__ == "__main__":
    unittest.main()
