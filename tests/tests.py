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

def create_pip_graph():
    
    success = Node([],
                   [],
                   "INSTALL_SUCCESS",
                   NodeType.SUCCESS)

    failure = Node([],
                   [],
                   "INSTALL_FAILURE",
                   NodeType.FAILURE)

    verify_install = Node([success, failure],
                          ["verification_passed", "verification_failed"],
                          "VERIFY_INSTALL",
                          NodeType.INTERMEDIATE)

    install_packages = Node([verify_install],
                            ["pip3 install torch torchvision torchaudio"],
                            "INSTALL_PACKAGES",
                            NodeType.INTERMEDIATE)

    verify_pip = Node([install_packages],
                      ["verify pip3 exists"],
                      "VERIFY_PIP",
                      NodeType.INTERMEDIATE)

    return verify_pip

import unittest

class TestProcessAutomation(unittest.TestCase):

    def test_process_automation(self):
        
        head = create_graph()
        result = dfs_pathway(head)
        actual = ["transition_3", "transition_1"]
        self.assertTrue(result == actual)
        
    def test_torch_install_path(self):
        """
        Tests the expected DFS pathway.
        """

        graph = create_pip_graph()

        result = dfs_pathway(graph)

        expected = ["verify pip3 exists",
                    "pip3 install torch torchvision torchaudio",
                    "verification_passed"]

        self.assertEqual(result, expected)

    def test_torch_install(self):
        """
        Runs pip installation and verifies torch, torchvision,
        and torchaudio were installed successfully.
        """
        
        # Success nodes:
        
        already = Node([],
                       [],
                       "Requirement already satisfied",
                       NodeType.SUCCESS)

        installed = Node([],
                         [],
                         "Successfully installed",
                         NodeType.SUCCESS)
        
        # Failure nodes:
        
        no_space = Node([],
                        [],
                        "No space left on device",
                        NodeType.FAILURE)

        os_error = Node([],
                        [],
                        "Could not install packages due to an OSError",
                        NodeType.FAILURE)

        generic_error = Node([],
                             [],
                             "ERROR:",
                             NodeType.FAILURE)

        root = Node(
            [already,
             installed,
             no_space,
             os_error,
             generic_error,],
            ["", "", "", "", ""],
            "Collecting",
            NodeType.INTERMEDIATE)

        graph = Graph(root)

        result = process_automation("pip3 install torch torchvision torchaudio",
                                    graph)

        # Read logs.txt to check for successful installations:

        with open("logs.txt", "r", errors="ignore") as f:
            log = f.read()

        torch_installed = (
            "Requirement already satisfied: torch" in log or
            ("Successfully installed" in log and "torch" in log)
        )

        torchvision_installed = (
            "Requirement already satisfied: torchvision" in log or
            ("Successfully installed" in log and "torchvision" in log)
        )

        torchaudio_installed = (
            "Requirement already satisfied: torchaudio" in log or
            ("Successfully installed" in log and "torchaudio" in log)
        )
        
        # If installation fails, report reason for failure:
        
        if "No space left on device" in log:
            self.fail("Disk is full (No space left on device).")

        if "Could not install packages due to an OSError" in log:
            self.fail("pip encountered an operating system error.")

        if "ERROR:" in log:
            self.fail("pip reported an error.")

        self.assertTrue(result)
        self.assertTrue(torch_installed)
        self.assertTrue(torchvision_installed)
        self.assertTrue(torchaudio_installed)

if __name__ == '__main__':
    unittest.main()