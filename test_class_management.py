
# FitHub Class Management - Member 2 Testing
# These tests check if the class capacity function works correctly.

import unittest
from unittest.mock import patch, MagicMock

from class_capacity import check_class_capacity


class TestClassManagement(unittest.TestCase):

    # This helper creates a fake database connection.
    # We can test without changing real bookings.
    def make_database(self, capacity, bookings):
        connection = MagicMock()
        cursor = connection.cursor.return_value

        cursor.fetchone.side_effect = [
            (capacity,),
            (bookings,)
        ]

        return connection

    # Test 1: A class with free spaces should allow booking.
    @patch("class_capacity.get_connection")
    def test_class_has_space(self, mock_connection):
        mock_connection.return_value = self.make_database(20, 10)

        result = check_class_capacity(1, "2026-11-02")

        self.assertTrue(result)

    # Test 2: A full class should not allow booking.
    @patch("class_capacity.get_connection")
    def test_class_is_full(self, mock_connection):
        mock_connection.return_value = self.make_database(20, 20)

        result = check_class_capacity(1, "2026-11-02")

        self.assertFalse(result)

    # Test 3: A class with more bookings than capacity is full.
    @patch("class_capacity.get_connection")
    def test_overbooked_class(self, mock_connection):
        mock_connection.return_value = self.make_database(10, 12)

        result = check_class_capacity(2, "2026-11-03")

        self.assertFalse(result)

    # Test 4: Invalid class ID should give an error.
    @patch("class_capacity.get_connection")
    def test_class_not_found(self, mock_connection):
        connection = MagicMock()
        connection.cursor.return_value.fetchone.return_value = None
        mock_connection.return_value = connection

        with self.assertRaises(ValueError):
            check_class_capacity(999, "2026-11-02")

    # Test 5: Invalid date should give an error.
    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            check_class_capacity(1, "wrong-date")


if __name__ == "__main__":
    unittest.main()
