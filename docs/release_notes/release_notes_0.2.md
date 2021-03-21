## Gromax v0.2.0
### Features
* Gromacs 2021 is now supported. Note that support of advanced GPU options is not yet implemented,
  but any features that worked for Gromacs 2020 should work for Gromacs 2021.
* Reduced the default number of combinations generated. The default combinations
  should still come close to maximizing performance. Exhausive benchmark generation
  can still be requested using the `--generate_exhaustive_combinations` flag. 
  See [the examples doc](../examples.md) for more details.
### Compatibility
* Python 3.7 is now required.
  
