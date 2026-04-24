import unittest

from latvia_party_sim import CycleStage, default_emphasis


class UISchemaTests(unittest.TestCase):
    def test_hot_campaign_focuses_map_segments_and_actions(self) -> None:
        emphasis = default_emphasis(CycleStage.HOT_CAMPAIGN)
        self.assertGreaterEqual(emphasis.map_panel, 5)
        self.assertGreaterEqual(emphasis.segments_panel, 5)
        self.assertGreaterEqual(emphasis.bottom_actions, 5)
        self.assertLessEqual(emphasis.parliament, 2)


if __name__ == "__main__":
    unittest.main()
