/* Minimal probSAT (Balint & Schoening 2012), break-only polynomial variant for 3-SAT: cb = 2.06, eps = 0.9.
   Usage: probsat file.cnf [seed] [maxflips]. Prints SAT + time, and checks the assignment. */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <stdint.h>
static uint64_t s; static inline double rnd(void){ s ^= s << 13; s ^= s >> 7; s ^= s << 17; return (s >> 11) * (1.0 / 9007199254740992.0); }
int main(int argc, char **argv){
  FILE *f = fopen(argv[1], "r"); int n, m; char line[4096];
  while (fgets(line, sizeof line, f)) if (line[0] == 'p') { sscanf(line, "p cnf %d %d", &n, &m); break; }
  int (*cl)[3] = malloc(sizeof(int[3]) * m);
  for (int i = 0; i < m; i++){ int z; if (fscanf(f, "%d %d %d %d", &cl[i][0], &cl[i][1], &cl[i][2], &z) != 4) return 2; }
  s = argc > 2 ? strtoull(argv[2], 0, 10) * 0x9E3779B97F4A7C15ULL + 1 : 88172645463325252ULL;
  long maxflips = argc > 3 ? atol(argv[3]) : 2000000000L;
  int *occn = calloc(2 * n + 2, sizeof(int)), **occ = malloc(sizeof(int*) * (2 * n + 2));
  #define IX(l) ((l) > 0 ? 2 * (l) : -2 * (l) + 1)
  for (int i = 0; i < m; i++) for (int j = 0; j < 3; j++) occn[IX(cl[i][j])]++;
  for (int i = 0; i < 2 * n + 2; i++){ occ[i] = malloc(sizeof(int) * (occn[i] + 1)); occn[i] = 0; }
  for (int i = 0; i < m; i++) for (int j = 0; j < 3; j++){ int x = IX(cl[i][j]); occ[x][occn[x]++] = i; }
  char *a = malloc(n + 1); int *nt = calloc(m, sizeof(int)), *un = malloc(sizeof(int) * m), *pos = malloc(sizeof(int) * m), nu = 0;
  int *brk = calloc(n + 1, sizeof(int)), *crit = calloc(m, sizeof(int));
  double pw[64]; for (int i = 0; i < 64; i++) pw[i] = pow(0.9 + i, -2.06);
  struct timespec t0, t1; clock_gettime(CLOCK_MONOTONIC, &t0);
  for (int v = 1; v <= n; v++) a[v] = rnd() < 0.5;
  #define TRUE(l) ((l) > 0 ? a[l] : !a[-(l)])
  for (int i = 0; i < m; i++){ for (int j = 0; j < 3; j++) if (TRUE(cl[i][j])){ nt[i]++; crit[i] ^= abs(cl[i][j]); }
    if (!nt[i]){ pos[i] = nu; un[nu++] = i; } else if (nt[i] == 1) brk[crit[i]]++; }
  long flips = 0;
  while (nu && flips < maxflips){
    int c = un[(int)(rnd() * nu)]; double p[3], tot = 0;
    for (int j = 0; j < 3; j++){ int b = brk[abs(cl[c][j])]; p[j] = pw[b < 63 ? b : 63]; tot += p[j]; }
    double r = rnd() * tot; int j = r < p[0] ? 0 : r < p[0] + p[1] ? 1 : 2; int v = abs(cl[c][j]);
    int tl = a[v] ? v : -v;            /* literal currently true, becomes false */
    a[v] = !a[v]; flips++;
    int x = IX(tl);
    for (int k = 0; k < occn[x]; k++){ int d = occ[x][k]; nt[d]--; crit[d] ^= v;
      if (nt[d] == 0){ pos[d] = nu; un[nu++] = d; brk[v]--; } else if (nt[d] == 1) brk[crit[d]]++; }
    x = IX(-tl);
    for (int k = 0; k < occn[x]; k++){ int d = occ[x][k]; nt[d]++; crit[d] ^= v;
      if (nt[d] == 1){ int q = pos[d]; un[q] = un[--nu]; pos[un[q]] = q; brk[v]++; } else if (nt[d] == 2) brk[crit[d] ^ v]--; }
  }
  clock_gettime(CLOCK_MONOTONIC, &t1);
  double ms = (t1.tv_sec - t0.tv_sec) * 1e3 + (t1.tv_nsec - t0.tv_nsec) / 1e6;
  int ok = 1; for (int i = 0; i < m && ok; i++) ok = TRUE(cl[i][0]) || TRUE(cl[i][1]) || TRUE(cl[i][2]);
  printf("%s %.2f ms %ld flips\n", nu ? "UNKNOWN" : ok ? "SAT(checked)" : "BUG", ms, flips);
  return 0;
}
