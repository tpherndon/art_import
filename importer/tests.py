from decimal import *

from django.test import TestCase

from importer.parser import conversion_factor, parse_size, parse_year


class ConversionFactorTest(TestCase):
    def test_size_in_inches(self):
        size = '40 x 25 in.'
        factor = conversion_factor(size)
        self.assertEqual(Decimal('2.54'), factor)

    def test_size_in_feet(self):
        size = '3.75 ft.'
        factor = conversion_factor(size)
        self.assertEqual(Decimal('12.0') * Decimal('2.54'), factor)

    def test_size_in_meters(self):
        size = '5 meters tall'
        factor = conversion_factor(size)
        self.assertEqual(Decimal('1000.0'), factor)

        size = '1 meter tall'
        factor = conversion_factor(size)
        self.assertEqual(Decimal('1000.0'), factor)

    def test_size_in_gallons(self):
        """
        Test of units not known to converter.
        """
        size = '5 gal. per deciliter'
        factor = conversion_factor(size)
        self.assertEqual(Decimal('1.0'), factor)

    def test_ambiguous_units(self):
        """
        Test where unit label occurs embedded in another word. Known to
        fail, need to switch conversion_factor to using regular expressions.
        """
        size_meter = '5 kilometers to go'
        factor = conversion_factor(size_meter)
        self.assertEqual(Decimal('1.0'), factor)

        size_centimeter = '5 centimeters long'
        factor = conversion_factor(size_centimeter)
        self.assertEqual(Decimal('1.0'), factor)

        size_within = 'a word within another'
        factor = conversion_factor(size_within)
        self.assertEqual(Decimal('1.0'), factor)

        size_bereft = 'we are bereft. Bereft, I tell you'
        factor = conversion_factor(size_bereft)
        self.assertEqual(Decimal('1.0'), factor)


class YearParserTest(TestCase):
    def test_single_year(self):
        year = '1956'
        parsed_year = parse_year(year)
        self.assertEqual((1956, 1956), parsed_year)

    def test_nd(self):
        year = 'nd'
        parsed_year = parse_year(year)
        self.assertEqual((1, 1), parsed_year)

    def test_circa(self):
        year = 'c.1953'
        parsed_year = parse_year(year)
        self.assertEqual((1953, 1953), parsed_year)

    def test_multiple_year(self):
        year = '2011-12'
        parsed_year = parse_year(year)
        self.assertEqual((2011, 2012), parsed_year)

        year = '2011-2012'
        parsed_year = parse_year(year)
        self.assertEqual((2011, 2012), parsed_year)

        year = 'c.1950-53'
        parsed_year = parse_year(year)
        self.assertEqual((1950, 1953), parsed_year)


class SizeParserTest(TestCase):
    """
    Test parse_size to make sure it captures dimensions properly. All sizes
    in centimeters, since we're not testing the conversion factor.
    """
    def test_no_size(self):
        size = ''
        parsed_size = parse_size(size)
        self.assertEqual((Decimal('0.0'), Decimal('0.0'), Decimal('0.0')),
                parsed_size)

    def test_single_dimension(self):
        size = '4.5 cm tall'
        parsed_size = parse_size(size)
        self.assertEqual((Decimal('0.0'), Decimal('4.5'), Decimal('0.0')),
                parsed_size)

    def test_range(self):
        size = '6-8 cm. tall'
        parsed_size = parse_size(size)
        self.assertEqual((Decimal('0.0'), Decimal('8.0'), Decimal('0.0')),
                parsed_size)

    def test_height_width(self):
        size = '40 x 25 cm tall'
        parsed_size = parse_size(size)
        self.assertEqual((Decimal('0.0'), Decimal('40.0'), Decimal('25.0')),
                parsed_size)

    def test_depth_height_width(self):
        size = '12 x 40 x 25 cm'
        parsed_size = parse_size(size)
        self.assertEqual((Decimal('12.0'), Decimal('40.0'), Decimal('25.0')),
                parsed_size)
