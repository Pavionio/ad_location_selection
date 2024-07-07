import json
import os
from collections.abc import Generator
import random
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely import MultiPolygon
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon

PATH_TO_MARKS = 'marks.csv'
UPLOAD_FOLDER = ''


def get_all_markers_storage() -> pd.DataFrame:
    """Получение координат всех точек"""
    df = pd.read_csv(PATH_TO_MARKS)
    return df.apply(lambda row: {"lat": row['lat'], "lon": row['lon']}, axis=1)


def take_information_from_file_storage(file, filename: str, dr) -> bool:
    """ Дополнение файла точками, если охват для новых точек отсутствует, предсказание его с помощью модели """
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)
    df = pd.read_json(path)

    if "value" not in df.columns:
        df["value"] = dr.predict(df)

    df = pd.concat([df, pd.json_normalize(df['targetAudience'])], axis=1)
    df = df.explode('points').reset_index(drop=True)
    df = df.drop(['id', "hash", "targetAudience"], axis=1)
    df = pd.concat([df, pd.json_normalize(df['points'])], axis=1)
    df.drop("points", inplace=True, axis=1)

    new_marks = pd.concat([pd.read_csv(PATH_TO_MARKS), df])
    new_marks.to_csv(PATH_TO_MARKS, index=False)
    os.remove(path)

    return True


def geo_storage() -> str:
    """Выгрузка файла с координатами полигонов"""
    with open('mo.json', encoding='utf8') as f:
        j = json.load(f)
    return json.dumps(j, ensure_ascii=False)


def filter_storage(data: dict) -> dict:
    """Отбор точек, находящихся в выделеных полигонах"""
    params = data['params']
    df = pd.read_csv(PATH_TO_MARKS)

    gdf = gpd.GeoDataFrame(
        {'geometry': [(Polygon(i[0]) if len(i) == 1 else MultiPolygon(i)) for i in data['coordinates']],
         'id': range(len(data['coordinates']))})
    gdf = gdf.set_geometry("geometry")
    df['coords'] = list(zip(df['lon'], df['lat']))
    df['coords'] = df['coords'].apply(Point)
    points = gpd.GeoDataFrame(df, geometry='coords', crs=gdf.crs)
    pointInPolys = gpd.tools.sjoin(points, gdf, predicate="within", how='inner')

    return pointInPolys.apply(lambda row: {"lat": row['lat'], "lon": row['lon']}, axis=1)
