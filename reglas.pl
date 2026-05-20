% reglas.pl
:- consult('hechos_generados.pl').

% Reglas específicas
recomendar_premium(Usuario, Libro) :-
    le_gusto_genero(Usuario, Genero), le_gusto_autor(Usuario, Autor),
    libro_genero(Libro, Genero), libro_autor(Libro, Autor), disponible(Libro).

recomendar_por_autor(Usuario, Libro) :-
    le_gusto_autor(Usuario, Autor), libro_autor(Libro, Autor), disponible(Libro).

recomendar_por_genero(Usuario, Libro) :-
    le_gusto_genero(Usuario, Genero), libro_genero(Libro, Genero), disponible(Libro).

% REGLA MAESTRA (Esta es la que llama Python)
% El operador ";" significa "O" (OR). Prolog intentará todas estas opciones.
recomendar(Usuario, Libro) :-
    recomendar_premium(Usuario, Libro) ;
    recomendar_por_autor(Usuario, Libro) ;
    recomendar_por_genero(Usuario, Libro).