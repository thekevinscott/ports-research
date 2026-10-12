"""Zhang-Shasha ordered tree edit distance, unit cost for insert, delete and relabel."""

type LabelTree = tuple[str, tuple[LabelTree, ...]]


def tree_size(tree: LabelTree) -> int:
    return 1 + sum(tree_size(child) for child in tree[1])


def postorder(tree: LabelTree) -> tuple[list[str], list[int], list[int]]:
    """Labels in postorder, each node's leftmost leaf index, and the keyroots in increasing order."""
    labels: list[str] = []
    leftmost: list[int] = []

    def visit(node: LabelTree) -> int:
        leaves = [visit(child) for child in node[1]]
        leftmost.append(leaves[0] if leaves else len(labels))
        labels.append(node[0])
        return leftmost[-1]

    visit(tree)
    return labels, leftmost, keyroots(leftmost)


def keyroots(leftmost: list[int]) -> list[int]:
    highest = {}
    for i, leaf in enumerate(leftmost):
        highest[leaf] = i
    return sorted(highest.values())


def tree_edit_distance(a: LabelTree, b: LabelTree) -> int:
    a_labels, a_left, a_keyroots = postorder(a)
    b_labels, b_left, b_keyroots = postorder(b)
    trees = [[0] * len(b_labels) for _ in a_labels]
    for i in a_keyroots:
        for j in b_keyroots:
            forest_distance(i, j, a_labels, a_left, b_labels, b_left, trees)
    return trees[-1][-1]


def forest_distance(i, j, a_labels, a_left, b_labels, b_left, trees) -> None:
    li, lj = a_left[i], b_left[j]
    rows, columns = i - li + 2, j - lj + 2
    forest = [[0] * columns for _ in range(rows)]
    for x in range(1, rows):
        forest[x][0] = x
    for y in range(1, columns):
        forest[0][y] = y
    for x in range(1, rows):
        ai = li + x - 1
        for y in range(1, columns):
            bj = lj + y - 1
            if a_left[ai] == li and b_left[bj] == lj:
                relabel = forest[x - 1][y - 1] + (a_labels[ai] != b_labels[bj])
                forest[x][y] = min(forest[x - 1][y] + 1, forest[x][y - 1] + 1, relabel)
                trees[ai][bj] = forest[x][y]
            else:
                subtree = forest[a_left[ai] - li][b_left[bj] - lj] + trees[ai][bj]
                forest[x][y] = min(forest[x - 1][y] + 1, forest[x][y - 1] + 1, subtree)
