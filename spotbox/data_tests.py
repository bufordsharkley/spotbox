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

if __name__ == '__main__':
    unittest.main()

