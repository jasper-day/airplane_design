from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, \
Mapped, mapped_column
import math
from sqlalchemy.sql import select, insert
from sqlalchemy.dialects.sqlite import insert as upsert
from typing import Optional, Dict
import json

class Base(DeclarativeBase):
    pass

class Material(Base):
    __tablename__ = "materials"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    E_lower: Mapped[float]
    E_upper: Mapped[float]

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

def find_avg_E(E_lower, E_upper, session=session):
    target_materials = session.execute(select(Material.name, Material.E_lower, Material.E_upper)\
        .where(Material.E_lower.between(E_lower,E_upper))\
        .where(Material.E_upper.between(E_lower,E_upper))).all()
    for (name, E_lower, E_upper) in target_materials:
        #material = material[0]
        print(f"""Name: { name }
Average Young's Modulus: {(E_lower+E_upper)/2 }
""")

def get_materials_like(name):
    materials = session.scalars(select(Material)\
                                .where(Material.name.like(name))).all()
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
    engine = create_engine('sqlite:///../data/design.db')
    Session = sessionmaker(bind=engine)
    session = Session()
#    with Session() as session:
#        Base.metadata.create_all(engine)
#        airfoils = parse_dir("/home/jasper/PARA/3_Resources/06_Airplanes/Airfoil_Coordinates")
#        for airfoil in airfoils:
#            insert_airfoil(airfoil, session=session, commit=False)
#        session.commit()
