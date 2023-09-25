import unittest
import ifm_contrib as ifm


class TestTs(unittest.TestCase):

    def test_info(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        doc.c.ts.df.info()

    def test_points(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        doc.c.ts.df.points(10)


if __name__ == '__main__':
    unittest.main()
