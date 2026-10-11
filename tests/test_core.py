import unittest

from xff_header_chain_parser import parse_xff_chain, InvalidHeaderError


class TestParseXffChain(unittest.TestCase):
    def test_single_ip(self):
        self.assertEqual(parse_xff_chain("203.0.113.1"), ["203.0.113.1"])

    def test_two_ips_preserves_order(self):
        self.assertEqual(
            parse_xff_chain("203.0.113.1, 198.51.100.7"),
            ["203.0.113.1", "198.51.100.7"],
        )

    def test_three_ips_preserves_order(self):
        self.assertEqual(
            parse_xff_chain("203.0.113.1, 198.51.100.7, 192.0.2.5"),
            ["203.0.113.1", "198.51.100.7", "192.0.2.5"],
        )

    def test_no_whitespace(self):
        self.assertEqual(
            parse_xff_chain("203.0.113.1,198.51.100.7"),
            ["203.0.113.1", "198.51.100.7"],
        )

    def test_extra_whitespace(self):
        self.assertEqual(
            parse_xff_chain("  203.0.113.1  ,   198.51.100.7  "),
            ["203.0.113.1", "198.51.100.7"],
        )

    def test_empty_string_returns_empty_list(self):
        self.assertEqual(parse_xff_chain(""), [])

    def test_whitespace_only_returns_empty_list(self):
        self.assertEqual(parse_xff_chain("   "), [])

    def test_stray_commas_dropped(self):
        self.assertEqual(
            parse_xff_chain("203.0.113.1,,198.51.100.7"),
            ["203.0.113.1", "198.51.100.7"],
        )

    def test_bare_comma_returns_empty_list(self):
        self.assertEqual(parse_xff_chain(","), [])

    def test_ipv6_preserved_verbatim(self):
        self.assertEqual(
            parse_xff_chain("2001:db8::1, 2001:db8::2"),
            ["2001:db8::1", "2001:db8::2"],
        )

    def test_port_suffix_preserved(self):
        self.assertEqual(
            parse_xff_chain("203.0.113.1:443, [2001:db8::1]:443"),
            ["203.0.113.1:443", "[2001:db8::1]:443"],
        )

    def test_none_rejected(self):
        with self.assertRaises(InvalidHeaderError):
            parse_xff_chain(None)

    def test_non_string_rejected(self):
        with self.assertRaises(InvalidHeaderError):
            parse_xff_chain(123)

    def test_invalid_header_error_is_value_error(self):
        self.assertTrue(issubclass(InvalidHeaderError, ValueError))


if __name__ == "__main__":
    unittest.main()
