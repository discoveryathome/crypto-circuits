#include <bits/stdc++.h>

typedef struct {
  int src;
  int dst;
  int type;
} Op;

template <typename T>
using Matrix = std::vector<std::vector<T>>;

Matrix<int> read_matrix(std::istream &is) {
  int n, x, y;
  is >> n;
  assert(n == 1);
  is >> x >> y;
  Matrix<int> matrix(x, std::vector<int>(y, 0));
  for (int i = 0; i < x; i++) {
    for (int j = 0; j < y; j++) {
      is >> matrix[i][j];
    }
  }
  return matrix;
}

void process_id(Matrix<int> &matrix, int block_size, int id) {
  int n = matrix.size();
  if (n / block_size != 2 && n / block_size != 4) {
    for (int step = n / 2; step >= block_size; step /= 2) {
      for (int i = 0; i < n / 2 / step; i++) {
        for (int j = 0; j < step; j++) {
          for (int k = 0; k < n; k++) {
            matrix[i * step * 2 + j + step][k] ^= matrix[i * step * 2 + j][k];
          }
        }
      }
      for (int i = 0; i < n / 2 / step; i++) {
        for (int j = 0; j < step; j++) {
          for (int k = 0; k < n; k++) {
            matrix[k][i * step * 2 + j] ^= matrix[k][i * step * 2 + j + step];
          }
        }
      }
    }
    return;
  } else {
    if (n / block_size == 4) {
      int super_id = id / 1000;
      id = id % 1000;
      if (super_id & 0x2) {
        for (int j = 0; j < n / 2; j++) {
          for (int k = 0; k < n; k++) {
            matrix[j + n / 2][k] ^= matrix[j][k];
          }
        }
      } else {
        for (int j = 0; j < n / 2; j++) {
          for (int k = 0; k < n; k++) {
            matrix[j][k] ^= matrix[j + n / 2][k];
          }
        }
      }
      if (super_id & 0x1) {
        for (int j = 0; j < n / 2; j++) {
          for (int k = 0; k < n; k++) {
            matrix[k][j + n / 2] ^= matrix[k][j];
          }
        }
      } else {
        for (int j = 0; j < n / 2; j++) {
          for (int k = 0; k < n; k++) {
            matrix[k][j] ^= matrix[k][j + n / 2];
          }
        }
      }
    }
    int step = block_size;
    {
      for (int i = 0; i < n / 2 / step; i++) {
        if (id & (1 << (n / step - 1 - i))) {
          for (int j = 0; j < step; j++) {
            for (int k = 0; k < n; k++) {
              matrix[i * step * 2 + j + step][k] ^= matrix[i * step * 2 + j][k];
            }
          }
        } else {
          for (int j = 0; j < step; j++) {
            for (int k = 0; k < n; k++) {
              matrix[i * step * 2 + j][k] ^= matrix[i * step * 2 + j + step][k];
            }
          }
        }
      }
    }
    {
      for (int i = 0; i < n / 2 / step; i++) {
        if (id & (1 << (n / step / 2 - 1 - i))) {
          for (int j = 0; j < step; j++) {
            for (int k = 0; k < n; k++) {
              matrix[k][i * step * 2 + j + step] ^= matrix[k][i * step * 2 + j];
            }
          }
        } else {
          for (int j = 0; j < step; j++) {
            for (int k = 0; k < n; k++) {
              matrix[k][i * step * 2 + j] ^= matrix[k][i * step * 2 + j + step];
            }
          }
        }
      }
    }
  }
}

