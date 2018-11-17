import unittest
import ifm_contrib as ifm

class TestMesh(unittest.TestCase):

    def test_get_imatrix(self):
        doc =  ifm.loadDocument("./models/example_2D.fem")
        self.assertEqual(len(doc.c.mesh.get_imatrix()), 959)
        self.assertEqual(len(doc.c.mesh.get_imatrix(ignore_inactive=True)), 904)
        self.assertEqual(len(doc.c.mesh.get_imatrix(split_quads_to_triangles=True)), 1088)
        self.assertEqual(len(doc.c.mesh.get_imatrix(ignore_inactive=True, split_quads_to_triangles=True)), 1088 - 55)

        doc =  ifm.loadDocument("./models/example_3D_mspecies.fem")
        self.assertEqual(len(doc.c.mesh.get_imatrix()), 1960)
        self.assertEqual(len(doc.c.mesh.get_imatrix(ignore_inactive=True)), 1787)
        self.assertEqual(len(doc.c.mesh.get_imatrix(split_quads_to_triangles=True)), 2176)
        self.assertEqual(len(doc.c.mesh.get_imatrix(ignore_inactive=True, split_quads_to_triangles=True)), 1976)

if __name__ == '__main__':
    unittest.main()