from measure_ast.tree_edit_distance import tree_edit_distance, tree_size


def leaf(label):
    return (label, ())


def node(label, *children):
    return (label, children)


# Zhang and Shasha's worked example: f(d(a, c(b)), e) against f(c(d(a, b)), e).
ZS_LEFT = node("f", node("d", leaf("a"), node("c", leaf("b"))), leaf("e"))
ZS_RIGHT = node("f", node("c", node("d", leaf("a"), leaf("b"))), leaf("e"))


def describe_tree_size():
    def it_counts_every_node():
        assert tree_size(ZS_LEFT) == 6

    def it_counts_a_lone_leaf_as_one():
        assert tree_size(leaf("a")) == 1


def describe_tree_edit_distance():
    def it_is_zero_for_identical_trees():
        assert tree_edit_distance(ZS_LEFT, ZS_LEFT) == 0

    def it_costs_one_to_relabel_a_node():
        assert tree_edit_distance(node("a", leaf("b")), node("a", leaf("c"))) == 1

    def it_costs_one_to_insert_a_leaf():
        assert tree_edit_distance(node("a", leaf("b")), node("a", leaf("b"), leaf("c"))) == 1

    def it_costs_one_to_delete_an_inner_node_and_keep_its_children():
        assert tree_edit_distance(node("a", node("x", leaf("b"), leaf("c"))), node("a", leaf("b"), leaf("c"))) == 1

    def it_matches_the_zhang_shasha_worked_example():
        assert tree_edit_distance(ZS_LEFT, ZS_RIGHT) == 2

    def it_is_symmetric():
        assert tree_edit_distance(ZS_RIGHT, ZS_LEFT) == 2

    def it_costs_the_whole_tree_against_a_single_unrelated_leaf():
        assert tree_edit_distance(ZS_LEFT, leaf("z")) == 6
