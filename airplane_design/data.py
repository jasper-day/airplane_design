from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, \
Mapped, mapped_column
import math
from sqlalchemy.sql import select, insert
from typing import Optional, Dict
import json
from airfoil import parse_dir

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

engine = create_engine('sqlite:///../data/design.db')
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

def insert_airfoil(airfoil_data: Dict, session=session, commit=True):
    """
    Inserts an airfoil to the database
    """
    airfoil = Airfoil(
        title=airfoil_data["title"],
        filename=airfoil_data["filename"],
        extension=airfoil_data["extension"],
        path=airfoil_data["path"],
        coordinates=json.dumps(airfoil_data["coordinates"]),
        upper_planform=json.dumps(airfoil_data["upper_planform"]),
        lower_planform=json.dumps(airfoil_data["lower_planform"])
    )
    session.add(airfoil)
    if commit:
        session.commit()


def output_airfoil(airfoil: Airfoil):
    """
    Deserializes the airfoil information and returns a dict
    """
    airfoil_dict = {
        "title": airfoil.title,
        "filename": airfoil.filename,
        "extension": airfoil.extension,
        "path": airfoil.path,
        "coordinates": json.loads(airfoil.coordinates),
        "upper_planform": json.loads(airfoil.upper_planform),
        "lower_planform": json.loads(airfoil.lower_planform)
    }
    return airfoil_dict

def get_airfoils_by_re(re_pattern):
    matches = session.scalars(select(Airfoil).where(Airfoil.filename.regexp_match(re_pattern)))
    return matches.all()


if __name__ == "__main__":
    engine = create_engine('sqlite:///../data/design.db')
    Session = sessionmaker(bind=engine)
    with Session() as session:
        Base.metadata.create_all(engine)
        airfoils = parse_dir("/home/jasper/PARA/3_Resources/06_Airplanes/Airfoil_Coordinates")
        for airfoil in airfoils:
            insert_airfoil(airfoil, session=session, commit=False)
        session.commit()


