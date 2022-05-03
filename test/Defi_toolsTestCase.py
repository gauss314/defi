import unittest
import defi.defi_tools as dft

class Defi_toolsTestCase(unittest.TestCase):
    
    def test_geckoList(self):
        result = dft.geckoList()
        self.assertEqual(len(result.index), 250) #default por page
    
    def test_geckoListIds(self):
        result = dft.geckoList(ids="bitcoin,ethereum")
        self.assertEqual(len(result.index), 2)
        self.assertEqual(sorted(result['id'].tolist()), ["bitcoin", "ethereum"]) #alphabetically order
        
if __name__ == "__main__":
    unittest.main()