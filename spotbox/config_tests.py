import copy
import unittest

import mock

from spotbox import config

OK_CONFIG = {
    'who am i': 'kzsu',
    'spot count': 3,
    'media directory': '/tmp',
    'graphic': '/path/to/graphic.gif',
    'menus': [
        {
            'file format': 'PSA_field1_field2_field3.extension',
            'headers': [
                {
                    'field': 'field1',
                    'width': 37
                },
                {
                    'field': 'field2',
                    'width': 32
                },
                {
                    'field': 'field3',
                    'width': 21
                },
            ]
        },
        {
            'file format': 'PROMO_field4_field5.extension',
            'headers': [
                {
                    'field': 'field4',
                    'width': 37
                },
                {
                    'field': 'field5',
                    'width': 2
                },
            ]
        },
    ]
}



class ProcessTests(unittest.TestCase):

    def setUp(self):
        # some trivially valid config
        self.raw_config = copy.deepcopy(OK_CONFIG)

    def test_config_passes_back_processed_config(self):
        processed = config.process_raw_config(self.raw_config)
        self.assertIsInstance(processed, config.Config)

    def test_config_keeps_reference_to_media_directory(self):
        processed = config.process_raw_config(self.raw_config)
        self.assertEqual(processed.media_directory, '/tmp')

    def test_config_must_contain_media_directory(self):
        del self.raw_config['media directory']
        with self.assertRaises(KeyError):
            processed = config.process_raw_config(self.raw_config)

    def test_config_creates_file_config(self):
        # file config should be a dict for each spot type with a format
        processed = config.process_raw_config(self.raw_config)
        file_config = processed.file_config
        self.assertEqual(file_config,
                         {'PSA': 'PSA_field1_field2_field3.extension',
                          'PROMO': 'PROMO_field4_field5.extension'})

    def test_config_checks_entity(self):
        del self.raw_config['who am i']
        with self.assertRaises(KeyError):
            processed = config.process_raw_config(self.raw_config)

    def test_config_checks_spot_count(self):
        del self.raw_config['spot count']
        with self.assertRaises(KeyError):
            processed = config.process_raw_config(self.raw_config)

    def test_config_spot_count_is_correct(self):
        processed = config.process_raw_config(self.raw_config)
        self.assertEqual(processed.num_spots, 3)

    def test_config_creates_menu_config(self):
        processed = config.process_raw_config(self.raw_config)
        menu_config = processed.menu_config
        self.assertEqual(menu_config.headers,
                         {'PSA': [
                {
                    'field': 'field1',
                    'width': 37
                },
                {
                    'field': 'field2',
                    'width': 32
                },
                {
                    'field': 'field3',
                    'width': 21
                }],
                        'PROMO': [

                {
                    'field': 'field4',
                    'width': 37
                },
                {
                    'field': 'field5',
                    'width': 2
                }]})
        self.assertEqual(menu_config.order, ['PSA', 'PROMO'])

    def test_config_checks_for_graphic(self):
        del self.raw_config['graphic']
        with self.assertRaises(KeyError):
            processed = config.process_raw_config(self.raw_config)

    def test_graphic_correct(self):
        processed = config.process_raw_config(self.raw_config)
        self.assertEqual(processed.graphic, '/path/to/graphic.gif')

    @mock.patch('os.path.expanduser', autospec=True)
    def test_home_directory_paths_are_expanded(self, expand_mock):
        expand_mock.return_value = '/your/expanded/path'
        self.raw_config['graphic'] = '~/graphic'
        self.raw_config['media directory'] = '~/mediadir'
        processed = config.process_raw_config(self.raw_config)
        self.assertEqual(processed.graphic, '/your/expanded/path')
        self.assertEqual(processed.media_directory, '/your/expanded/path')



if __name__ == '__main__':
    unittest.main()
