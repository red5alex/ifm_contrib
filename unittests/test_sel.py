import unittest
import ifm_contrib as ifm
from ifm import Enum


class TestSel(unittest.TestCase):

    def test_sel_convert_2D(self):
        self.doc = ifm.loadDocument("./models/example_2D.fem")

        self.assertEqual(self.doc.c.sel.getSelectionType("conversiontest_el"), 1)
        self.assertEqual(self.doc.c.sel.getSelectionType("conversiontest_doesnotexist"), -1)

        # -> invalid is not possible
        self.assertRaises(ValueError,
                          self.doc.c.sel.convert,
                          "conversiontest_el", Enum.SEL_INVALID)

        # no conversion on equal types
        self.assertEqual(self.doc.c.sel.convert("conversiontest_el", Enum.SEL_ELEMENTAL),
                         [586, 955])
        self.assertEqual(self.doc.c.sel.convert("conversiontest_el", Enum.SEL_ELEMS),
                         [586, 955])

        # elemental -> nodal
        self.assertEqual(self.doc.c.sel.convert("conversiontest_el", Enum.SEL_NODAL),
                         [369, 370, 465, 467, 480])
        self.assertEqual(self.doc.c.sel.convert("conversiontest_el", Enum.SEL_NODES),
                         [369, 370, 465, 467, 480])

        # other not yet implemented
        with self.assertRaises(NotImplementedError):
            self.doc.c.sel.convert("conversiontest_el", Enum.SEL_FACES)
            self.doc.c.sel.convert("conversiontest_el", Enum.SEL_FRACS)
            self.doc.c.sel.convert("conversiontest_el", Enum.SEL_EDGES)

        self.doc.closeDocument()

    def test_sel_convert_3D(self):
        self.doc = ifm.loadDocument("./models/example_3D_mspecies.fem")

        self.assertEqual(self.doc.c.sel.getSelectionType("conversiontest_el"), 1)
        self.assertEqual(self.doc.c.sel.getSelectionType("conversiontest_doesnotexist"), -1)

        # -> invalid is not possible
        self.assertRaises(ValueError,
                          self.doc.c.sel.convert,
                          "conversiontest_el", Enum.SEL_INVALID)

        # no conversion on equal types
        self.assertEqual(self.doc.c.sel.convert("conversiontest_el", Enum.SEL_ELEMENTAL),
                         [718, 971])
        self.assertEqual(self.doc.c.sel.convert("conversiontest_el", Enum.SEL_ELEMS),
                         [718, 971])

        # elemental -> nodal
        self.assertEqual(self.doc.c.sel.convert("conversiontest_el", Enum.SEL_NODAL),
                         [455, 477, 478, 510, 523, 1040, 1062, 1063, 1095, 1108])
        self.assertEqual(self.doc.c.sel.convert("conversiontest_el", Enum.SEL_NODES),
                         [455, 477, 478, 510, 523, 1040, 1062, 1063, 1095, 1108])

        # other not yet implemented
        with self.assertRaises(NotImplementedError):
            self.doc.c.sel.convert("conversiontest_el", Enum.SEL_FACES)
            self.doc.c.sel.convert("conversiontest_el", Enum.SEL_FRACS)
            self.doc.c.sel.convert("conversiontest_el", Enum.SEL_EDGES)

        self.doc.closeDocument()


if __name__ == '__main__':
    unittest.main()
