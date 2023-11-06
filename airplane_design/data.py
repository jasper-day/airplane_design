from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, \
Mapped, mapped_column
import math
from sqlalchemy.sql import select, insert
from sqlalchemy.dialects.sqlite import insert as upsert
from typing import Optional, Dict
import json

# multiply by this number to change to consistent units MKS
unit_table = {
    "GPa": 1e9,
    "MPa": 1e6,
    "kPa": 1e3,
    "Pa": 1,
    "g/cc": 1e3,
    "kg/m^3": 1,
}

class Base(DeclarativeBase):
    pass

class Material(Base):
    __tablename__ = "materials"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    youngs_mod: Mapped[Optional[float]]
    youngs_mod_unit: Mapped[Optional[str]]
    density: Mapped[Optional[float]]
    density_unit: Mapped[Optional[str]]
    yield_strength: Mapped[Optional[float]]
    yield_strength_unit: Mapped[Optional[str]]
    toughness: Mapped[Optional[float]]
    toughness_unit: Mapped[Optional[str]]
    def get_youngs_mod(self):
        try:
            return self.youngs_mod * unit_table[self.youngs_mod_unit]
        except:
            return None
    def get_density(self):
        try:
            return self.density * unit_table[self.density_unit]
        except:
            return None
    def get_yield_strength(self):
        try:
            return self.density * unit_table[self.yield_strength_unit]
        except:
            return None
    def get_toughness(self):
        try:
            return self.toughness * unit_table[self.toughness_unit]
        except:
            return None

class Airfoil(Base):
    __tablename__ = "airfoils"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[Optional[str]]
    filename: Mapped[str] = mapped_column(unique=True)
    path: Mapped[str]
    extension: Mapped[str]
    coordinates: Mapped[str] # json
    upper_planform: Mapped[str] # json
    lower_planform: Mapped[str] # json
    thickness: Mapped[float]
    camber_line: Mapped[str] # json

    def __init__(self, coordinates, upper_planform, lower_planform, camber_line, *args, **kwargs):
        self.coordinates = json.dumps(coordinates)
        self.upper_planform = json.dumps(coordinates)
        self.lower_planform = json.dumps(coordinates)
        self.camber_line = json.dumps(camber_line)
        super(Airfoil, self).__init__(*args, **kwargs)

    def deserialize(self):
        """
        Deserializes the airfoil information and returns a dict
        """
        airfoil_dict = {
            "title": self.title,
            "filename": self.filename,
            "extension": self.extension,
            "path": self.path,
            "coordinates": json.loads(self.coordinates),
            "upper_planform": json.loads(self.upper_planform),
            "lower_planform": json.loads(self.lower_planform),
            "thickness": self.thickness,
            "camber_line": json.loads(self.camber_line)
        }
        return airfoil_dict

# problems with relative path
# engine = create_engine('sqlite:///../data/design.db')
engine = create_engine('sqlite:///data/design.db')
Session = sessionmaker(bind=engine)
session = Session()

def get_materials_like(name):
    materials = session.scalars(select(Material)\
                                .where(Material.name.like(name + '%'))).all()
    return materials

def insert_airfoil(airfoil_data: Dict, session=session, commit=True):
    """
    Inserts an airfoil to the database
    """
    airfoil = Airfoil(**airfoil_data)
    session.add(airfoil)
    if commit:
        session.commit()

def insert_airfoils(airfoil_data, session=session):
    """
    Inserts a list of airfoils
    """
    for airfoil in airfoils:
        insert_airfoil(airfoil, session=session, commit=False)
        session.commit()


def get_airfoils_by_re(re_pattern):
    matches = session.scalars(select(Airfoil).where(Airfoil.filename.regexp_match(re_pattern)))
    return matches.all()


if __name__ == "__main__":
    from airfoil import parse_dir
    engine = create_engine('sqlite:///data/design.db')
    Session = sessionmaker(bind=engine)
    session = Session()
#    with Session() as session:
#        Base.metadata.create_all(engine)
#        airfoils = parse_dir("/home/jasper/PARA/3_Resources/06_Airplanes/Airfoil_Coordinates")
#        for airfoil in airfoils:
#            insert_airfoil(airfoil, session=session, commit=False)
#        session.commit()
