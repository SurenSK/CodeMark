import ast

class EqCompareTransform:
    @staticmethod
    def is_applicable(node):
        is_eq = isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq)
        is_not_neq = (isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not) and
                      isinstance(node.operand, ast.Compare) and len(node.operand.ops) == 1 and
                      isinstance(node.operand.ops[0], ast.NotEq))
        return is_eq or is_not_neq

    @staticmethod
    def get_bit(node):
        return 1 if isinstance(node, ast.UnaryOp) else 0

    @staticmethod
    def transform(node):
        if EqCompareTransform.get_bit(node):
            return node.operand
        else:
            new_compare = ast.Compare(left=node.left, ops=[ast.NotEq()], comparators=node.comparators)
            return ast.UnaryOp(op=ast.Not(), operand=new_compare)

class DeMorganTransform:
    @staticmethod
    def is_applicable(node):
        is_and = isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And)
        is_not_or_not = (isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not) and
                         isinstance(node.operand, ast.BoolOp) and isinstance(node.operand.op, ast.Or) and
                         all(isinstance(v, ast.UnaryOp) and isinstance(v.op, ast.Not) for v in node.operand.values))
        return is_and or is_not_or_not

    @staticmethod
    def get_bit(node):
        return 1 if isinstance(node, ast.UnaryOp) else 0

    @staticmethod
    def transform(node):
        if DeMorganTransform.get_bit(node):
            original_values = [v.operand for v in node.operand.values]
            return ast.BoolOp(op=ast.And(), values=original_values)
        else:
            negated_values = [ast.UnaryOp(op=ast.Not(), operand=v) for v in node.values]
            or_op = ast.BoolOp(op=ast.Or(), values=negated_values)
            return ast.UnaryOp(op=ast.Not(), operand=or_op)

TRANSFORMS = [EqCompareTransform, DeMorganTransform]

def get_ordered_sites(tree):
    sites = []
    for node in ast.walk(tree):
        for transform in TRANSFORMS:
            if transform.is_applicable(node):
                sites.append({'node': node, 'transform': transform})
                break
    return sites

class WatermarkTransformer(ast.NodeTransformer):
    def __init__(self, nodes_to_transform):
        self.nodes_to_transform = nodes_to_transform
    
    def visit(self, node):
        if id(node) in self.nodes_to_transform:
            transform = self.nodes_to_transform[id(node)]
            return transform.transform(node)
        return super().visit(node)


def encode(code, payload):
    tree = ast.parse(code)
    sites = get_ordered_sites(tree)
    nodes_to_transform = {}
    for i, site in enumerate(sites):
        node, transform = site['node'], site['transform']
        payload_bit = (payload >> i) & 1
        current_bit = transform.get_bit(node)
        if payload_bit != current_bit:
            nodes_to_transform[id(node)] = transform
    
    transformer = WatermarkTransformer(nodes_to_transform)
    new_tree = ast.fix_missing_locations(transformer.visit(tree))
    return ast.unparse(new_tree)

def decode(code, getMax=False):
    tree = ast.parse(code)
    sites = get_ordered_sites(tree)
    payload = 0
    for i, site in enumerate(sites):
        node, transform = site['node'], site['transform']
        bit = transform.get_bit(node)
        payload |= (bit << i)
    if getMax:
        return payload, (1 << len(sites)) - 1
    return payload
