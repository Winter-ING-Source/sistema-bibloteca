;; traductor.lisp
(defun compilar-a-prolog (archivo-entrada archivo-salida)
  ;; Obligamos a LISP a leer y escribir soportando acentos (UTF-8)
  (with-open-file (in archivo-entrada :direction :input :external-format :utf-8)
    (with-open-file (out archivo-salida :direction :output :if-exists :supersede :external-format :utf-8)
      (let ((datos (read in nil)))
        (dolist (registro datos)
          (let ((tipo (car registro)))
            (cond 
              ((eq tipo 'libro)
               (format out "libro_autor('~a', '~a').~%" (cadr registro) (caddr registro))
               (format out "libro_genero('~a', '~a').~%" (cadr registro) (cadddr registro)))
              
              ((eq tipo 'disponible)
               (if (string= (caddr registro) "True")
                   (format out "disponible('~a').~%" (cadr registro))))
              
              ((eq tipo 'le_gusto)
               (format out "le_gusto_genero('~a', '~a').~%" (cadr registro) (caddr registro))
               (format out "le_gusto_autor('~a', '~a').~%" (cadr registro) (cadddr registro))))))))))

(compilar-a-prolog "datos_intermedios.lisp" "hechos_generados.pl")