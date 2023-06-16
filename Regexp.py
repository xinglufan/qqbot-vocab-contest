import re


class Regexp:
    def __init__(self, rule: str, field=None):
        self.rule = rule
        self.field = field
        self.exp = re.compile(str(rule))

    def __repr__(self):
        return self.rule

    def findMap(self, content):
        content = str(content)
        match = self.exp.match(content)
        if match is None:
            return None
        dic = {}
        groups = match.groupdict()
        for k in groups:
            if groups[k] is not None:
                dic[k] = createValue(groups[k])
        return dic

    def isMatch(self, content):
        match = self.exp.findall(str(content))
        return len(match) > 0

    def isMatch2(self, content):
        match = self.exp.match(str(content))
        return match is not None


class Value:
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, Value):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return False

    def __hash__(self):
        return self.value.__hash__()

    def strip(self):
        return Value(self.value.strip())

    def toReg(self):
        return Regexp(self.value)

    def toInt(self) -> int:
        try:
            return int(self.value)
        except Exception:
            print("无法将[", self.value, "]转换为int")
        return 0

    def toFloat(self) -> float:
        try:
            return float(self.value)
        except Exception:
            print("无法将[", self.value, "]转换为float")
        return 0.

    def toFloatWithErr(self) -> float:
        return float(self.value)

    def toStr(self):
        return self.value

    def splitBySpace(self):
        splits = self.value.strip().split(" ")
        s = [s for s in splits if s != ""]
        return s


def createValue(value):
    if isinstance(value, str):
        return Value(value)
    elif isinstance(value, Value):
        return value
    else:
        print("创建Value错误, 不支持类型: {}".format(type(value)))
