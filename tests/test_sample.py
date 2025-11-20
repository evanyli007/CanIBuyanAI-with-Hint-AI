"""
Sample test file to verify repository functionality.
"""

import unittest


class TestSample(unittest.TestCase):
    """Sample test class to verify basic functionality."""
    
    def test_basic_assertion(self):
        """Test that basic assertions work."""
        self.assertTrue(True)
        self.assertEqual(1 + 1, 2)
        self.assertNotEqual("hello", "world")
    
    def test_string_operations(self):
        """Test basic string operations."""
        test_string = "CanIBuyanAI"
        self.assertIn("AI", test_string)
        self.assertEqual(len(test_string), 11)
        self.assertTrue(test_string.startswith("Can"))
    
    def test_list_operations(self):
        """Test basic list operations."""
        test_list = [1, 2, 3, 4, 5]
        self.assertEqual(len(test_list), 5)
        self.assertIn(3, test_list)
        self.assertEqual(sum(test_list), 15)


if __name__ == '__main__':
    unittest.main()