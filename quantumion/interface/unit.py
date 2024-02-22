from typing import Union

import numpy as np

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
VoltageDimension = EnergyDimension / ChargeDimension
PowerDimension = EnergyDimension / TimeDimension
ForceDimension = MassDimension * LengthDimension / TimeDimension**2

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


########################################################################################

unitless = UnitBase(scale=1, dimension=Dimensionless)

deci = UnitBase(scale=1e-1, dimension=Dimensionless)
centi = UnitBase(scale=1e-2, dimension=Dimensionless)
milli = UnitBase(scale=1e-3, dimension=Dimensionless)
micro = UnitBase(scale=1e-6, dimension=Dimensionless)
nano = UnitBase(scale=1e-9, dimension=Dimensionless)
pico = UnitBase(scale=1e-12, dimension=Dimensionless)
femto = UnitBase(scale=1e-15, dimension=Dimensionless)
atto = UnitBase(scale=1e-18, dimension=Dimensionless)
zepto = UnitBase(scale=1e-21, dimension=Dimensionless)
yocto = UnitBase(scale=1e-24, dimension=Dimensionless)
ronto = UnitBase(scale=1e-27, dimension=Dimensionless)
quecto = UnitBase(scale=1e-30, dimension=Dimensionless)

deca = UnitBase(scale=1e1, dimension=Dimensionless)
hecto = UnitBase(scale=1e2, dimension=Dimensionless)
kilo = UnitBase(scale=1e3, dimension=Dimensionless)
mega = UnitBase(scale=1e6, dimension=Dimensionless)
giga = UnitBase(scale=1e9, dimension=Dimensionless)
tera = UnitBase(scale=1e12, dimension=Dimensionless)
peta = UnitBase(scale=1e15, dimension=Dimensionless)
exa = UnitBase(scale=1e18, dimension=Dimensionless)
zetta = UnitBase(scale=1e21, dimension=Dimensionless)
yotta = UnitBase(scale=1e24, dimension=Dimensionless)
ronna = UnitBase(scale=1e27, dimension=Dimensionless)
quetta = UnitBase(scale=1e30, dimension=Dimensionless)

pi = UnitBase(scale=np.pi, dimension=Dimensionless)

########################################################################################s

metre = UnitBase(scale=1, dimension=LengthDimension)
astronomicalunit = UnitBase(scale=1.495978707e11, dimension=LengthDimension)

second = UnitBase(scale=1, dimension=TimeDimension)
minute = UnitBase(scale=60, dimension=TimeDimension)
hour = UnitBase(scale=3600, dimension=TimeDimension)
day = UnitBase(scale=86400, dimension=TimeDimension)
year = UnitBase(scale=31557600, dimension=TimeDimension)

speedoflight = UnitBase(scale=299792458, dimension=VelocityDimension)

lightyear = speedoflight * year

########################################################################################

volt = UnitBase(scale=1, dimension=VoltageDimension)

gram = UnitBase(scale=1e-3, dimension=MassDimension)
atomicmassunit = UnitBase(scale=1.66053906660e-27, dimension=MassDimension)

joule = UnitBase(scale=1, dimension=EnergyDimension)
electronvolt = UnitBase(scale=1.602176634e-19, dimension=EnergyDimension)

watt = UnitBase(scale=1, dimension=PowerDimension)

newton = UnitBase(scale=1, dimension=ForceDimension)

########################################################################################

ampere = UnitBase(scale=1, dimension=CurrentDimension)

coulomb = UnitBase(scale=1, dimension=ChargeDimension)
elementarycharge = UnitBase(scale=1.602176634e-19, dimension=ChargeDimension)


########################################################################################

planckconstant = UnitBase(
    scale=6.62607015e-34, dimension=EnergyDimension * TimeDimension
)
reducedplanckconstant = planckconstant / (pi * 2)

boltzmannconstant = UnitBase(
    scale=1.380649e-23, dimension=EnergyDimension / TemperatureDimension
)

avogadroconstant = UnitBase(scale=6.02214076e23, dimension=SubstanceDimension ** (-1))

gravitationalconstant = UnitBase(
    scale=6.67430e-11, dimension=ForceDimension * LengthDimension**2 / MassDimension**2
)


plancklength = (reducedplanckconstant * gravitationalconstant / speedoflight**3) ** 0.5
plancktime = (reducedplanckconstant * gravitationalconstant / speedoflight**5) ** 0.5
planckmass = (reducedplanckconstant * speedoflight / gravitationalconstant) ** 0.5
plancktemperature = (
    reducedplanckconstant
    * speedoflight**5
    / (gravitationalconstant * boltzmannconstant**2)
) ** 0.5


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
    pass
