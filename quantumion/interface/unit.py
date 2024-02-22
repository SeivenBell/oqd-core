from typing import Union

########################################################################################

from quantumion.interface.base import TypeReflectBaseModel
from quantumion.interface.math import CastMathExpr

########################################################################################


class UnitDimensionBase(TypeReflectBaseModel):
    length: Union[int, float] = 0
    time: Union[int, float] = 0
    mass: Union[int, float] = 0
    current: Union[int, float] = 0
    temperature: Union[int, float] = 0
    luminosity: Union[int, float] = 0
    substance: Union[int, float] = 0
    pass

    def __mul__(self, other):
        assert isinstance(other, UnitDimensionBase)

        dimension_dict = {}
        for k in UnitDimensionBase.model_fields.keys():
            if k == "class_":
                continue
            else:
                dimension_dict[k] = self.__dict__[k] + other.__dict__[k]

        return UnitDimensionBase(**dimension_dict)

    def __truediv__(self, other):
        assert isinstance(other, UnitDimensionBase)

        dimension_dict = {}
        for k in UnitDimensionBase.model_fields.keys():
            if k == "class_":
                continue
            else:
                dimension_dict[k] = self.__dict__[k] - other.__dict__[k]

        return UnitDimensionBase(**dimension_dict)

    def __pow__(self, other):
        assert isinstance(other, (int, float))

        dimension_dict = {}
        for k in UnitDimensionBase.model_fields.keys():
            if k == "class_":
                continue
            else:
                dimension_dict[k] = self.__dict__[k] * other

        return UnitDimensionBase(**dimension_dict)


########################################################################################

Dimensionless = UnitDimensionBase()
LengthDimension = UnitDimensionBase(length=1)
TimeDimension = UnitDimensionBase(time=1)
MassDimension = UnitDimensionBase(mass=1)
CurrentDimension = UnitDimensionBase(current=1)
TemperatureDimension = UnitDimensionBase(temperature=1)
LuminosityDimension = UnitDimensionBase(luminosity=1)
SubstanceDimension = UnitDimensionBase(substance=1)

AreaDimension = LengthDimension**2
VolumeDimension = LengthDimension**3
VelocityDimension = LengthDimension / TimeDimension
AccelerationDimension = LengthDimension / TimeDimension**2
ChargeDimension = CurrentDimension * TimeDimension
EnergyDimension = MassDimension * LengthDimension**2 / TimeDimension**2
FrequencyDimension = TimeDimension ** (-1)

########################################################################################


class UnitBase(TypeReflectBaseModel):
    scale: float
    dimension: UnitDimensionBase = Dimensionless
    pass

    @classmethod
    def cast(cls, value):
        if isinstance(value, UnitBase):
            return value
        if isinstance(value, (int, float)):
            return UnitBase(scale=value)
        raise TypeError

    def __mul__(self, other):
        other = UnitBase.cast(other)
        return UnitBase(
            scale=self.scale * other.scale, dimension=self.dimension * other.dimension
        )

    def __truediv__(self, other):
        other = UnitBase.cast(other)
        return UnitBase(
            scale=self.scale / other.scale, dimension=self.dimension / other.dimension
        )

    def __pow__(self, other):
        assert isinstance(other, (int, float))
        return UnitBase(scale=self.scale**other, dimension=self.dimension**other)


unitless = UnitBase(scale=1, dimension=Dimensionless)

metre = UnitBase(scale=1, dimension=LengthDimension)
decimetre = UnitBase(scale=1e-1, dimension=LengthDimension)
centimetre = UnitBase(scale=1e-2, dimension=LengthDimension)
millimetre = UnitBase(scale=1e-3, dimension=LengthDimension)
micrometre = UnitBase(scale=1e-6, dimension=LengthDimension)
nanometre = UnitBase(scale=1e-9, dimension=LengthDimension)
picometre = UnitBase(scale=1e-12, dimension=LengthDimension)
femtometre = UnitBase(scale=1e-15, dimension=LengthDimension)
attometre = UnitBase(scale=1e-18, dimension=LengthDimension)
zeptometre = UnitBase(scale=1e-21, dimension=LengthDimension)
yactometre = UnitBase(scale=1e-24, dimension=LengthDimension)
kilometre = UnitBase(scale=1e3, dimension=LengthDimension)
megametre = UnitBase(scale=1e6, dimension=LengthDimension)
gigametre = UnitBase(scale=1e9, dimension=LengthDimension)
terametre = UnitBase(scale=1e12, dimension=LengthDimension)
petametre = UnitBase(scale=1e15, dimension=LengthDimension)
exametre = UnitBase(scale=1e18, dimension=LengthDimension)
zettametre = UnitBase(scale=1e21, dimension=LengthDimension)
yottametre = UnitBase(scale=1e24, dimension=LengthDimension)
ronnametre = UnitBase(scale=1e27, dimension=LengthDimension)


second = UnitBase(scale=1, dimension=TimeDimension)
decisecond = UnitBase(scale=1e-1, dimension=TimeDimension)
centisecond = UnitBase(scale=1e-2, dimension=TimeDimension)
millisecond = UnitBase(scale=1e-3, dimension=TimeDimension)
microsecond = UnitBase(scale=1e-6, dimension=TimeDimension)
nanosecond = UnitBase(scale=1e-9, dimension=TimeDimension)
picosecond = UnitBase(scale=1e-12, dimension=TimeDimension)
femtosecond = UnitBase(scale=1e-15, dimension=TimeDimension)
attosecond = UnitBase(scale=1e-18, dimension=TimeDimension)
zeptosecond = UnitBase(scale=1e-21, dimension=TimeDimension)
yactosecond = UnitBase(scale=1e-24, dimension=TimeDimension)
kilosecond = UnitBase(scale=1e3, dimension=TimeDimension)
megasecond = UnitBase(scale=1e6, dimension=TimeDimension)
gigasecond = UnitBase(scale=1e9, dimension=TimeDimension)
terasecond = UnitBase(scale=1e12, dimension=TimeDimension)
petasecond = UnitBase(scale=1e15, dimension=TimeDimension)
exasecond = UnitBase(scale=1e18, dimension=TimeDimension)
zettasecond = UnitBase(scale=1e21, dimension=TimeDimension)
yottasecond = UnitBase(scale=1e24, dimension=TimeDimension)
ronnasecond = UnitBase(scale=1e27, dimension=TimeDimension)
minute = UnitBase(scale=6e2, dimension=TimeDimension)
hour = UnitBase(scale=3.6e3, dimension=TimeDimension)

########################################################################################


class UnitfulMathExpr(TypeReflectBaseModel):
    expr: CastMathExpr
    unit: UnitBase = unitless

    def __add__(self, other):
        return UnitfulMathExpr(self.expr + other.expr, self.unit)

    def __sub__(self, other):
        return UnitfulMathExpr(self.expr - other.expr, self.unit)

    def __mul__(self, other):
        return UnitfulMathExpr(self.expr * other.expr, self.unit * other.unit)

    def __div__(self, other):
        return UnitfulMathExpr(self.expr / other.expr, self.unit / other.unit)


########################################################################################

if __name__ == "__main__":
    print(kilometre / hour)
