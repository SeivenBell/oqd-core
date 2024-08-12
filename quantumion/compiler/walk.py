from quantumion.compiler.base import PassBase
from quantumion.compiler.rule import ConversionRule

########################################################################################


class Walk(PassBase):
    def __init__(self, rule: PassBase):
        super().__init__()

        self.rule = rule
        pass

    @property
    def children(self):
        return [self.rule]

    def map(self, model):
        return self.walk(model)

    def walk(self, model):
        for cls in model.__class__.__mro__:
            walk_func = getattr(self, "walk_{}".format(cls.__name__), None)
            if walk_func:
                break

        if not walk_func:
            walk_func = self.generic_walk

        return walk_func(model)

    def generic_walk(self, model):
        return self.rule(model)

    pass


########################################################################################


class Pre(Walk):
    """
    This class represents a the pre order tree traversal algorithm that walks through an AST
    and applies the rule from top to bottom.
    """

    def walk_dict(self, model):
        new_model = self.rule(model)

        new_model = {k: self(v) for k, v in new_model.items()}

        return new_model

    def walk_list(self, model):
        new_model = self.rule(model)

        new_model = [self(e) for e in new_model]

        return new_model

    def walk_tuple(self, model):
        new_model = self.rule(model)

        new_model = tuple([self(e) for e in new_model])

        return new_model

    def walk_VisitableBaseModel(self, model):
        new_model = self.rule(model)

        new_fields = {}
        for key in new_model.model_fields.keys():
            if key == "class_":
                continue
            new_fields[key] = self(getattr(new_model, key))
        new_model = new_model.__class__(**new_fields)

        return new_model


class Post(Walk):
    """
    This class represents a the post order tree traversal algorithm that walks through an AST
    and applies the rule from bottom to top.
    """

    def walk_dict(self, model):
        new_model = {k: self(v) for k, v in model.items()}

        if isinstance(self.rule, ConversionRule):
            self.rule.operands = new_model

        new_model = self.rule(new_model)
        return new_model

    def walk_list(self, model):
        new_model = [self(e) for e in model]

        if isinstance(self.rule, ConversionRule):
            self.rule.operands = new_model

        new_model = self.rule(new_model)

        return new_model

    def walk_tuple(self, model):
        new_model = tuple([self(e) for e in model])

        if isinstance(self.rule, ConversionRule):
            self.rule.operands = new_model

        new_model = self.rule(new_model)

        return new_model

    def walk_VisitableBaseModel(self, model):
        new_fields = {}
        for key in model.model_fields.keys():
            if key == "class_":
                continue
            new_fields[key] = self(getattr(model, key))

        if isinstance(self.rule, ConversionRule):
            self.rule.operands = new_fields
            new_model = self.rule(model)
        else:
            new_model = model.__class__(**new_fields)
            new_model = self.rule(new_model)

        return new_model


class Level(Walk):
    def __init__(self, rule):
        super().__init__(rule)

        self.stack = []
        self.initial = True

    def generic_walk(self, model):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.rule(self.stack.pop(0))
        if self.stack:
            self(self.stack[0])
        pass

    def walk_list(self, model):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.stack.extend(model)

        self.rule(self.stack.pop(0))
        if self.stack:
            self(self.stack[0])
        pass

    def walk_tuple(self, model):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.stack.extend(model)

        self.rule(self.stack.pop(0))
        if self.stack:
            self(self.stack[0])
        pass

    def walk_dict(self, model):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.stack.extend(model.values())

        self.rule(self.stack.pop(0))
        if self.stack:
            self(self.stack[0])
        pass

    def walk_VisitableBaseModel(self, model):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.stack.extend(
            [getattr(model, k) for k in model.model_fields.keys() if k != "class_"]
        )

        self.rule(self.stack.pop(0))
        if self.stack:
            self(self.stack[0])
        pass
