from quantumion.compiler.base import PassBase
from quantumion.compiler.rule import ConversionRule
from quantumion.compiler.utils import controlled_reverse

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

    def __init__(self, rule, *, reverse=False):
        super().__init__(rule)
        self.reverse = reverse

    def walk_dict(self, model):
        new_model = self.rule(model)

        new_model = {
            k: self(v) for k, v in controlled_reverse(new_model.items(), self.reverse)
        }

        return {k: v for k, v in controlled_reverse(new_model.items(), self.reverse)}

    def walk_list(self, model):
        new_model = self.rule(model)

        new_model = [self(e) for e in controlled_reverse(new_model, self.reverse)]

        return controlled_reverse(new_model, self.reverse, restore_type=True)

    def walk_tuple(self, model):
        new_model = self.rule(model)

        new_model = tuple(
            [self(e) for e in controlled_reverse(new_model, self.reverse)]
        )

        return controlled_reverse(new_model, self.reverse, restore_type=True)

    def walk_VisitableBaseModel(self, model):
        new_model = self.rule(model)

        new_fields = {}
        for key in controlled_reverse(new_model.model_fields.keys(), self.reverse):
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

    def __init__(self, rule, *, reverse=False):
        super().__init__(rule)
        self.reverse = reverse

    def walk_dict(self, model):
        new_model = {
            k: self(v) for k, v in controlled_reverse(model.items(), self.reverse)
        }
        new_model = {
            k: v for k, v in controlled_reverse(new_model.items(), self.reverse)
        }

        if isinstance(self.rule, ConversionRule):
            self.rule.operands = new_model

        new_model = self.rule(new_model)

        return new_model

    def walk_list(self, model):
        new_model = [self(e) for e in controlled_reverse(model, self.reverse)]
        new_model = controlled_reverse(new_model, self.reverse, restore_type=True)

        if isinstance(self.rule, ConversionRule):
            self.rule.operands = new_model

        new_model = self.rule(new_model)
        return new_model

    def walk_tuple(self, model):
        new_model = tuple([self(e) for e in controlled_reverse(model, self.reverse)])
        new_model = controlled_reverse(new_model, self.reverse, restore_type=True)

        if isinstance(self.rule, ConversionRule):
            self.rule.operands = new_model

        new_model = self.rule(new_model)
        return new_model

    def walk_VisitableBaseModel(self, model):
        new_fields = {}
        for key in controlled_reverse(model.model_fields.keys(), self.reverse):
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
    """
    This class represents a the level/breadth first order tree traversal algorithm that walks through an AST.
    """

    def __init__(self, rule, *, reverse=False):
        super().__init__(rule)

        self.stack = []
        self.initial = True
        self.reverse = reverse

    def generic_walk(self, model):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.rule(self.stack.pop(0))
        if self.stack:
            self(self.stack[0])
        return model

    def walk_list(self, model):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.stack.extend(controlled_reverse(model, self.reverse))

        self.rule(self.stack.pop(0))
        if self.stack:
            self(self.stack[0])
        return model

    def walk_tuple(self, model):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.stack.extend(controlled_reverse(model, self.reverse))

        self.rule(self.stack.pop(0))
        if self.stack:
            self(self.stack[0])
        return model

    def walk_dict(self, model):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.stack.extend(controlled_reverse(model.values(), self.reverse))

        self.rule(self.stack.pop(0))
        if self.stack:
            self(self.stack[0])
        return model

    def walk_VisitableBaseModel(self, model):
        if self.initial:
            self.stack.append(model)
            self.initial = False

        self.stack.extend(
            controlled_reverse(
                [getattr(model, k) for k in model.model_fields.keys() if k != "class_"],
                self.reverse,
            )
        )

        self.rule(self.stack.pop(0))
        if self.stack:
            self(self.stack[0])
        return model


class In(Walk):
    """
    This class represents a the in order tree traversal algorithm that walks through an AST.
    """

    def __init__(self, rule, *, reverse=False):
        super().__init__(rule)
        self.reverse = reverse

    def generic_walk(self, model):
        self.rule(model)
        return model

    def walk_list(self, model):

        for e in model[:-1]:
            self(e)

        self.rule(model)
        self(model[-1])
        return model

    def walk_tuple(self, model):
        for e in model[:-1]:
            self(e)

        self.rule(model)
        self(model[-1])
        return model

    def walk_dict(self, model):
        for v in list(model.values())[:-1]:
            self(v)

        self.rule(model)
        self(list(model.values())[-1])
        return model

    def walk_VisitableBaseModel(self, model):
        for k in list(model.model_fields.keys())[:-1]:
            self(getattr(model, k))

        self.rule(model)
        self(getattr(model, list(model.model_fields.keys())[-1]))
        return model
