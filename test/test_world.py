import world
import unittest

class TorusStructureTest(unittest.TestCase):
    def setUp(self):
        self.w = 10
        self.h = 10
        self.cell_size = (5, 5)
        self.good_spot_frequency = 0.1
        self.torus_structure = world.TorusStructure(self.w, self.h, self.cell_size, self.good_spot_frequency)
        self.torus_structure_moore = world.TorusStructure(self.w, self.h,self.cell_size, self.good_spot_frequency, neighborhood_type="moore")
        self.torus_structure_von_neumann = world.TorusStructure(self.w, self.h, self.cell_size, self.good_spot_frequency, neighborhood_type="von_neumann")
        
    def test_absolute(self):
        self.assertEqual((1, 1), self.torus_structure._absolute(1, 1))
        self.assertEqual((self.w - 1, 1), self.torus_structure._absolute(-1, 1))
        self.assertEqual((0, 1), self.torus_structure._absolute(- self.w * 3, 1))
        self.assertEqual((1, self.h - 1), self.torus_structure._absolute(self.w + 1, -1))
        
    def test_coordinates(self):
        self.assertEqual(
            set([self.torus_structure._slots[x][y] for (x, y) in
            (1, 0), (9, 0), (0, 1), (0, 9), (1, 1), (1, 9), (9, 1), (9, 9), (1, 0), 
             (9, 0), (0, 2), (0, 8), (1, 2), (1, 8), (9, 2), (9, 8), (2, 0), (8, 0), 
             (0, 1), (0, 9), (2, 1), (2, 9), (8, 1), (8, 9), (2, 0), (8, 0), (0, 2), 
             (0, 8), (2, 2), (2, 8), (8, 2), (8, 8)]), 
            set(self.torus_structure.get_radius(10, (0, 0))))
        self.assertEqual(
            self.torus_structure.get_radius(11, (0, 0)), 
            self.torus_structure.get_radius(10, (0, 0)))
        self.assertEqual([], self.torus_structure.get_radius(0, (0, 0)))
        
if __name__ == "__main__":
    unittest.main()