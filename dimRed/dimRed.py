#!/usr/bin/python
# -*- coding: <UTF-8> -*-

"""
Functions for dimensionality reduction.
"""

from sklearn import manifold, decomposition
import umap

from dimRed import myTypes
import dimRed.settings.dimRedTypesSettings as dimRedTypesSettings

"""
Applies the given dimensionality reduction method to the given data.
"""
def dimensionReduction(Xs, method, settings, overrideDims=None):

    params = dimRedTypesSettings.getFirstElements(settings.params)
    dimensions = params["n_components"] if "n_components" in params else None

    dimensions = overrideDims if overrideDims else dimensions

    print("Dimensionality reduction: {}, {} dimensions...".format(method, dimensions))

    if len(Xs) == 0 or dimensions > len(Xs[0]):
        return Xs

    params["n_components"] = min(len(Xs), dimensions)

    if method == myTypes.DimRedMethod.PCA:
        embedding = decomposition.PCA(**params)
        X_embedded = embedding.fit_transform(Xs)

    elif method == myTypes.DimRedMethod.MDS:
        embedding = manifold.MDS(**params)
        X_embedded = embedding.fit_transform(Xs)

    elif method == myTypes.DimRedMethod.tSNE:
        if params["n_components"] >= params["perplexity"]:
            params["perplexity"] = params["n_components"] - 1
        X_embedded = manifold.TSNE(**params).fit_transform(Xs)

    elif method == myTypes.DimRedMethod.UMAP:
        embedding = umap.UMAP(**params)
        X_embedded = embedding.fit_transform(Xs)

    print("...dimensionality reduction finished")

    return X_embedded

"""
Trains the projection on the original data (Xs) but calculates the projection for interpolated samples as well (samples).
"""
def dimensionReductionForEmbedding(Xs, samples, method, settings, dimensions):
    print("TESTING")
    print("Dimensionality reduction for embedding: {}, {} dimensions...".format(method, dimensions))

    X_embedded = Xs

    params = dimRedTypesSettings.getFirstElements(settings.params)
    params["n_components"] = min(len(Xs), dimensions)

    if method == myTypes.DimRedMethod.PCA:
        embedding = decomposition.PCA(**params)
        embedding.fit(Xs)
        X_embedded = embedding.transform(samples)

    elif method == myTypes.DimRedMethod.UMAP:
        embedding = umap.UMAP(**params)
        trans = embedding.fit(Xs)
        X_embedded = trans.transform(samples)

    print("...dimensionality reduction for embedding finished")

    return X_embedded
