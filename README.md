# Stable Marriage of Poisson and Lebesgue

Python simulation of the stable allocation between a Poisson point process and Lebesgue measure, including support for **random appetites**.

This implementation follows the theoretical framework developed by Hoffman, Holroyd, and Peres for constant appetites, and its extension to random appetites by Díaz–Pachón.

## Features

- Interactive parameter input with explanations and suggested values
- Support for different appetite regimes:
  - Constant appetites
  - Exponentially distributed appetites
  - Uniformly distributed appetites
  - Voronoi tessellation (infinite appetite limit)
- Paper-style visualization with concentric stripes and per-territory colors
- Dynamic figure titles that reflect the chosen model
- High-resolution figure export (DPI control)
- Safe handling of subcritical, critical, and supercritical regimes

## Usage

1. Open the Jupyter notebook (`.ipynb`) or the Python script (`.py`).
2. Run the file. You will be prompted to enter the model and visualization parameters.
3. The script generates a high-resolution figure saved in the `artifacts/` folder.
4. The first five parameters are for model construction. The last three are for visualization of the generated figure.


### Main Parameters

| Parameter                 | Description                                  | Suggested Values                              |
|---------------------------|----------------------------------------------|-----------------------------------------------|
| `M`                       | Number of Poisson centers                    | 50 – 200                                      |
| `L`                       | Side length of the simulation box            | Usually `sqrt(M)`                             |
| `N`                       | Grid resolution                              | 200 – 500                                     |
| `APPETITE_TYPE`           | Type of appetite distribution                | constant / exponential                        |
| `APPETITE_MEAN`           | Mean appetite per center                     | 1.0 (critical), >1 (super)                    |
| `USE_STRIPED_TERRITORIES' | Y/N to draw stripes in the territories       | N for Voronoi tessellation or small appetites |
| `STRIPE_WIDTH`            | Width of concentric stripes in visualization | 0.10 – 0.20                                   |
| `DPI`                     | Resolution of the saved figure               | 300 (publication quality) , 600 (online)      |

The first five parameters are for model construction (in particular, the intensity of the point process is $\lambda=M/L^2$). 

The last three parameters are for visualization of the generated figure.

## Files

- `stable_marriage.ipynb` — Jupyter Notebook version (recommended for exploration)
- `stable_marriage.py` — Python script version (cleaner for version control)

## Acknowledgments

This simulation script was developed with assistance from **Grok**, an AI built by xAI.

## References

- Hoffman, C., Holroyd, A. E., & Peres, Y. (2006). A stable marriage of Poisson and Lebesgue. *Annals of Probability*, 34(4), 1241–1272.
- Hoffman, C., Holroyd, A. E., & Peres, Y. (2009). Tail bounds for the stable marriage of Poisson and Lebesgue. *Canadian Journal of Mathematics*, 61(6), 1279–1299. arXiv:0911.1429.
- Freire M. V., Popov S., & Vachkovskaia M. (2007). Percolation for the stable marriage of Poisson and Lebesgue. *Stochastic Processes and Their Applications*, 117(4), 514–525.
- Díaz–Pachón D. A. (2012). A note on large deviations for the stable marriage of Poisson and Lebesgue with random appetites. *Journal of Theoretical Probability*, 25(1), 77–91.
- Díaz–Pachón D. A. (2013). Percolation for the stable marriage of Poisson and Lebesgue with random appetites. *Stochastics*, 85(2), 252–261.
- Díaz–Pachón D. A. (2009). Algumas Propriedades de Alocaçoes para o processo pontual de Poisson. Doctoral Dissertation, *Instituto de Matemática e Estatística - Universidade de São Paulo*.

## Author

**Daniel Andrés Díaz-Pachón**  
Research Assistant Professor,  
Division of Biostatistics and Bioinformatics  
University of Miami
