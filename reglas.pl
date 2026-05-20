% Declaración de hechos dinámicos para evitar errores si algún archivo está vacío
:- dynamic libro_autor/2.
:- dynamic libro_genero/2.
:- dynamic disponible/1.
:- dynamic le_gusto_genero/2.
:- dynamic le_gusto_autor/2.
:- dynamic ya_leyo/2.

% Cargar los hechos generados por LISP
:- consult('hechos_generados.pl').

% 1. Regla Premium: Match Perfecto (Mismo Autor y Género)
recomendar(Usuario, Libro) :-
    le_gusto_genero(Usuario, Genero),
    le_gusto_autor(Usuario, Autor),
    libro_genero(Libro, Genero),
    libro_autor(Libro, Autor),
    disponible(Libro),
    \+ ya_leyo(Usuario, Libro). % CANDADO: Que no lo haya leído

% 2. Regla Secundaria: Match por Autor
recomendar(Usuario, Libro) :-
    le_gusto_autor(Usuario, Autor),
    libro_autor(Libro, Autor),
    disponible(Libro),
    \+ ya_leyo(Usuario, Libro). % CANDADO: Que no lo haya leído

% 3. Regla Terciaria: Match por Género
recomendar(Usuario, Libro) :-
    le_gusto_genero(Usuario, Genero),
    libro_genero(Libro, Genero),
    disponible(Libro),
    \+ ya_leyo(Usuario, Libro). % CANDADO: Que no lo haya leído