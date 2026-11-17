import unittest

from visionx.alerts import AlertManager


def detection(name, area, confidence=0.90, position="near the center"):
    return {
        "name": name,
        "position": position,
        "confidence": confidence,
        "area_ratio": area,
    }


class TestAlertManager(unittest.TestCase):

    def test_vehicle_beats_larger_cellphone(self):
        manager = AlertManager(cooldown=0)

        message = manager.choose_alert(
            [
                detection("cell phone", 0.40),
                detection("car", 0.05),
            ],
            now=100,
        )

        self.assertEqual(message, "Vehicle detected near the center")

    def test_larger_object_wins_same_priority(self):
        manager = AlertManager(cooldown=0)

        message = manager.choose_alert(
            [
                detection("person", 0.05),
                detection("person", 0.25, position="on the left"),
            ],
            now=100,
        )

        self.assertEqual(message, "person detected on your left")

    def test_low_confidence_is_ignored(self):
        manager = AlertManager(cooldown=0)

        message = manager.choose_alert(
            [
                detection("car", 0.30, confidence=0.20),
            ],
            now=100,
        )

        self.assertIsNone(message)

    def test_same_object_is_not_repeated(self):
        manager = AlertManager(cooldown=0)

        car = detection("car", 0.15)

        first = manager.choose_alert([car], now=100)
        second = manager.choose_alert([car], now=101)

        self.assertIsNotNone(first)
        self.assertIsNone(second)

    def test_object_can_be_announced_after_disappearing(self):
        manager = AlertManager(
            cooldown=0,
            forget_after=2.0,
        )

        car = detection("car", 0.15)

        first = manager.choose_alert([car], now=100)
        manager.choose_alert([], now=103)
        second = manager.choose_alert([car], now=104)

        self.assertIsNotNone(first)
        self.assertIsNotNone(second)


if __name__ == "__main__":
    unittest.main(verbosity=2)
