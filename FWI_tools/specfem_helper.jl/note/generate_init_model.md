# how to generate an initial gll model?

## overview

- calculate two modles with crust1.0+ak135. One with correct crust1.0 while another is not. we say these two models as ak135_bad and ak135_good.
- for Tao and Min's model, calculate corresponding ak135 model using ak135_bad.
- calculate per_tao and per_min, per_ak135_bad using ak135_bad.
- interp Tao and Min's models using ak135_bad.
  - per_ak135_bad +per_min -> per_ak135_bad_min
  - per_ak135_min +per_tao -> per_ak135_bad_min_tao
- smooth the perturbation per_ak135_bad_min_tao. (or not)
- use ak135_good to get the actual velocity model.

## structure

So the structure of this part should be:

cdw:

- model
  - tao_gll -> global model
  - min_gll -> global model
  - ak135_tao_gll -> cdw/specfem/tao/DATABASES_MPI
  - ak135_min_gll -> cdw/specfem/min/DATABASES_MPI
  - ak135_bad_gll -> cdw/specfem/ak135_bad/DATABASES_MPI
  - ak135_good_gll -> cdw/specfem/ak135_good/DATABASES_MPI
  - ak135_good_min_tao
  - ak135_good_min_tao_smooth
- control_file
  - ak135_bad -> cdw/specfem/ak135_bad/DATABASES_MPI
  - min -> cdw/specfem/min/DATABASES_MPI
  - tao -> cdw/specfem/tao/DATABASES_MPI
- perturbation -> cds/perturbation
  - per_tao
  - per_min
  - per_ak135_bad
  - per_ak135_bad_min
  - per_ak135_bad_min_tao
  - per_ak135_bad_min_tao_smooth
- specfem -> cds/specfem
  - tao
  - min
  - ak135_bad
  - ak135_good

cds:

- perturbation
  - per_tao
  - per_min
  - per_ak135_bad
  - per_ak135_bad_min
  - per_ak135_bad_min_tao
  - per_ak135_bad_min_tao_smooth
- specfem
  - tao (tao configuration+ak135/crust1.0+bad ak135)
  - min (min configuration+ak135/crust1.0+bad ak135)
  - ak135_bad (my configuration+ak135/crust1.0+bad ak135)
  - ak135_good (my configuration+ak135/crust1.0+bad ak135)

## use structure to set up the procedures:

1. in specfem, manually configure this four specfem dir.
2. use the code to generate the structure.
3. run all the specfem codes with flag mesh_out being turned on.
4. calculate the perturbation:
   - use tao_gll/ak135_tao_gll to get per_tao.
   - use min_gll/ak135_min_gll to get per_min.
   - use ak135_bad_gll/ak135_bad_gll to get per_ak135_bad.
5. perturbation:
   - per_ak135_bad +per_min -> per_ak135_bad_min
   - per_ak135_bad_min +per_tao -> per_ak135_bad_min_tao (the control file of per_ak135_bad_min is per_ak135_bad)
6. smooth:
   - use smoother to smooth per_ak135_bad_min_tao (the control file of per_ak135_bad_min is per_ak135_bad)
7. retrive:
   - use per_ak135_bad_min_tao\*ak135_good_gll to get ak135_good_min_tao.
   - use per_ak135_bad_min_tao_smooth\*ak135_good_gll to get ak135_good_min_tao_smooth.
