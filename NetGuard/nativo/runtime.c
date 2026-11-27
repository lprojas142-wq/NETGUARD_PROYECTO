/* NetGuard runtime - soporte de entrada/salida para código x86-64 generado.
 * GNU C/Linux: el backend genera .asm Intel que invoca este runtime C.
 * La lógica de condiciones y saltos permanece en instrucciones x86-64 nativas.
 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>
#include <arpa/inet.h>

typedef struct { char ip[64], tipo[96], estado[96]; int64_t puerto, fallos; double trafico; } Evento;
typedef struct { Evento *datos; size_t n, capacidad, actual; } Coleccion;
static size_t total = 0, alertas = 0, marcados = 0;

static char *trim(char *s) {
    while (isspace((unsigned char)*s)) ++s;
    char *f = s + strlen(s);
    while (f > s && isspace((unsigned char)f[-1])) --f;
    *f = '\0';
    return s;
}

void* ng_load(const char *ruta) {
    FILE *f = fopen(ruta, "r");
    if (!f) { fprintf(stderr, "[R01] No se pudo abrir LOG: %s\n", ruta); exit(2); }
    Coleccion *c = calloc(1, sizeof(*c));
    if (!c) exit(3);
    char *linea = NULL; size_t cap = 0; ssize_t nr;
    while ((nr = getline(&linea, &cap, f)) >= 0) {
        (void)nr;
        char *l = trim(linea);
        if (!*l || *l == '#') continue;
        char *campos[7] = {0}, *save = NULL;
        for (int i = 0; i < 7; ++i) {
            campos[i] = strtok_r(i ? NULL : l, ",", &save);
            if (!campos[i]) break;
            campos[i] = trim(campos[i]);
        }
        if (campos[0] && strcmp(campos[0], "sourceIP") == 0) continue;
        if (!campos[5] || campos[6]) continue;
        struct in_addr ip4;
        if (inet_pton(AF_INET, campos[0], &ip4) != 1) continue;
        char *fin1 = NULL, *fin2 = NULL, *fin3 = NULL;
        long long port = strtoll(campos[2], &fin1, 10);
        long long fail = strtoll(campos[3], &fin2, 10);
        double mb = strtod(campos[4], &fin3);
        if (!fin1 || *fin1 || !fin2 || *fin2 || !fin3 || *fin3) continue;
        if (c->n == c->capacidad) {
            c->capacidad = c->capacidad ? c->capacidad * 2 : 32;
            Evento *nuevo = realloc(c->datos, c->capacidad * sizeof(*nuevo));
            if (!nuevo) exit(3);
            c->datos = nuevo;
        }
        Evento *e = &c->datos[c->n++];
        snprintf(e->ip, sizeof(e->ip), "%s", campos[0]);
        snprintf(e->tipo, sizeof(e->tipo), "%s", campos[1]);
        snprintf(e->estado, sizeof(e->estado), "%s", campos[5]);
        e->puerto = port; e->fallos = fail; e->trafico = mb;
    }
    free(linea); fclose(f);
    total += c->n;
    return c;
}

void ng_init(void *p) { ((Coleccion*)p)->actual = 0; }
void* ng_next(void *p) {
    Coleccion *c = p;
    if (c->actual >= c->n) return NULL;
    return &c->datos[c->actual++];
}
int64_t ng_get_int(void *p, int campo) {
    Evento *e = p;
    if (!e) { fprintf(stderr,"[R02] Evento nulo\n"); exit(2); }
    switch (campo) { case 2: return e->puerto; case 3: return e->fallos; default: return 0; }
}
double ng_get_float(void *p, int campo) {
    Evento *e = p;
    if (!e) { fprintf(stderr,"[R02] Evento nulo\n"); exit(2); }
    return campo == 4 ? e->trafico : 0.0;
}
const char* ng_get_text(void *p, int campo) {
    Evento *e = p;
    if (!e) { fprintf(stderr,"[R02] Evento nulo\n"); exit(2); }
    switch (campo) { case 0: return e->ip; case 1: return e->tipo; case 5: return e->estado; default: return ""; }
}
int ng_text_eq(const char *a, const char *b) { return strcmp(a,b) == 0; }
void ng_alert(const char *mensaje, const char *ip) {
    ++alertas;
    printf("[ALERTA]  %s - origen %s\n", mensaje, ip);
}
void ng_mark(void *p, const char *estado) {
    Evento *e = p;
    snprintf(e->estado, sizeof(e->estado), "%s", estado);
    ++marcados;
    printf("[MARCADO] %s -> %s\n", e->ip, e->estado);
}
void ng_summary(void) {
    printf("Eventos analizados: %zu | Alertas: %zu | Marcados: %zu\n", total, alertas, marcados);
}

/* Registros STRUCT de usuario: campos tipados en memoria dinámica. */
typedef struct NGCampo {
    char *nombre;
    uint64_t dato;
    struct NGCampo *siguiente;
} NGCampo;
typedef struct { NGCampo *campos; } NGStruct;

void* ng_struct_new(void) {
    NGStruct *s = calloc(1, sizeof(*s));
    if (!s) exit(3);
    return s;
}
static NGCampo* campo_struct(void *ptr, const char *nombre, int crear) {
    NGStruct *obj = ptr;
    if (!obj) { fprintf(stderr, "[R02] Estructura sin inicializar\n"); exit(2); }
    for (NGCampo *c = obj->campos; c; c = c->siguiente)
        if (strcmp(c->nombre, nombre) == 0) return c;
    if (!crear) return NULL;
    NGCampo *c = calloc(1, sizeof(*c));
    if (!c) exit(3);
    c->nombre = strdup(nombre);
    if (!c->nombre) exit(3);
    c->siguiente = obj->campos;
    obj->campos = c;
    return c;
}
int64_t ng_struct_get_int(void *ptr, const char *nombre) {
    NGCampo *c = campo_struct(ptr, nombre, 0);
    return c ? (int64_t)c->dato : 0;
}
double ng_struct_get_float(void *ptr, const char *nombre) {
    NGCampo *c = campo_struct(ptr, nombre, 0);
    double valor = 0.0;
    if (c) memcpy(&valor, &c->dato, sizeof(valor));
    return valor;
}
const char* ng_struct_get_text(void *ptr, const char *nombre) {
    NGCampo *c = campo_struct(ptr, nombre, 0);
    return (c && c->dato) ? (const char*)(uintptr_t)c->dato : "";
}
void ng_struct_set_int(void *ptr, const char *nombre, int64_t valor) {
    campo_struct(ptr, nombre, 1)->dato = (uint64_t)valor;
}
void ng_struct_set_float(void *ptr, const char *nombre, double valor) {
    uint64_t bits; memcpy(&bits, &valor, sizeof(bits));
    campo_struct(ptr, nombre, 1)->dato = bits;
}
void ng_struct_set_text(void *ptr, const char *nombre, const char *valor) {
    campo_struct(ptr, nombre, 1)->dato = (uint64_t)(uintptr_t)valor;
}

void ng_div_zero(void) { fprintf(stderr,"[R03] División entre cero en código nativo\n"); exit(2); }
