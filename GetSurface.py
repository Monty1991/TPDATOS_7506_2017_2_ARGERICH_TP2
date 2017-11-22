import numpy as np

# ------------------------------------------------------------------------------
# IS FLOAT
# ------------------------------------------------------------------------------
def isFloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


# ------------------------------------------------------------------------------
# ENCONTRAR SUPERFICIE
# ------------------------------------------------------------------------------
def findSurface(words, i, surface):
    size = len(words)
    offset = 0
    iFound = False
    if isFloat(words[i]):
        if (i + 2 < size) and words[i+1].lower() == "x" and isFloat(words[i+2]):
            a = float(words[i])
            b = float(words[i+2])
            surface += a*b
            return surface, offset, iFound
    return surface, offset, iFound


# ------------------------------------------------------------------------------
# VALIDATE SURFACE
# ------------------------------------------------------------------------------
def validateSurface(surface, surfaceCalculated):
    if np.isnan(surface):
        return surfaceCalculated
    if surface != surfaceCalculated:
        return surface
    if surface == surfaceCalculated:
        return surface


# ------------------------------------------------------------------------------
# GET SURFACE
# ------------------------------------------------------------------------------
def getSurface(df):
    surfaces = df['surface_total_in_m2'].tolist()
    if 'description' not in df:
        return surfaces
    dfSize = len(df.index)
    descriptions = df['description'].tolist()
    for i in range(0, dfSize):
        if type(descriptions[i]) != type(""):
            validateSurface(surfaces[i], 0)
            continue
        surfaceCalculated = 0
        words = descriptions[i].split()
        wordsSize = len(words)
        for pos in range(0, wordsSize):
            triple = findSurface(words, pos, surfaceCalculated)
            surfaceCalculated, offset, iFound = triple
            if iFound:
                pos += offset
        surfaces[i] = validateSurface(surfaces[i], surfaceCalculated)
    return surfaces


# ------------------------------------------------------------------------------
# CREATE DICTIONARY SURFACES MEAN
# ------------------------------------------------------------------------------
def createDictionarySurfacesMean(df):
    df = df.loc[:, ['surface_total_in_m2', 'place_name']].groupby('place_name') \
        .agg([np.mean, np.size]).reset_index()
    surfacesMeanByPlace = df[('surface_total_in_m2', 'mean')].tolist()
    places = df['place_name'].tolist()
    size = len(surfacesMeanByPlace)
    surface = {}
    for i in range(0, size):
        surface[places[i]] = surfacesMeanByPlace[i]
    return surface


# ------------------------------------------------------------------------------
# VALIDATE SURFACES MEAN
# ------------------------------------------------------------------------------
def validateSufaceMean(df, surfaceMeanDicc, places):
    surfaces = df['surface_total_in_m2'].tolist()
    size = len(surfaces)
    for i in range(0, size):
        if surfaces[i] != 0:
            continue
        surfaceMean = surfaceMeanDicc[places[i]]
        if np.isnan(surfaceMean):
            continue
        surfaces[i] = surfaceMean
    df['surface_total_in_m2'] = surfaces
    return df
# ------------------------------------------------------------------------------

# Se debe usar en esta secuencia. i quereslee el codigo y entendelo,
# pero se usa asi

#df
#places = df['place_name'].tolist()
#surfaceMeanDicc = createDictionarySurfacesMean(df)
#df['surface_total_in_m2'] = getSurface(df)
#df = validateSufaceMean(df, surfaceMeanDicc, places)