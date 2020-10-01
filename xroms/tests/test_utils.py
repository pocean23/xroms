"""Test utilities in xroms"""

import cartopy
import numpy as np
import xarray as xr

import xroms


grid = xr.open_dataset("xroms/tests/input/grid.nc")
ds = xroms.open_netcdf("xroms/tests/input/ocean_his_0001.nc")
# ds = xr.open_dataset('xroms/tests/input/ocean_his_0001.nc')
# combine the two:
ds = ds.merge(grid, overwrite_vars=True, compat="override")


def test_argsel2d():
    """Check that function returns correct indices.

    This compares with previous calculation."""

    lon0, lat0 = -95.8, 27.1
    assert xroms.argsel2d(ds.lon_rho, ds.lat_rho, lon0, lat0) == (0, 1)
    assert xroms.argsel2d(ds.lon_psi, ds.lat_psi, lon0, lat0) == (0, 0)
    assert xroms.argsel2d(ds.lon_u, ds.lat_u, lon0, lat0) == (0, 0)
    assert xroms.argsel2d(ds.lon_v, ds.lat_v, lon0, lat0) == (0, 1)
    assert xroms.argsel2d(ds.lon_vert, ds.lat_vert, lon0, lat0) == (1, 1)


def test_argsel2d_exact():
    """test for exact index."""

    lon0, lat0 = -95.928571, 27.166685  # one corner of grid
    assert xroms.argsel2d(ds.lon_rho, ds.lat_rho, lon0, lat0) == (0, 0)
    assert xroms.argsel2d(ds.lon_psi, ds.lat_psi, lon0, lat0) == (0, 0)
    assert xroms.argsel2d(ds.lon_u, ds.lat_u, lon0, lat0) == (1, 0)
    assert xroms.argsel2d(ds.lon_v, ds.lat_v, lon0, lat0) == (0, 0)
    assert xroms.argsel2d(ds.lon_vert, ds.lat_vert, lon0, lat0) == (1, 1)

    lon0, lat0 = -94.071429, 28.333351  # other corner of grid
    assert xroms.argsel2d(ds.lon_rho, ds.lat_rho, lon0, lat0) == (7, 13)
    assert xroms.argsel2d(ds.lon_psi, ds.lat_psi, lon0, lat0) == (7, 12)
    assert xroms.argsel2d(ds.lon_u, ds.lat_u, lon0, lat0) == (8, 12)
    assert xroms.argsel2d(ds.lon_v, ds.lat_v, lon0, lat0) == (7, 13)
    assert xroms.argsel2d(ds.lon_vert, ds.lat_vert, lon0, lat0) == (8, 13)


def test_sel2d():
    """Check that function returns correct value for scalar inputs."""

    lon0, lat0 = -94.8, 28.0

    assert (
        xroms.sel2d(ds.u, ds.lon_u, ds.lat_u, lon0, lat0).isel(s_rho=0, ocean_time=0)
        == 0.7
    )
    assert np.allclose(
        xroms.sel2d(ds.v, ds.lon_v, ds.lat_v, lon0, lat0).isel(s_rho=0, ocean_time=0),
        0.042857,
    )


# def test_sel2d_list():
#     '''Test sel2d for lon0/lat0 as list.'''

#     lon0, lat0 = [-95.7,-94.8], [27.4,28.0]

#     assert np.allclose(xroms.sel2d(ds.u, ds.lon_u, ds.lat_u, lon0, lat0).isel(s_rho=0, ocean_time=0), [0.1, 0.7])
#     assert np.allclose(xroms.sel2d(ds.v, ds.lon_v, ds.lat_v, lon0, lat0).isel(s_rho=0, ocean_time=0), [-0.071429,  0.042857])


def test_xisoslice():
    """Test xisoslice function."""

    # test longitude slice of u
    res = xroms.xisoslice(ds.lon_u, -95, ds.u, "xi_u")
    assert np.allclose(res, 0.6)

    # test latitude slice of u
    res = xroms.xisoslice(ds.lat_u, 28, ds.u, "eta_rho").std()
    assert np.allclose(res, 0.37416574)

    # test when slice isn't along a value that is equal along that slice
    # convert to projected space
    proj = cartopy.crs.LambertConformal(central_longitude=-98, central_latitude=30)
    pc = cartopy.crs.PlateCarree()
    x_u, y_u = proj.transform_points(pc, ds.lon_u.values, ds.lat_u.values)[..., :2].T
    ds["x_u"] = (("eta_u", "xi_u"), x_u.T)
    res = xroms.xisoslice(ds.x_u, 380000, ds.lon_u, "xi_u").mean()
    assert np.allclose(res, -94.19483976)

    # test getting latitude for longitude slice
    res = xroms.xisoslice(ds.lon_rho, -94.5, ds.lat_rho, "xi_rho").mean().values
    assert np.allclose(res, 27.75001934)

    # test requesting an exact iso_value that is in the iso_array, in xi_rho
    lon0 = ds.lon_rho[4, 7]
    res = xroms.xisoslice(ds.lon_rho, lon0, ds.lat_rho, "xi_rho")
    assert np.allclose(res, ds.lat_rho[:, 7])

    # test requesting an exact iso_value that is in the iso_array, in eta_rho
    lat0 = ds.lat_rho[3, 4]
    res = xroms.xisoslice(ds.lat_rho, lat0, ds.lon_rho, "eta_rho")
    assert np.allclose(res, ds.lon_rho[3, :])
