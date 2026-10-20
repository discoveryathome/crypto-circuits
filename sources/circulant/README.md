Repo for "Utilizing Circulant Structure to Optimize the Implementations of Linear Layers"

### Data

Download data from https://gitee.com/Haotian-Shi/Quantum-circuits-of-aes-with-a-low-depth-linear-layer-and-a-new-structure (or https://github.com/rub-hgi/shorter_linear_slps_for_mds_matrices). The `matrices_bp_format` directory will be used.

### Compilation

```bash
g++ -std=c++20 circulant.cpp greedy.cpp reduce.cpp matrix.cpp -o circulant
g++ -std=c++20 circulant-post.cpp -o circulant-post
```

### Usage

Run `./circulant ./matrices_bp_format` to obtain implementation for linear layers. Search `! filename.start_with` to change the target linear layer. You can change `size_record` or `depth_record` to decide how results should be filtered. Store the result to a `.txt` file, e.g.

```
Joltik.txt 8 52 (6+2 36+16 id=1)
0 8 4 12 3 10 6 13 1 5 15 11 
13 9 7 3 1 8 4 11 12 15 5 0 6 2 14 10 
11 14 2 1 0 7 5 4 9 12 8 15 
9 8 4 7 10 13 3 6 
13 9 7 3 1 8 4 11 6 2 14 10 
0 12 4 8 2 9 7 14 1 5 15 11 
```

Run `./circulant-post ./raw/Joltik.txt ./matrices_bp_format` to get corresponding permutation, row operations and column operations.

### License

GPLv3, since it has GPLv3 component.
