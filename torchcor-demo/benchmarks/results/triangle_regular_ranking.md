# Triangle regularity ranking (on-target methods)

## target_faces=50000
| rank | method | mean_q | q10 | runtime_sec | out_faces |
|---:|---|---:|---:|---:|---:|
| 1 | pyvista_decimatepro | 0.4948 | 0.1063 | 0.736 | 49994 |
| 2 | pymeshlab_qem | 0.3313 | 0.0626 | 8.046 | 49575 |

Selected for regularity at 50000: **pyvista_decimatepro**

## target_faces=100000
| rank | method | mean_q | q10 | runtime_sec | out_faces |
|---:|---|---:|---:|---:|---:|
| 1 | pymeshlab_qem | 0.6580 | 0.2308 | 7.529 | 99999 |
| 2 | pyvista_decimatepro | 0.5531 | 0.1357 | 0.907 | 99997 |

Selected for regularity at 100000: **pymeshlab_qem**
