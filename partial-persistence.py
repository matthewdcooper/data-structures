"""

One way of improving the memory efficiency of the NaiveStack would be to recognise that:

[]
[1]
[1,2]
[1,2,3]

Holds the same information as:

[1, 2, 3]

(on the assumption that there have been no pops)

So rather than creating a new version for every push and every pop, we could create a new version only on pops,
since it is easy to see what the previous version of a stack that has been pushed to was.

This does mean that finding a particular version would no longer be a simple index look-up. You'd need
to iterate through each version until you found the right one.

Rather than storing a copy of each version, perhaps it would be more memory efficient to store
the sequence of update operations. And when a particular version is asked for, we could then
re-create that particular version from scratch? This would come at a cost for reading.
Each read would require all the update operations to be re-run first.

One solution to this might be to store a) the most recently accessed version r, and
b) the sequence of update operations, and c) to make sure all update operations are reversible.
Then, if we want to read from version v, rather than iterating through update operations
from 0 to v, we could find the 'fastest path' either forwards or backwards from r to v. 

A stack is readily reversible. The reverse of a push is a pop. And the reverse of a pop is to push its return value.
If we know the sequence of pushes and pops we can start at any point in that sequence and go back and forth in it.

Let's implement that as ReversibleStack.

"""

class NaiveStack:
    """ A partially persistent stack that makes no effort to save space or time. """
    def __init__(self):
        self.stacks = [[]]

    def push(self, value):
        new_stack = self.stacks[-1].copy()
        new_stack.append(value)
        self.stacks.append(new_stack)

    def pop(self):
        new_stack = self.stacks[-1].copy()
        value = new_stack.pop()
        self.stacks.append(new_stack)
        return value

    def read(self, version, index):
        return self.stacks[version][index]

    def show(self):
        for stack in self.stacks:
            print(stack)


class SequenceStack:
    """ A partially persistent stack that iterates through a subsequence of update operations
    to return a given version. Saves space but slows down read operations."""
    def __init__(self):
        self.sequence = [] # the complete sequence of pushes and pops

    def push(self, value):
        """Append a push operation to end of update sequence."""
        self.sequence.append(lambda stack: stack.append(value))

    def pop(self):
        """Append a pop operation to end of update sequence."""
        self.sequence.append(lambda stack: stack.pop())

    def read_version(self, version):
        """Return the stack as it was at version."""
        stack = []
        for update_operation in self.sequence[:version]:
            update_operation(stack)
        return stack

    def read(self, version, index):
        return self.read_version(version)[index]

    def show(self):
        """ Print all versions of the stack. """
        for v in range(len(self.sequence)):
            print("version {}: ".format(v), self.read_version(v))


class ReversibleSequenceStack:
    """ A partially persistent stack that stores the most recently read version and
    iterates either forwards or backwards through the sequence of update operations
    to return a requested version. This saves on space (although doubles the space
    requirements for storing update operations because we are saving both the original
    and its reverse), and tries to make up for the slow reading operation by reducing
    how many update operations must be applied to reach the desired version."""
    def __init__(self):
        self.sequence = [] # the complete sequence of pushes and pops
        self.stack = [] # most recently read version of the stack
        self.version = 0 # most recently read version

    def push(self, value):
        """Append a tuple of push and pop operation to end of update sequence."""
        # the second value of the tuple is the opposite and can be used to iterate backwards
        op = lambda stack: stack.append(value)
        rev_op = lambda stack: stack.pop()
        self.sequence.append((op, rev_op))

    def pop(self):
        """Append a tuple of pop and push operation to end of update sequence."""
        # the second value of the tuple is the opposite and can be used to iterate backwards
        value = self.read_version(len(self.sequence))[-1]
        op = lambda stack: stack.pop()
        rev_op = lambda stack: stack.append(value)
        self.sequence.append((op, rev_op))


    def read_version(self, version):
        """Return the stack as it was at version."""
        if version == self.version: return self.stack

        while self.version < version:
            update_operation = self.sequence[self.version][0]
            self.version += 1
            update_operation(self.stack)

        while self.version > version:
            update_operation = self.sequence[self.version-1][1]
            self.version -= 1
            update_operation(self.stack)

        return self.stack

    def read(self, version, index):
        return self.read_version(version)[index]


rs = ReversibleSequenceStack()
rs.push(1) 
rs.push(2)
rs.push(3)
rs.pop()
rs.pop()
rs.push(7)

for i in range(0, 7):
    print(i, rs.read_version(i))

for i in range(6, -1, -1):
    print(i, rs.read_version(i))