std::pair<std::vector<std::vector<Op>>, std::vector<std::vector<Op>>>
id_to_circuit(int n, int block_size, int id) {
  std::vector<std::vector<Op>> pre, post;
  if (n / block_size != 2 && n / block_size != 4) {
    for (int step = n / 2; step >= block_size; step /= 2) {
      std::vector<Op> layer;
      for (int i = 0; i < n / 2 / step; i++) {
        for (int j = 0; j < step; j++) {
          layer.push_back({i * step * 2 + j, i * step * 2 + j + step, 0});
        }
      }
      pre.push_back(layer);
    }
    for (int step = n / 2; step >= block_size; step /= 2) {
      std::vector<Op> layer;
      for (int i = 0; i < n / 2 / step; i++) {
        for (int j = 0; j < step; j++) {
          layer.push_back({i * step * 2 + j + step, i * step * 2 + j, 0});
        }
      }
      post.push_back(layer);
    }
  } else {
    if (n / block_size == 4) {
      int super_id = id / 1000;
      id = id % 1000;
      if (super_id & 0x2) {
        std::vector<Op> layer;
        for (int j = 0; j < n / 2; j++) {
          layer.push_back({j, j + n / 2, 0});
        }
        pre.push_back(layer);
      } else {
        std::vector<Op> layer;
        for (int j = 0; j < n / 2; j++) {
          layer.push_back({j + n / 2, j, 0});
        }
        pre.push_back(layer);
      }
      if (super_id & 0x1) {
        std::vector<Op> layer;
        for (int j = 0; j < n / 2; j++) {
          layer.push_back({j, j + n / 2, 0});
        }
        post.push_back(layer);
      } else {
        std::vector<Op> layer;
        for (int j = 0; j < n / 2; j++) {
          layer.push_back({j + n / 2, j, 0});
        }
        post.push_back(layer);
      }
    }
    int step = block_size;
    {
      std::vector<Op> layer;
      for (int i = 0; i < n / 2 / step; i++) {
        if (id & (1 << (n / step - 1 - i))) {
          for (int j = 0; j < step; j++) {
            layer.push_back({i * step * 2 + j, i * step * 2 + j + step, 0});
          }
        } else {
          for (int j = 0; j < step; j++) {
            layer.push_back({i * step * 2 + j + step, i * step * 2 + j, 0});
          }
        }
      }
      pre.push_back(layer);
    }
    {
      std::vector<Op> layer;
      for (int i = 0; i < n / 2 / step; i++) {
        if (id & (1 << (n / step / 2 - 1 - i))) {
          for (int j = 0; j < step; j++) {
            layer.push_back({i * step * 2 + j, i * step * 2 + j + step, 0});
          }
        } else {
          for (int j = 0; j < step; j++) {
            layer.push_back({i * step * 2 + j + step, i * step * 2 + j, 0});
          }
        }
      }
      post.push_back(layer);
    }
  }
  return {post, pre};
}

int main(int argc, char *argv[]) {
  if (argc != 3) {
    fprintf(stderr, "Usage: %s raw_result path_to_matrices\n", argv[0]);
    return 1;
  }
  std::ifstream in(argv[1]);
  uint64_t val[64];
  for (int i = 0; i < 64; i++) {
    val[i] = 1ULL << i;
  }
  int n, block_size, id;
  std::string matrix_name;
  Matrix<int> matrix;
  while (true) {
    std::string line;
    std::getline(in, line);
    if (line.empty()) break;
    std::stringstream ss(line);
    if (matrix_name.empty()) {
      std::string tmp;
      ss >> matrix_name;
      std::filesystem::path path = std::string(argv[2]) + matrix_name;
      std::ifstream fs(path);
      matrix = read_matrix(fs);
      n = matrix.size();
      assert(n <= 64);
      ss >> tmp;
      ss >> tmp;
      ss >> tmp;
      sscanf(tmp.c_str(), "(%*d+%d", &block_size);
      if (block_size) {
        block_size = n / block_size;
      } else {
        block_size = n;
      }
      ss >> tmp;
      ss >> tmp;
      sscanf(tmp.c_str(), "id=%d)", &id);
    } else {
      while (true) {
        int x = -1, y = -1;
        ss >> x >> y;
        if (x == -1) break;
        val[y] ^= val[x];
      }
    }
  }
  process_id(matrix, block_size, id);
  uint64_t target[64] = {0};
  for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
      if (matrix[i][j]) {
        target[i] ^= 1ULL << j;
      }
    }
  }
  int perm[64];
  for (int i = 0; i < n; i++) {
    perm[i] = -1;
    for (int j = 0; j < n; j++) {
      if (val[j] == target[i]) {
        perm[i] = j;
        break;
      }
    }
    assert(perm[i] != -1);
    fprintf(stderr, "%d, ", perm[i]);
  }
  fprintf(stderr, "\n");
  auto [pre, post] = id_to_circuit(n, block_size, id);
  for (auto &layer : pre) {
    for (auto &op : layer) {
      op = {op.dst, op.src, 0};
    }
  }
  std::reverse(post.begin(), post.end());
  for (auto &layer : post) {
    for (auto &op : layer) {
      op = {perm[op.src], perm[op.dst], 0};
    }
  }
  for (auto layer : pre) {
    for (auto op : layer) {
      printf("%d %d ", op.src, op.dst);
    }
    printf("\n");
  }
  printf("---\n");
  for (auto layer : post) {
    for (auto op : layer) {
      printf("%d %d ", op.src, op.dst);
    }
    printf("\n");
  }
  return 0;
}
