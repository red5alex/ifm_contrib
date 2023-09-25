import unittest
import ifm_contrib as ifm

class TestMesh(unittest.TestCase):

    def test_show_available_aux(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        doc.c.mesh.available_aux()

    def test_get_imatrix(self):
        doc =  ifm.loadDocument("./models/example_2D.fem")
        self.assertEqual(len(doc.c.mesh.get_imatrix()), 959)
        self.assertEqual(len(doc.c.mesh.get_imatrix(ignore_inactive=True)), 904)
        self.assertEqual(len(doc.c.mesh.get_imatrix(split_quads_to_triangles=True)), 1088)
        self.assertEqual(len(doc.c.mesh.get_imatrix(ignore_inactive=True, split_quads_to_triangles=True)), 1088 - 55)

        ee = doc.c.mesh.get_imatrix(ignore_inactive=True, return_elements=True)
        self.assertEqual(ee[1], [e for e in range(doc.getNumberOfElements()) if doc.getMatElementActive(e)])

        with self.assertRaises(ValueError):
            doc.c.mesh.get_imatrix(layer=-1)
            doc.c.mesh.get_imatrix(layer=2)

        doc =  ifm.loadDocument("./models/example_3D_mspecies.fem")
        self.assertEqual(len(doc.c.mesh.get_imatrix()), 1960)
        self.assertEqual(len(doc.c.mesh.get_imatrix(ignore_inactive=True)), 1787)
        self.assertEqual(len(doc.c.mesh.get_imatrix(split_quads_to_triangles=True)), 2176)
        self.assertEqual(len(doc.c.mesh.get_imatrix(ignore_inactive=True, split_quads_to_triangles=True)), 1976)

        self.assertEqual(len(doc.c.mesh.get_imatrix(layer=1)), 980)
        self.assertEqual(len(doc.c.mesh.get_imatrix(layer=2)), 980)
        self.assertEqual(len(doc.c.mesh.get_imatrix(layer=1, ignore_inactive=True)), 807)
        self.assertEqual(len(doc.c.mesh.get_imatrix(layer=2, ignore_inactive=True)), 980)
        self.assertEqual(len(doc.c.mesh.get_imatrix(layer=1, split_quads_to_triangles=True)), 980 + 108)
        self.assertEqual(len(doc.c.mesh.get_imatrix(layer=2, split_quads_to_triangles=True)), 980 + 108)
        self.assertEqual(len(doc.c.mesh.get_imatrix(layer=1, ignore_inactive=True, split_quads_to_triangles=True)), 807 + 81)
        self.assertEqual(len(doc.c.mesh.get_imatrix(layer=2, ignore_inactive=True, split_quads_to_triangles=True)), 980 + 108)

        ee = doc.c.mesh.get_imatrix(ignore_inactive=True, return_elements=True)
        self.assertEqual(ee[1], [e for e in range(doc.getNumberOfElements()) if doc.getMatElementActive(e)])

        with self.assertRaises(ValueError):
            doc.c.mesh.get_imatrix(layer=-1)
            doc.c.mesh.get_imatrix(layer=3)


    def test_get_imatrix2d(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        self.assertEqual(len(doc.c.mesh.get_imatrix2d()), 959)
        self.assertEqual(len(doc.c.mesh.get_imatrix2d(ignore_inactive=True)), 904)
        self.assertEqual(len(doc.c.mesh.get_imatrix2d(split_quads_to_triangles=True)), 1088)
        self.assertEqual(len(doc.c.mesh.get_imatrix2d(ignore_inactive=True, split_quads_to_triangles=True)), 1088 - 55)

        ee = doc.c.mesh.get_imatrix2d(ignore_inactive=True, return_elements=True)
        self.assertEqual(ee[1], [e for e in range(doc.getNumberOfElements()) if doc.getMatElementActive(e)])

        doc = ifm.loadDocument("./models/example_3D_mspecies.fem")
        self.assertEqual(len(doc.c.mesh.get_imatrix2d(slice=1)), 980)
        self.assertEqual(len(doc.c.mesh.get_imatrix2d(slice=2)), 980)
        self.assertEqual(len(doc.c.mesh.get_imatrix2d(slice=3)), 980)
        self.assertEqual(len(doc.c.mesh.get_imatrix2d(slice=1, ignore_inactive=True)), 807)
        self.assertEqual(len(doc.c.mesh.get_imatrix2d(slice=2, ignore_inactive=True)), 980)
        self.assertEqual(len(doc.c.mesh.get_imatrix2d(slice=1, split_quads_to_triangles=True)), 980 + 108)
        self.assertEqual(len(doc.c.mesh.get_imatrix2d(slice=2, split_quads_to_triangles=True)), 980 + 108)
        self.assertEqual(len(doc.c.mesh.get_imatrix2d(slice=1, ignore_inactive=True, split_quads_to_triangles=True)), 807 + 81)
        self.assertEqual(len(doc.c.mesh.get_imatrix2d(slice=2, ignore_inactive=True, split_quads_to_triangles=True)), 980 + 108)

        ee = doc.c.mesh.get_imatrix2d(ignore_inactive=True, return_elements=True)
        self.assertEqual(ee[1], [e for e in range(doc.getNumberOfElementsPerLayer()) if doc.getMatElementActive(e)])

        with self.assertRaises(ValueError):
            doc.c.mesh.get_imatrix2d(slice=4)

    def test_getCentroid(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        doc.c.mesh.getCentroid(0)

    def test_mlw(self):
        doc = ifm.loadDocument("./models/example_3D_mspecies.fem")
        doc.c.mesh.mlw()


if __name__ == '__main__':
    unittest.main()