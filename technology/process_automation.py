"""
A core primitive that was discovered is the ability to monitor child processes
from the parent process in python and guide it to a particular state by providing
input commands

"""

import pexpect
from typing import List
import sys
import enum

class NodeType(enum.Enum):
    INTERMEDIATE = 0
    SUCCESS = 1
    FAILURE = 2

class Node:

    def __init__(self,
                 children: list,
                 transitions: list,
                 expected_string: str,
                 type: NodeType):

        self.children = children
        self.transitions = transitions
        assert(len(self.children) == len(self.transitions))
        self.expected_string = expected_string
        self.type = type


class Graph:

    def __init__(self, node):
        self.node = node
        self.string_to_node = dict() # FIX: Initialize dict before dfs.
        self._dfs(node)

    def _dfs(self, node):

        if not (node in self.string_to_node):
            self.string_to_node[node.expected_string] = node
            for child in node.children:
                self._dfs(child)



def dfs_pathway(node):

    result = []

    def dfs(node, res):

        if node.type == NodeType.SUCCESS:
            nonlocal result
            result = res[:]
            return True

        for i, child in enumerate(node.children):
            transition = node.transitions[i]
            res.append(transition)
            path = dfs(child, res)
            if not path:
                res.pop()
            else:
                break

        return False

    dfs(node, [])

    return result

def process_automation(command: str,
                      graph: Graph,
                      ):
    """
    Spawns process provided by command, guides the process via inputs, searches
    for success strings to verify successful execution.

    """

    with open("logs.txt", "wb") as log_file:

        child = pexpect.spawn(command,
                              timeout=30,
                              maxread=2000,
                              searchwindowsize=None,
                              logfile=log_file,
                              cwd=None,
                              env=None)


        states = list(graph.string_to_node.keys()) + [pexpect.TIMEOUT, pexpect.EOF] # FIX: Cast keys dict to list.
        successful = None
        while True:
            index = child.expect(states)
            state = states[index]
            if state == pexpect.TIMEOUT:
                successful = False # ADD: If window times out, then we were not successful.
                break
            elif state == pexpect.EOF:
                child.close() # FIX: Close file after reaching end.
                successful = (child.exitstatus == 0) # If child process ends with no failures, then we were successful.
                break
            else:
                node = graph.string_to_node[state]
                if node.type == NodeType.INTERMEDIATE:
                    path = dfs_pathway(node)
                    transition = None
                    if path:
                        transition = path[0]
                    child.sendline(transition)
                elif node.type == NodeType.SUCCESS:
                    successful = True
                    break
                else:
                    successful = False
                    
    return successful # ADD: Let process_automation return if a process was successful or not