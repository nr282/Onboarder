"""
Tests the automation of various installation processes, including verification etc.



"""

from technology.process_automation import process_automation, Node, Graph, NodeType, dfs_pathway
import unittest

def create_graph():


    node_1 = Node([],
                  [],
                  "SUCCESS_1",
                  NodeType.SUCCESS)

    node_2 = Node([],
                  [],
                  "FAILURE_2",
                  NodeType.FAILURE)

    node_3 = Node([node_1, node_2],
                  ["transition_1", "transition_2"],
                  "INTERMEDIATE_3",
                  NodeType.INTERMEDIATE)

    node_4 = Node([node_3],
                  ["transition_3"],
                  "INTERMEDIATE_4",
                  NodeType.INTERMEDIATE)


    return node_4

import unittest

class TestProcessAutomation(unittest.TestCase):

    def test_process_automation(self):


        head = create_graph()
        result = dfs_pathway(head)
        actual = ["transition_3", "transition_1"]
        self.assertTrue(result == actual)




if __name__ == '__main__':
    unittest.main()




