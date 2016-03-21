import copy
import unittest

from spotbox import data


class SplitTests(unittest.TestCase):

    def test_returns_components_of_filename(self):
        filename = '/some/path/okay_now_look_at_this.mp3'
        components = data.split_file_name(filename)
        self.assertEqual(components, ('okay', 'now', 'look', 'at', 'this'))

    def test_returns_components_of_filename_even_if_no_extension(self):
        filename = '/some/path/okay_now_look_at_this'
        components = data.split_file_name(filename)
        self.assertEqual(components, ('okay', 'now', 'look', 'at', 'this'))

    def test_can_combine_format_with_filename(self):
        filename = 'LID_some kinda title_some description_0.34.wav'
        format = ('key', 'title', 'description', 'time')
        resp = data.merge_file_and_format(filename, format)
        self.assertEqual(resp,
            {'key': 'LID', 'title': 'some kinda title',
             'description': 'some description', 'time': '0.34'})

    def test_is_forgiving_if_fields_missing(self):
        filename = 'LID_some kinda title_some description.wav'
        format = ('key', 'title', 'description', 'time')
        resp = data.merge_file_and_format(filename, format)
        self.assertEqual(resp,
            {'key': 'LID', 'title': 'some kinda title',
             'description': 'some description', 'time': ''})

    def test_can_preserve_slashes_if_wished(self):
        # If it's not a path (i.e. a format) you may want to keep slashes:
        filename = 'LID_i_can/trust_slashes.bip'
        components = data.split_file_name(filename, keep_slash=True)
        self.assertEqual(components, ('LID', 'i', 'can/trust', 'slashes'))



FILE_CONFIG = {'LID': 'LID_boom_bap.extension',
               'PROMO': 'PROMO_who_what_where.extension'}


class SpotTests(unittest.TestCase):

    def setUp(self):
        self.config = copy.deepcopy(FILE_CONFIG)

    def test_spot_raises_if_not_in_config(self):
        path = 'UNKNOWN_fields_fields.mp3'
        with self.assertRaises(ValueError):
            spot = data.Spot(path, self.config)

    def test_spot_resolves_if_correct(self):
        path = 'LID_hello_there.mp3'
        spot = data.Spot(path, self.config)
        self.assertEqual(spot.info, {'boom': 'hello', 'bap': 'there'})
        self.assertEqual(spot.type, 'LID')
        self.assertEqual(spot.path, path)

    def test_spot_resolves_even_if_slash_in_format(self):
        path = 'LID_hello_there.mp3'
        self.config['LID'] = 'LID_boom/boom_bap.extension'
        spot = data.Spot(path, self.config)
        self.assertEqual(spot.info, {'boom/boom': 'hello', 'bap': 'there'})


if __name__ == '__main__':
    unittest.main()

