import unittest
import ifm_contrib as ifm


class TestTs(unittest.TestCase):

    def test_info(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        doc.c.ts.info()

    def test_points(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        doc.c.ts.points(1)
        doc.c.ts.points(1111)

    def test_exists(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        self.assertRaises(TypeError, doc.c.ts.exists, None)
        self.assertEqual(True, doc.c.ts.exists(10))
        self.assertEqual(False, doc.c.ts.exists(0))
        self.assertEqual(False, doc.c.ts.exists(-1))
        self.assertEqual(False, doc.c.ts.exists(1111))


if __name__ == '__main__':
    unittest.main()
